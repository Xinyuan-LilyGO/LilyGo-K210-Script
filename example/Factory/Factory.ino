#include <Arduino.h>

// ======== 引脚配置 ========
const int MOTOR_EN_PIN = 2;
const int MOTOR_AIN1_PIN = 22;
const int MOTOR_AIN2_PIN = 21;
const int MOTOR_BIN1_PIN = 15;
const int MOTOR_BIN2_PIN = 13;
#define SERVO_PIN 19
#define SERIAL2_RX 25
#define SERIAL2_TX 26

// ======== 舵机配置 ========
#define SERVO_PWM_FREQ 50
#define SERVO_PWM_CHANNEL 4
#define SERVO_PWM_RESOLUTION 16
const int SERVO_MIN_ANGLE = 90;
const int SERVO_MAX_ANGLE = 160;
int servoCurrentAngle = 90;

// ======== PWM配置 ========
const int MOTOR_PWM_FREQ = 1000;
const int MOTOR_PWM_RESOLUTION = 8;
const int PWM_MAX_DUTY = 255;
const int PWM_CH_AIN1 = 0;
const int PWM_CH_AIN2 = 1;
const int PWM_CH_BIN1 = 2;
const int PWM_CH_BIN2 = 3;

// ======== 全局状态 ========
bool motorEnabled = false;
bool servoScanning = false;
int servoDirection = 1; // 1: 向上, -1: 向下
unsigned long lastServoMoveTime = 0;
const long servoMoveInterval = 40; // 舵机移动间隔(ms)
const int servoStep = 1; // 每次移动的角度
bool faceDetected = false;
unsigned long faceDetectedTime = 0; // 添加人脸检测时间戳
const long faceDetectionCooldown = 3000; // 人脸检测后的冷却时间(ms)

// 动作序列状态
enum ActionState {
    ACTION_IDLE,
    ACTION_PREPARE,      // 准备阶段：将舵机抬到最大角度
    ACTION_BACKWARD,     // 后退
    ACTION_SWEEP1,       // 第一次扫描
    ACTION_FORWARD,      // 前进
    ACTION_SWEEP2,       // 第二次扫描
    ACTION_LEFT,         // 左转
    ACTION_SWEEP3,       // 第三次扫描
    ACTION_RIGHT,        // 右转
    ACTION_SWEEP4        // 第四次扫描
};

ActionState currentAction = ACTION_IDLE;
unsigned long actionStartTime = 0;
const long backwardDuration = 2000;  // 后退持续时间(ms)
const long forwardDuration = 2000;   // 前进持续时间(ms)
const long turnDuration = 2000;      // 转向持续时间(ms)
const long prepareDuration = 3000;   // 准备阶段持续时间(ms)

HardwareSerial SerialPort2(2);

// ======== 舵机控制函数 ========
uint32_t angleToDuty(int angle) {
    angle = constrain(angle, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE);
    float pulseWidth = 0.5 + (angle / 180.0) * 2.0;
    float dutyCycle = (pulseWidth / 20.0) * 100.0;
    return (uint32_t)(dutyCycle * (1 << SERVO_PWM_RESOLUTION) / 100);
}

void setServoAngle(int angle) {
    angle = constrain(angle, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE);
    ledcWrite(SERVO_PWM_CHANNEL, angleToDuty(angle));
    servoCurrentAngle = angle;
    Serial.printf("Servo: %d°\n", angle);
}

void startServoScan(bool start) {
    servoScanning = start;
    if (!start) {
        // 停止扫描时重置所有状态
        setMotorPWM(0, 0, 0, 0); // 停止电机
        Serial.println("Servo scanning STOPPED");
    } else {
        // 开始扫描时重置状态
        servoDirection = 1; // 重置方向
        // 设置初始角度为最小角度，确保扫描从底部开始
        setServoAngle(SERVO_MIN_ANGLE);
        Serial.println("Servo scanning STARTED");
    }
}

