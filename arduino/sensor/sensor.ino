#include <Adafruit_BMP280.h>
#include <dht.h>
#include <LowPower.h>
#include <SPI.h>
#include "RF24.h"

/* configuration for DHT22 and NRF24L01
The BMP280 must be connected to the I2C interface */
#define DHT22_PIN 3   // DHT22
#define CS_PIN 7  // chip select for NRF24L01
#define CE_PIN 8  // chip enable for NRF24L01
const uint64_t address = 0xF1F2F3F4E1LL;  // address for NRF24L01 (randomly chosen)
int channel = 105;   // randomly chosen channel, above of Wifi range

// create entitis for the sensors and RF24
dht DHT;
Adafruit_BMP280 bmp;
RF24 radio(CS_PIN, CE_PIN);

void setup() {
    // initialize the BMP280
    bmp.begin(0x76);

    // initialize RF24
    radio.begin();
    radio.setDataRate(RF24_250KBPS);  // lower data rate to increase range
    radio.setChannel(channel);
    radio.enableDynamicPayloads();
    radio.openWritingPipe(address);
    
}

void loop() { 
  // read temperature (BMP280) 
  float temperature = bmp.readTemperature();
    
  // read humidity (DHT22)
  uint32_t start = micros();
  int chk = DHT.read22(DHT22_PIN);
  uint32_t stop = micros();
  float humidity = DHT.humidity;

  // read pressure (BMP280)
  float pressure = bmp.readPressure() / 100;  //Pa -> hPa

  // convert floats to one string
  static char temperaturestr[10];
  dtostrf(temperature, 2, 1, temperaturestr);
  static char humiditystr[10];
  dtostrf(humidity, 2, 1, humiditystr);
  static char pressurestr[10];
  dtostrf(pressure, 3, 1, pressurestr);

  static char payload[31];
  sprintf(payload,"%s;%s;%s", temperaturestr, humiditystr, pressurestr);
    
  // write data to NRF24L01 module
  radio.write(payload, sizeof(payload));
  
  // sleep for 10 minutes
  //sleep();
  delay(100);
}

void sleep() {
  for (int i = 0; i < 75; i++) {
    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF); 
  }
}

