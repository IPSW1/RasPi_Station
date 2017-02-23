#include <Wire.h>
#include <SoftwareSerial.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <dht.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP085_U.h>
#include <LowPower.h>

/* Datapins for DS18B20, DHT22 and software serial
The BMP180 must be connected to the I2C interface */
#define ONE_WIRE_PIN 9  //DS18B20
#define DHT22_PIN 6   //DHT22
#define softSer_RX 10   //SoftwareSerial RX
#define softSer_TX 11 //SoftwareSerial TX

//Create entitis for the sensors and the software serial interface
OneWire oneWire(ONE_WIRE_PIN);
DallasTemperature sensors(&oneWire);
dht DHT;
Adafruit_BMP085_Unified bmp = Adafruit_BMP085_Unified(10085);
SoftwareSerial bluetooth(softSer_RX, softSer_TX);


void setup(){
    //Start software serial with 9600 baud
    bluetooth.begin(9600);

    //Initialize the BMP180
    bmp.begin();
    sensor_t sensor;
    bmp.getSensor(&sensor);
    sensors.begin();
}

void loop(){ 
  //Read temperature (DS18S20) 
  sensors.requestTemperatures();
    
  //Read humidity (DHT22)
  uint32_t start = micros();
  int chk = DHT.read22(DHT22_PIN);
  uint32_t stop = micros();

  //Read pressure (BMP180)
  sensors_event_t event;
  bmp.getEvent(&event);
    
  //Write data to the bluetooth module
  bluetooth.print(sensors.getTempCByIndex(0), 1);
  bluetooth.print(";");
  bluetooth.print(DHT.humidity, 1);
  bluetooth.print(";");
  bluetooth.print(event.pressure);
  bluetooth.println();
  
  //Sleep for 10 minutes
  sleep();
}

void sleep() {
  for (int i = 0; i < 75; i++) {
    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF); 
  }
}