// 单次上下扫描函数
void performSingleSweep() {
    if (faceDetected) return; // 如果检测到人脸，立即停止扫描
    
    Serial.println("Performing single sweep");
    
    // 从当前角度向下扫描到最小角度（如果不在最小角度）
    if (servoCurrentAngle > SERVO_MIN_ANGLE) {
        for (int angle = servoCurrentAngle; angle >= SERVO_MIN_ANGLE; angle--) {
            if (faceDetected) break; // 如果检测到人脸，立即停止扫描
            setServoAngle(angle);
            delay(servoMoveInterval);
        }
    }
    
    // 从最小角度向上扫描到最大角度
    for (int angle = SERVO_MIN_ANGLE; angle <= SERVO_MAX_ANGLE; angle++) {
        if (faceDetected) break; // 如果检测到人脸，立即停止扫描
        setServoAngle(angle);
        delay(servoMoveInterval);
    }
    
    // // 从最大角度向下扫描到最小角度
    // for (int angle = SERVO_MAX_ANGLE; angle >= SERVO_MIN_ANGLE; angle--) {
    //     if (faceDetected) break; // 如果检测到人脸，立即停止扫描
    //     setServoAngle(angle);
    //     delay(servoMoveInterval);
    // }
    
    Serial.println("Single sweep completed");
}

void updateServoPosition() {
    if (!servoScanning || faceDetected) return;
    
    unsigned long currentTime = millis();
    if (currentTime - lastServoMoveTime < servoMoveInterval) return;
    
    lastServoMoveTime = currentTime;
    
    int newAngle = servoCurrentAngle + (servoDirection * servoStep);
    
    // 检查边界并改变方向
    if (newAngle >= SERVO_MAX_ANGLE) {
        newAngle = SERVO_MAX_ANGLE;
        servoDirection = -1; // 改变方向向下
        Serial.println("Servo direction: DOWN");
    } else if (newAngle <= SERVO_MIN_ANGLE) {
        newAngle = SERVO_MIN_ANGLE;
        servoDirection = 1; // 改变方向向上
        Serial.println("Servo direction: UP");
    }
    
    setServoAngle(newAngle);
}

// ======== 动作序列控制函数 ========
void startActionSequence() {
    currentAction = ACTION_PREPARE;
    actionStartTime = millis();
    // 停止常规扫描
    startServoScan(false);
    Serial.println("Starting action sequence: PREPARE");
}

void updateActionSequence() {
    if (currentAction == ACTION_IDLE || faceDetected) return;
    
    unsigned long elapsedTime = millis() - actionStartTime;
    
    switch (currentAction) {
        case ACTION_PREPARE:
            // 将舵机抬到最大角度
            if (servoCurrentAngle < SERVO_MAX_ANGLE) {
                setServoAngle(servoCurrentAngle + 1);
            } else if (elapsedTime >= prepareDuration) {
                currentAction = ACTION_BACKWARD;
                actionStartTime = millis();
                Serial.println("Action: BACKWARD");
                setMotorPWM(100, 0, 0, 100); // 后退
            }
            break;
            
        case ACTION_BACKWARD:
            if (elapsedTime >= backwardDuration) {
                setMotorPWM(0, 0, 0, 0); // 停止电机
                currentAction = ACTION_SWEEP1;
                actionStartTime = millis();
                Serial.println("Backward complete, starting sweep 1");
            }
            break;
            
        case ACTION_SWEEP1:
            performSingleSweep();
            if (faceDetected) {
                currentAction = ACTION_IDLE;
                break;
            }
            currentAction = ACTION_FORWARD;
            actionStartTime = millis();
            Serial.println("Sweep 1 complete, starting FORWARD");
            setMotorPWM(0, 100, 100, 0); // 前进
            break;
            
        case ACTION_FORWARD:
            if (elapsedTime >= forwardDuration) {
                setMotorPWM(0, 0, 0, 0); // 停止电机
                currentAction = ACTION_SWEEP2;
                actionStartTime = millis();
                Serial.println("Forward complete, starting sweep 2");
            }
            break;
            
        case ACTION_SWEEP2:
            performSingleSweep();
            if (faceDetected) {
                currentAction = ACTION_IDLE;
                break;
            }
            currentAction = ACTION_LEFT;
            actionStartTime = millis();
            Serial.println("Sweep 2 complete, starting LEFT");
            setMotorPWM(0, 0, 100, 0); // 左转
            break;
            
        case ACTION_LEFT:
            if (elapsedTime >= turnDuration) {
                setMotorPWM(0, 0, 0, 0); // 停止电机
                currentAction = ACTION_SWEEP3;
                actionStartTime = millis();
                Serial.println("Left turn complete, starting sweep 3");
            }
            break;
            
        case ACTION_SWEEP3:
            performSingleSweep();
            if (faceDetected) {
                currentAction = ACTION_IDLE;
                break;
            }
            currentAction = ACTION_RIGHT;
            actionStartTime = millis();
            Serial.println("Sweep 3 complete, starting RIGHT");
            setMotorPWM(0, 100, 0, 0); // 右转
            break;
            
        case ACTION_RIGHT:
            if (elapsedTime >= turnDuration) {
                setMotorPWM(0, 0, 0, 0); // 停止电机
                currentAction = ACTION_SWEEP4;
                actionStartTime = millis();
                Serial.println("Right turn complete, starting sweep 4");
            }
            break;
            
        case ACTION_SWEEP4:
            performSingleSweep();
            if (faceDetected) {
                currentAction = ACTION_IDLE;
                break;
            }
            // 完成一个完整周期，重新开始
            currentAction = ACTION_BACKWARD;
            actionStartTime = millis();
            Serial.println("Sweep 4 complete, restarting sequence");
            setMotorPWM(100, 0, 0, 100); // 后退
            break;
            
        default:
            break;
    }
}

