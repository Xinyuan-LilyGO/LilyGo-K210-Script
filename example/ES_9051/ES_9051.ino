#include <Arduino.h>

// 舵机控制配置
#define SERVO_PIN 19            // 信号引脚
#define PWM_FREQ 50             // 舵机PWM频率(标准50Hz)
#define PWM_CHANNEL 0         // LEDC通道(0~15)
#define PWM_RESOLUTION 10 // 分辨率(10位=0~1023)

// 舵机运行参数
const int minAngle = 95;        // 最小角度
const int maxAngle = 160;    // 最大角度
int currentAngle = 90;         // 当前角度

// 角度转占空比计算函数
int angleToDuty(int angle) {
    // 约束角度范围
    angle = constrain(angle, minAngle, maxAngle);
    
    // 脉冲宽度计算：0.5ms(0°) ~ 2.5ms(180°)
    float pulseWidth = 0.5 + (angle / 180.0) * 2.0; // 单位: ms
    float dutyCycle = (pulseWidth / 20.0) * 100.0;    // 占空比(%) 
    
    // 转换为10位分辨率整数值
    return (int)(dutyCycle * (1 << PWM_RESOLUTION) / 100);
}

// 设置舵机角度
void setServoAngle(int angle) {
    angle = constrain(angle, minAngle, maxAngle);
    ledcWrite(PWM_CHANNEL, angleToDuty(angle));
    currentAngle = angle;
    Serial.printf("设置角度: %d°\n", angle);
}

// 平滑移动舵机到指定角度
void moveServoSmoothly(int targetAngle, int duration) {
    // 计算移动方向
    int direction = (targetAngle > currentAngle) ? 1 : -1;
    
    // 计算移动步数（每20ms移动一步）
    int steps = duration / 20;
    if (steps < 1) steps = 1;
    
    // 计算每步移动的角度
    float angleStep = (targetAngle - currentAngle) / (float)steps;
    
    // 逐步移动舵机
    for (int i = 0; i < steps; i++) {
        currentAngle += angleStep;
        ledcWrite(PWM_CHANNEL, angleToDuty(currentAngle));
        delay(20); // 每步间隔20ms
    }
    
    // 确保到达目标角度
    setServoAngle(targetAngle);
}

// 持续转动舵机（正转或反转）
void rotateServoContinuous(bool forward, int duration) {
    unsigned long startTime = millis();
    
    while (millis() - startTime < duration) {
        // 根据方向计算目标角度
        int targetAngle = forward ? maxAngle : minAngle;
        
        // 计算移动方向
        int direction = (targetAngle > currentAngle) ? 1 : -1;
        
        // 每步移动1°（约20ms）
        int newAngle = currentAngle + direction;
        
        // 设置新角度
        setServoAngle(newAngle);
        delay(20); // 每度间隔20ms
    }
}

void setup() {
    // 初始化LEDC PWM
    ledcSetup(PWM_CHANNEL, PWM_FREQ, PWM_RESOLUTION);
    ledcAttachPin(SERVO_PIN, PWM_CHANNEL);
    
    Serial.begin(115200);
    Serial.println("舵机正反转控制已启动");
    delay(2000);    
    // 初始位置设为90°
    setServoAngle(90);
    delay(2000);
}

void loop() {
    Serial.println("=== 开始正转 ===");
    rotateServoContinuous(true, 2000); // 正转2秒
    
    Serial.println("=== 开始反转 ===");
    rotateServoContinuous(false, 2000); // 反转2秒
}   