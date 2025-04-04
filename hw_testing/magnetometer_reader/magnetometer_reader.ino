/**
 * TLV493D Magnetometer Reader
 */

#include "TLx493D_inc.hpp"

using namespace ifx::tlx493d;

// using default I2C address
TLx493D_A1B6 sensor(Wire, TLx493D_IIC_ADDR_A0_e);

double temperature, x, y, z;
double fieldStrength;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  delay(3000);
  
  // initialize
  sensor.begin();
  Serial.println("Connected to TLV493D");
}

void loop() {
  // Read magnetic field values (in mT) and temperature
  sensor.getMagneticFieldAndTemperature(&x, &y, &z, &temperature);
  
  // Calculate field strength (magnitude of the vector)
  fieldStrength = sqrt(x*x + y*y + z*z);
  
  // Send data via CSV
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.print(",");
  Serial.print(z);
  Serial.print(",");
  Serial.print(fieldStrength);
  Serial.print(",");
  Serial.println(temperature);
  
  // Delay between readings
  delay(100);
} 