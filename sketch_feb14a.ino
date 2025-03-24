#include <PID_v1.h>

const int tempSensorPin = A0;
const int pwmPin = 9;

// PID Variables
double Setpoint = 25.0;  // Default target temperature
double Input, Output;
double Kp = 2.0, Ki = 0.5, Kd = 1.0;  // Tune these values
PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

void setup() {
    Serial.begin(9600);
    pinMode(pwmPin, OUTPUT);
    myPID.SetMode(AUTOMATIC);
    myPID.SetOutputLimits(50, 255);  // Prevent MOSFET from turning off
}

void loop() {
    int sensorValue = analogRead(tempSensorPin);
    float temperature = (sensorValue * 5.0 / 1023.0) * 100.0;  // Convert LM35 voltage to Celsius
    Input = temperature;

    // Read Setpoint from Python (ML model)
    if (Serial.available() > 0) {
        float newSetpoint = Serial.parseFloat();
        if (newSetpoint >= 20.0 && newSetpoint <= 50.0) {  // Safety range
            Setpoint = newSetpoint;
        }
    }

    // Compute PID output
    myPID.Compute();
    int pwmValue = constrain((int)Output, 50, 255);  // Ensure MOSFET never turns off completely
    
    analogWrite(pwmPin, pwmValue);

    // Send Data to Python
    Serial.print(temperature);
    Serial.print(",");
    Serial.println(pwmValue);

    delay(500);
}
