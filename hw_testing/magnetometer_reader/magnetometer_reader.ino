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
TLx493D_A1B6 sensor(Wire, TLx493D_IIC_ADDR_A0_e);

// Variables to store sensor readings
double temperature, x, y, z;
double fieldStrength;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  
  // Wait for serial port to connect
  delay(3000);
  
  // Initialize the sensor
  sensor.begin();
  // sensor.setAccessMode(TLx493D_AccessMode_e::FAST_MODE);  // Set to fast mode
  sensor.setUpdateRate(TLx493D_UpdateRateType_t::TLx493D_UPDATE_RATE_1000_HZ_e);
  
  Serial.println("TLV493D Magnetometer Test");
  Serial.println("-------------------------");
  Serial.println("Format: x,y,z,strength,temperature");
}

unsigned long lastReadTime = 0;
const unsigned long READ_INTERVAL = 1100;  // microseconds (1ms = 1kHz sampling)

void loop() {
  unsigned long currentTime = micros();
  
  if (currentTime - lastReadTime >= READ_INTERVAL) {
    lastReadTime = currentTime;
    
    // Read magnetic field values (in mT) and temperature
    sensor.getMagneticFieldAndTemperature(&x, &y, &z, &temperature);
    
    // Calculate field strength (magnitude of the vector)
    fieldStrength = sqrt(x*x + y*y + z*z);
    
    // Debug output
    // Serial.print("DEBUG - Raw values: X=");
    // Serial.print(x);
    // Serial.print(", Y=");
    // Serial.print(y);
    // Serial.print(", Z=");
    // Serial.print(z);
    // Serial.print(", Temp=");
    // Serial.println(temperature);
    
    // Send data in CSV format for easy parsing by visualization script
    Serial.print(currentTime);
    Serial.print(",");
    Serial.print(x);
    Serial.print(",");
    Serial.print(y);
    Serial.print(",");
    Serial.print(z);
    Serial.print(",");
    Serial.print(fieldStrength);
    Serial.print(",");
    Serial.println(temperature);
  }
} 