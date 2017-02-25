#include <Wire.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <dht.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP085_U.h>
#include <LowPower.h>
#include <SPI.h>
#include "RF24.h"

/* configuration for DS18B20, DHT22 and NRF24L01
The BMP180 must be connected to the I2C interface */
#define ONE_WIRE_PIN 4  // DS18B20
#define DHT22_PIN 3   // DHT22
#define CS_PIN 7  // chip select for NRF24L01
#define CE_PIN 8  // chip enable for NRF24L01
const uint64_t address = 0xF1F2F3F4E1LL;  // address for NRF24L01 (randomly chosen)

// create entitis for the sensors and the RF24
OneWire oneWire(ONE_WIRE_PIN);
DallasTemperature sensors(&oneWire);
dht DHT;
Adafruit_BMP085_Unified bmp = Adafruit_BMP085_Unified(10085);
RF24 radio(CS_PIN, CE_PIN);

void setup(){
    // initialize the BMP180
    bmp.begin();
    sensor_t sensor;
    bmp.getSensor(&sensor);
    sensors.begin();

    // initialize RF24
    radio.begin();
    radio.enableDynamicPayloads();
    radio.openWritingPipe(address);
}

void loop(){ 
  // read temperature (DS18S20) 
  sensors.requestTemperatures();
  float temperature = sensors.getTempCByIndex(0);
    
  // read humidity (DHT22)
  uint32_t start = micros();
  int chk = DHT.read22(DHT22_PIN);
  uint32_t stop = micros();
  float humidity = DHT.humidity;

  // read pressure (BMP180)
  sensors_event_t event;
  bmp.getEvent(&event);
  float pressure = event.pressure;

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
  sleep();
}

void sleep() {
  for (int i = 0; i < 75; i++) {
    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF); 
  }
}

