#include <Arduino.h>

// 电机控制引脚配置
const int MOTOR_EN_PIN = 2;        // 使能引脚
const int MOTOR_AIN1_PIN = 22;     // 左侧电机控制1
const int MOTOR_AIN2_PIN = 21;     // 左侧电机控制2
const int MOTOR_BIN1_PIN = 15;     // 右侧电机控制1
const int MOTOR_BIN2_PIN = 13;     // 右侧电机控制2

// 串口2配置 (使用GPIO25作为TX，GPIO26作为RX)
#define SERIAL2_RX 25  // 接收引脚
#define SERIAL2_TX 26  // 发送引脚
HardwareSerial SerialPort2(2);     // 使用UART2

// PWM通道配置
const int PWM_FREQ = 1000;         // PWM频率
const int PWM_RESOLUTION = 8;      // 8位分辨率 (0-255)
const int PWM_MAX_DUTY = 255;      // 最大占空比

// PWM通道分配
const int PWM_CH_AIN1 = 0;
const int PWM_CH_AIN2 = 1;
const int PWM_CH_BIN1 = 2;
const int PWM_CH_BIN2 = 3;

// 电机状态
bool motorEnabled = false;

void setup() {
    // 初始化主串口 (与电脑通信)
    Serial.begin(115200);
    
    // 初始化第二个串口 (与设备通信)
    SerialPort2.begin(115200, SERIAL_8N1, SERIAL2_RX, SERIAL2_TX);
    
    // 初始化电机使能引脚
    pinMode(MOTOR_EN_PIN, OUTPUT);
    digitalWrite(MOTOR_EN_PIN, LOW);
    
    // 配置PWM通道
    ledcSetup(PWM_CH_AIN1, PWM_FREQ, PWM_RESOLUTION);
    ledcSetup(PWM_CH_AIN2, PWM_FREQ, PWM_RESOLUTION);
    ledcSetup(PWM_CH_BIN1, PWM_FREQ, PWM_RESOLUTION);
    ledcSetup(PWM_CH_BIN2, PWM_FREQ, PWM_RESOLUTION);
    
    // 连接PWM通道到GPIO引脚
    ledcAttachPin(MOTOR_AIN1_PIN, PWM_CH_AIN1);
    ledcAttachPin(MOTOR_AIN2_PIN, PWM_CH_AIN2);
    ledcAttachPin(MOTOR_BIN1_PIN, PWM_CH_BIN1);
    ledcAttachPin(MOTOR_BIN2_PIN, PWM_CH_BIN2);
    
    // 初始化为0占空比
    ledcWrite(PWM_CH_AIN1, 0);
    ledcWrite(PWM_CH_AIN2, 0);
    ledcWrite(PWM_CH_BIN1, 0);
    ledcWrite(PWM_CH_BIN2, 0);
    
    Serial.println("ESP32 Motor Controller Ready");
    Serial.println("Supported commands:");
    Serial.println("AT+SGPIO=pin,value");
    Serial.println("AT+DRVPWMDUTY=ain1,ain2,bin1,bin2");
    
    SerialPort2.println("ESP32 Motor Ready");
}

// 设置电机使能状态
void setMotorEnable(bool enable) {
    digitalWrite(MOTOR_EN_PIN, enable ? HIGH : LOW);
    motorEnabled = enable;
    
    // 禁用时停止所有PWM
    if (!enable) {
        ledcWrite(PWM_CH_AIN1, 0);
        ledcWrite(PWM_CH_AIN2, 0);
        ledcWrite(PWM_CH_BIN1, 0);
        ledcWrite(PWM_CH_BIN2, 0);
        Serial.println("Motors disabled");
        SerialPort2.println("Motors disabled");
    } else {
        Serial.println("Motors enabled");
        SerialPort2.println("Motors enabled");
    }
}

// 设置PWM占空比
void setMotorPWM(int ain1, int ain2, int bin1, int bin2) {
    if (!motorEnabled) {
        Serial.println("ERROR: Motors not enabled");
        SerialPort2.println("ERROR: Motors not enabled");
        return;
    }
    
    // 限制占空比在0-255范围内
    ain1 = constrain(ain1, 0, PWM_MAX_DUTY);
    ain2 = constrain(ain2, 0, PWM_MAX_DUTY);
    bin1 = constrain(bin1, 0, PWM_MAX_DUTY);
    bin2 = constrain(bin2, 0, PWM_MAX_DUTY);
    
    // 设置PWM值
    ledcWrite(PWM_CH_AIN1, ain1);
    ledcWrite(PWM_CH_AIN2, ain2);
    ledcWrite(PWM_CH_BIN1, bin1);
    ledcWrite(PWM_CH_BIN2, bin2);
    
    Serial.print("Set PWM: ");
    Serial.print("AIN1="); Serial.print(ain1);
    Serial.print(", AIN2="); Serial.print(ain2);
    Serial.print(", BIN1="); Serial.print(bin1);
    Serial.print(", BIN2="); Serial.println(bin2);
    
    SerialPort2.print("Set PWM: ");
    SerialPort2.print("AIN1="); SerialPort2.print(ain1);
    SerialPort2.print(", AIN2="); SerialPort2.print(ain2);
    SerialPort2.print(", BIN1="); SerialPort2.print(bin1);
    SerialPort2.print(", BIN2="); SerialPort2.println(bin2);
    
    Serial.println("OK");
    SerialPort2.println("OK");
}

// 解析并处理命令 (从任意串口)
void processCommand(String cmd, Stream &source) {
    cmd.trim(); // 去除首尾空白
    
    if (cmd.startsWith("AT+SGPIO")) {
        // 格式: AT+SGPIO=pin,value
        int equalsPos = cmd.indexOf('=');
        int commaPos = cmd.indexOf(',');
        
        if (equalsPos != -1 && commaPos != -1) {
            int pin = cmd.substring(equalsPos + 1, commaPos).toInt();
            int value = cmd.substring(commaPos + 1).toInt();
            
            if (pin == MOTOR_EN_PIN) {
                setMotorEnable(value == 1);
                source.println("OK");
            } else {
                source.println("ERROR: Invalid pin");
            }
        } else {
            source.println("ERROR: Invalid command format");
        }
    }
    else if (cmd.startsWith("AT+DRVPWMDUTY")) {
        // 格式: AT+DRVPWMDUTY=ain1,ain2,bin1,bin2
        int equalsPos = cmd.indexOf('=');
        if (equalsPos == -1) {
            source.println("ERROR: Missing =");
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
            source.println("OK");
        } else {
            source.println("ERROR: Need 4 values");
        }
    }
    else {
        source.println("ERROR: Unknown command");
    }
}

void loop() {
    // 处理主串口命令 (电脑)
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        Serial.print("Received: ");
        Serial.println(command);
        processCommand(command, Serial);
    }
    
    // 处理第二个串口命令 (设备)
    if (SerialPort2.available()) {
        String command = SerialPort2.readStringUntil('\n');
        Serial.print("From Device: ");
        Serial.println(command);  // 转发到主串口
        processCommand(command, SerialPort2);
    }
    
    // 这里可以添加其他任务
    delay(10);
}