// ======== 电机控制函数 ========
void setMotorEnable(bool enable) {
    digitalWrite(MOTOR_EN_PIN, enable ? HIGH : LOW);
    motorEnabled = enable;
    
    if (!enable) {
        ledcWrite(PWM_CH_AIN1, 0);
        ledcWrite(PWM_CH_AIN2, 0);
        ledcWrite(PWM_CH_BIN1, 0);
        ledcWrite(PWM_CH_BIN2, 0);
        Serial.println("Motors disabled");
    } else {
        Serial.println("Motors enabled");
    }
}

void setMotorPWM(int ain1, int ain2, int bin1, int bin2) {
    if (!motorEnabled) {
        Serial.println("ERROR: Motors not enabled");
        return;
    }
    
    ain1 = constrain(ain1, 0, PWM_MAX_DUTY);
    ain2 = constrain(ain2, 0, PWM_MAX_DUTY);
    bin1 = constrain(bin1, 0, PWM_MAX_DUTY);
    bin2 = constrain(bin2, 0, PWM_MAX_DUTY);
    
    ledcWrite(PWM_CH_AIN1, ain1);
    ledcWrite(PWM_CH_AIN2, ain2);
    ledcWrite(PWM_CH_BIN1, bin1);
    ledcWrite(PWM_CH_BIN2, bin2);
    
    Serial.printf("PWM: AIN1=%d, AIN2=%d, BIN1=%d, BIN2=%d\n", ain1, ain2, bin1, bin2);
}

void setFaceDetected(bool detected) {
    if (detected) {
        faceDetected = true;
        faceDetectedTime = millis(); // 记录检测到人脸的时间
        Serial.println("Face detected!");
        // 检测到人脸时停止所有动作
        startServoScan(false);
        currentAction = ACTION_IDLE;
        setMotorPWM(0, 0, 0, 0); // 停止电机
    } else {
        // 只有当冷却时间过后才重置人脸检测标志
        if (millis() - faceDetectedTime > faceDetectionCooldown) {
            faceDetected = false;
            Serial.println("Face lost");
        }
    }
}

