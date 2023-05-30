#define TRIG 9 //TRIG 핀 설정 (초음파 보내는 핀)
#define ECHO 8 //ECHO 핀 설정 (초음파 받는 핀)
long startAt;
void setup() {
  // 시간 변화를 알아내기 위해서, 시작 시각을 저장합니다
  startAt = millis(); // 나중시간-시작시간 = 경과시간

  Serial.begin(9600);
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
}

// loop 안에 모든 코드를 넣기는 코드 관리가 어려움으로
// 기능마다 함수로 분리를 해줍니다
void getDistance(long *distance) {
  long duration;
  digitalWrite(TRIG, HIGH);
  delay(10);
  digitalWrite(TRIG, LOW);
  duration = pulseIn (ECHO, HIGH); //물체에 반사되어돌아온 초음파의 시간을 변수에 저장합니다.
  *distance = duration * 340 / 20000; //  duration은 왕복시간이고 마이크로세컨드이기 때문에 2000000인데 미터를 센치미터로 바꾸어야 하기 때문에 속도 340*duration/20000
  return;
}

void loop(){

  // 거리 cm 을 구해옵니다
  long distance;
  getDistance(&distance);

  // 경과 시간
  long dt = millis()-startAt;

  Serial.println(String(dt) + "," + distance); // 컴퓨터에 정보를 보냅니다
  delay(100); //0.1초마다 측정합니다
}
