#include <Wire.h>   // I2C 통신을 위한 라이브러리
#include <RTClib.h> // RTC 모듈용 RTCLib 라이브러리
#include "DHT.h"  
RTC_DS3231 rtc; // DS3231 RTC 모듈 객체 생성
// 수위 센서 핀이 연결된 아날로그 핀
int waterSensorPin = A0;

// 센서 데이터를 저장할 변수
int waterSensorValue = 0;

int feedCycle = 86400;
DateTime currentFeed;
const int lowWater=5;
bool forbidFeed = false;

void feeding()
{
  Serial.println("1");
}

void setup() {
  Serial.begin(9600);

  if (!rtc.begin()) {
    Serial.println("RTC 모듈을 찾을 수 없습니다!");
    while (1);
  }

  if (rtc.lostPower()) {
    Serial.println("RTC의 전원이 꺼졌습니다! 시간을 재설정합니다.");
    // 현재 시간을 다시 설정: 연도, 월, 일, 시, 분, 초
    rtc.adjust(DateTime(2024, 9, 26, 14, 0, 0)); 
  }
  currentFeed = rtc.now();
}




void loop() {
  if (Serial.available() > 0) {
    receivedData = Serial.readStringUntil('\n');  // '\n'이 올 때까지 문자열로 읽음
    Serial.print("Received: ");
    Serial.println(receivedData);  // 전송된 문자열 출력
  }
  waterSensorValue = analogRead(waterSensorPin); // 수위 센서로부터 아날로그 값을 읽기
  DateTime now = rtc.now();
  if(now.unixtime() - currentFeed.unixtime() >= feedCycle && !forbidFeed){
    feeding();
    currentFeed = now;
  }
  int a= 1;

  if(waterSensorValue<lowWater)
  {
    forbidFeed = true;
    Serial.println("forbidFeeding");
  }
  else{
    forbidFeed = false; 
    Serial.println("allowFeeding");
  }
  Serial.print("수위 센서 값: ");
  Serial.println(waterSensorValue);

  // 짧은 지연
  delay(1000);
}