// ======== 命令处理 ========
void processCommand(String cmd) {
    cmd.trim();
    
    if (cmd.startsWith("AT+SGPIO")) {
        int equalsPos = cmd.indexOf('=');
        int commaPos = cmd.indexOf(',');
        
        if (equalsPos != -1 && commaPos != -1) {
            int pin = cmd.substring(equalsPos + 1, commaPos).toInt();
            int value = cmd.substring(commaPos + 1).toInt();
            
            if (pin == MOTOR_EN_PIN) {
                setMotorEnable(value == 1);
                Serial.println("OK");
            } else {
                Serial.println("ERROR: Invalid pin");
            }
        }
    }
    else if (cmd.startsWith("AT+DRVPWMDUTY")) {
        // 格式: AT+DRVPWMDUTY=ain1,ain2,bin1,bin2
        int equalsPos = cmd.indexOf('=');
        if (equalsPos == -1) {
            Serial.println("ERROR: Missing =");
            return;
        }
        
        String params = cmd.substring(equalsPos + 1);
        int values[4];
        int lastIndex = 0;
        int valueCount = 0;
        
        // 解析逗号分隔的值
        for (int i = 0; i <= params.length(); i++) {
            if (i == params.length() || params[i] == ',') {
                values[valueCount] = params.substring(lastIndex, i).toInt();
                lastIndex = i + 1;
                valueCount++;
                
                if (valueCount >= 4) break;
            }
        }
        
        if (valueCount == 4) {
            setMotorPWM(values[0], values[1], values[2], values[3]);
            Serial.println("OK");
        } else {
            Serial.println("ERROR: Need 4 values");
        }
    }
    else if (cmd.startsWith("AT+SERVO=")) {
        int equalsPos = cmd.indexOf('=');
        if (equalsPos != -1) {
            int angle = cmd.substring(equalsPos + 1).toInt();
            // 停止所有动作并设置到指定角度
            startServoScan(false);
            currentAction = ACTION_IDLE;
            setServoAngle(angle);
            Serial.println("OK");
        }
    }
    else if (cmd.startsWith("AT+SCAN=")) {
        int equalsPos = cmd.indexOf('=');
        if (equalsPos != -1) {
            int mode = cmd.substring(equalsPos + 1).toInt();
            if (mode == 1) {
                // 启动动作序列（包含扫描和移动）
                startActionSequence();
                Serial.println("OK: Action sequence started");
            } else {
                // 停止所有动作
                startServoScan(false);
                currentAction = ACTION_IDLE;
                Serial.println("OK: All actions stopped");
            }
        }
    }
    else if (cmd.startsWith("AT+FACE=")) {
        int equalsPos = cmd.indexOf('=');
        if (equalsPos != -1) {
            int detected = cmd.substring(equalsPos + 1).toInt();
            setFaceDetected(detected == 1);
            Serial.println("OK");
        }
    }
    else if (cmd.equals("AT+STATUS")) {
        Serial.printf("Status: FaceDetected=%d, ServoScanning=%d, ServoAngle=%d, ActionState=%d\n", 
                    faceDetected, servoScanning, servoCurrentAngle, currentAction);
    }
    else {
        Serial.println("ERROR: Unknown command");
    }
}

// ======== 主程序 ========
void setup() {
    Serial.begin(115200);
    SerialPort2.begin(115200, SERIAL_8N1, SERIAL2_RX, SERIAL2_TX);
    
    pinMode(MOTOR_EN_PIN, OUTPUT);
    digitalWrite(MOTOR_EN_PIN, LOW);
    
    // 配置电机PWM通道
    ledcSetup(PWM_CH_AIN1, MOTOR_PWM_FREQ, MOTOR_PWM_RESOLUTION);
    ledcSetup(PWM_CH_AIN2, MOTOR_PWM_FREQ, MOTOR_PWM_RESOLUTION);
    ledcSetup(PWM_CH_BIN1, MOTOR_PWM_FREQ, MOTOR_PWM_RESOLUTION);
    ledcSetup(PWM_CH_BIN2, MOTOR_PWM_FREQ, MOTOR_PWM_RESOLUTION);
    
    ledcAttachPin(MOTOR_AIN1_PIN, PWM_CH_AIN1);
    ledcAttachPin(MOTOR_AIN2_PIN, PWM_CH_AIN2);
    ledcAttachPin(MOTOR_BIN1_PIN, PWM_CH_BIN1);
    ledcAttachPin(MOTOR_BIN2_PIN, PWM_CH_BIN2);
    
    ledcWrite(PWM_CH_AIN1, 0);
    ledcWrite(PWM_CH_AIN2, 0);
    ledcWrite(PWM_CH_BIN1, 0);
    ledcWrite(PWM_CH_BIN2, 0);
    
    // 配置舵机PWM通道
    ledcSetup(SERVO_PWM_CHANNEL, SERVO_PWM_FREQ, SERVO_PWM_RESOLUTION);
    ledcAttachPin(SERVO_PIN, SERVO_PWM_CHANNEL);
    setServoAngle(SERVO_MIN_ANGLE);
    
    Serial.println("System initialized");
    Serial.println("Commands: AT+SGPIO=pin,value | AT+DRVPWMDUTY=ain1,ain2,bin1,bin2 | AT+SERVO=angle | AT+SCAN=mode | AT+FACE=detected | AT+STATUS");
}

void loop() {
    // 处理串口命令
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        processCommand(command);
    }
    
    // 处理第二个串口命令 (来自K210)
    if (SerialPort2.available()) {
        String command = SerialPort2.readStringUntil('\n');
        Serial.print("From K210: ");
        Serial.println(command);
        processCommand(command);
    }
    
    // 更新舵机位置（如果正在扫描）
    updateServoPosition();
    
    // 更新动作序列
    updateActionSequence();
    
    // 添加一个小延迟以减少CPU使用率
    delay(10);
}