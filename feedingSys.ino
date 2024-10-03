#include <DS1302.h>
#include <dht11.h>
#include <Time.h>
#define DHTPIN 2
dht11 DHT11;
// 수위 센서 핀이 연결된 아날로그 핀
int waterSensorPin = A0;

const int CLK = 5;
const int DAT = 6;
const int RST = 7;
DS1302 myrtc(RST, DAT, CLK);

int waterSensorValue = 0;

int feedCycle = 86400;
time_t currentFeed;
const int lowWater=5;
bool forbidFeed = false;

void feeding()
{
  Serial.println("1");
}

void change_cycle(){
  delay(100);
  feedCycle = (int)Serial.readStringUntil('\n');
}

void setup() {
  Serial.begin(9600);
  dht.begin();

  myrtc.halt(false);
  myrtc.writeProtect(false);
  myrtc.setDOW(MONDAY);
  myrtc.setTime(14, 30, 20);
  myrtc.setDate(13, 4, 2020);

}

void loop() {
  delay(2000);

  Time t = rtc.time();

  // Unix Time 계산
  tmElements_t tm;
  tm.Second = t.sec;
  tm.Minute = t.min;
  tm.Hour = t.hour;
  tm.Day = t.date;
  tm.Month = t.mon;
  tm.Year = t.year - 1970;  // Time elements의 year는 1970 기준을 사용

  time_t unixTime = makeTime(tm);

  if (Serial.available() > 0) {
    receivedData = Serial.readStringUntil('\n');  // '\n'이 올 때까지 문자열로 읽음
    if(receivedData=="changecycle"){
      change_cycle();
    }
    else if(receivedData=="feed"){
      feeding();
    }
  }


  float humidity = dht.readHumidity();    // 습도 값 읽기
  float temperature = dht.readTemperature(); // 온도 값 읽기
  waterSensorValue = analogRead(waterSensorPin); // 수위 센서로부터 아날로그 값을 읽기

  time_t now = unixTime;
  if(now - currentFeed >= feedCycle && !forbidFeed){
    feeding();
    currentFeed = now;
    Serial.println("cur"+currentFeed);
  }
  Serial.println("tem"+temperature);
  Serial.println("hum"+humidity);
  Serial.println("wat"+waterSensorValue);
  if(waterSensorValue<lowWater)
  {
    forbidFeed = true;
    Serial.println("forbidFeeding");
  }
  else{
    forbidFeed = false; 
    Serial.println("allowFeeding");
  }

  // 짧은 지연
  delay(1000);
}
