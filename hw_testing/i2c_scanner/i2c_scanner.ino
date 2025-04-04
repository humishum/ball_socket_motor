#include <Wire.h>

void setup() {
  Wire.begin();
  Serial.begin(115200);
  while (!Serial);
  
  Serial.println("I2C Scanner");
  Serial.println("------------");
}

void loop() {
  byte error, address;
  int deviceCount = 0;
  
  Serial.println("Scanning for I2C devices...");
  
  for (address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();
    
    if (error == 0) {
      Serial.print("I2C device found at address 0x");
      if (address < 16) {
        Serial.print("0");
      }
      Serial.print(address, HEX);
      Serial.println();
      
      deviceCount++;
    } else if (error == 4) {
      Serial.print("Unknown error at address 0x");
      if (address < 16) {
        Serial.print("0");
      }
      Serial.println(address, HEX);
    }
  }
  
  if (deviceCount == 0) {
    Serial.println("No I2C devices found!");
    Serial.println("Check your wiring and pull-up resistors.");
  } else {
    Serial.print("Found ");
    Serial.print(deviceCount);
    Serial.println(" device(s).");
  }
  
  // TLV493D expected addresses
  Serial.println("\nTLV493D expected addresses:");
  Serial.println("0x5E (TLx493D_IIC_ADDR_A0_e)");
  Serial.println("0x1F (TLx493D_IIC_ADDR_A1_e)");
  
  delay(5000);  // Wait 5 seconds before scanning again
} 