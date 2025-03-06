/**
 * TLV493D Magnetometer Reader
 * 
 * This sketch reads magnetic field data from the Adafruit TLV493D Triple-Axis Magnetometer
 * and outputs the values over serial in a format that can be visualized by the companion
 * Python script.
 * 
 * Connections:
 * - Connect VCC to Arduino 5V (or 3.3V for 3.3V boards)
 * - Connect GND to Arduino GND
 * - Connect SCL to Arduino SCL
 * - Connect SDA to Arduino SDA
 */

#include "TLx493D_inc.hpp"

using namespace ifx::tlx493d;

// Create sensor object - using default I2C address
TLx493D_A1B6 sensor(Wire, 0x5e);

// Variables to store sensor readings
double temperature, x, y, z;
double fieldStrength;

void setup() {
  Serial.begin(115200);
  delay(3000);
  
  if (!sensor.begin()) {
    Serial.println("Failed to initialize TLV493D sensor!");
    while (1); // Halt execution
  } else {
    Serial.println("TLV493D sensor initialized successfully");
  }
  
  Serial.println("TLV493D Magnetometer Test");
  Serial.println("-------------------------");
  Serial.println("Format: x,y,z,strength,temperature");
}

void loop() {
  // Read magnetic field values (in mT) and temperature
  sensor.getMagneticFieldAndTemperature(&x, &y, &z, &temperature);
  
  // Calculate field strength (magnitude of the vector)
  fieldStrength = sqrt(x*x + y*y + z*z);
  
  // Debug output
  Serial.print("DEBUG - Raw values: X=");
  Serial.print(x);
  Serial.print(", Y=");
  Serial.print(y);
  Serial.print(", Z=");
  Serial.print(z);
  Serial.print(", Temp=");
  Serial.println(temperature);
  
  // Send data in CSV format for easy parsing by visualization script
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.print(",");
  Serial.print(z);
  Serial.print(",");
  Serial.print(fieldStrength);
  Serial.print(",");
  Serial.println(temperature);
  
  // Delay between readings (adjust as needed)
  delay(100);
} 