#include <Arduino_BuiltIn.h>
#include <Servo.h>
#include <DS1302.h>
// #include <dht11.h>
// #define DHTPIN 2
// dht11 DHT11;
// 수위 센서 핀이 연결된 아날로그 핀
int waterSensorPin = A0;

const int CLK = 6;
const int DAT = 5;
const int RST = 4;
DS1302 rtc(RST, DAT, CLK); //rtc 연결부

Servo servo;
int pos=0;
const int servoPin=7; //서보모터 연결부

int waterSensorValue = 0;

int feedCycle = 30;
long currentFeed = 0;
const int lowWater=5;
bool forbidFeed = false;  //일반변수
long globalunix = 0;
bool waitcycle = false;
String receivedData;
void feeding()
{
  for (pos = 0; pos < 30; pos += 1)    // 위에 변수를 선언한 pos는 0, 180도보다 작다면 , 1도씩 더하고
  {
  servo.write(pos);                            // 서보모터를 pos 각도로 움직여라
  delay(50);                                         // 0.1초의 딜레이 ( 1초 = 1000 )
  }
  for (pos = 30; pos > 0; pos -= 1)    // 위에 변수를 선언한 pos는 0, 180도보다 작다면 , 1도씩 더하고
  {
  servo.write(pos);                            // 서보모터를 pos 각도로 움직여라
  delay(50);                                         // 0.1초의 딜레이 ( 1초 = 1000 )
  }
  currentFeed = globalunix;
  Serial.print("cur");
  Serial.println(currentFeed);
}

void setup() {
  Serial.begin(9600);
  // dht.begin();
  pinMode(servoPin, OUTPUT);
  servo.attach(7);
  rtc.halt(false);
  rtc.writeProtect(false);
  // rtc.setDOW(MONDAY);
  rtc.setTime(17, 43, 30);
  // rtc.setDate(13, 4, 2020);
  servo.write(0);
}

void loop() {
  delay(100);

  while (Serial.available() > 0) {
    receivedData = Serial.readStringUntil('\n');  // '\n'이 올 때까지 문자열로 읽음
    if(waitcycle){
      int newCycle = receivedData.toInt();
      feedCycle = newCycle;
      waitcycle = false;
    }
    else{
      if(receivedData=="changecycle"){
        waitcycle = true;
      }
      else if(receivedData=="feed"){
        feeding();
      }
    }
  }

  Time t = rtc.getTime();

  // Unix Time 계산
  long unixtime = 0;
  unixtime += t.sec;
  unixtime += t.min*60;
  unixtime += ((long)t.hour*(3600));
  globalunix = unixtime;
  
  // Serial.println(t.sec);
  // Serial.println(t.min);
  // Serial.println(t.hour);
  // Serial.println(unixtime);
  // Serial.println(globalunix);
  // float humidity = dht.readHumidity();    // 습도 값 읽기
  // float temperature = dht.readTemperature(); // 온도 값 읽기
  // waterSensorValue = analogRead(waterSensorPin); // 수위 센서로부터 아날로그 값을 읽기

  if(unixtime - currentFeed >= feedCycle && !forbidFeed){
    feeding();
    currentFeed = globalunix;
  }
  // Serial.println("tem"+temperature);
  // Serial.println("hum"+humidity);
  // Serial.println("wat"+waterSensorValue);
  // if(waterSensorValue<lowWater)
  // {
  //   forbidFeed = true;
  //   Serial.println("forbidFeeding");
  // }
  // else{
  //   forbidFeed = false; 
  //   Serial.println("allowFeeding");
  // }

  // 짧은 지연
  delay(1000);
}
