import serial_asyncio
import asyncio
import threading
import datetime
import pandas
import aioconsole
import sys
import matplotlib.pyplot as pyplot
import matplotlib
import math

# 설정
# 시리얼 포트(윈도우: 디바이스포트명 COM1 COM2 COM3, 리눅스: /dev/ttyS0 ...)
SERIAL_PORT="COM8"

# 보드레이트 bps (Serial.begin 에 넣은만큼 설정)
BAUDRATE=9600

# 윈도우에서 코드를 실행하는 경우 True 로 바꿔주세요
DISABLE_GRAPH=False
DISABLE_AIOCONSOLE=True

# 아두이노 없는 상황에서 테스트를 위한 부분
TEST_MODE=True

# https://stackoverflow.com/questions/55409641/asyncio-run-cannot-be-called-from-a-running-event-loop-when-using-jupyter-no
# 다른 스레드에서 async 함수를 asyncio 로 진행시킵니다
# 이는... 파이썬 언어의 async 구조적 한계(?) 점에 의해 이렇게 더러운것이므로
# 요 부분은 이해하려고 하지 않는게 편합니다
# (async 가 파이썬에서 가장 어려운? 난해한? 부분이라....)
class RunThread(threading.Thread):
    def __init__(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None
        super().__init__()
    def run(self):
        self.result = asyncio.run(self.func(*self.args, **self.kwargs))
def run_async(func, *args, **kwargs):
    thread = RunThread(func, args, kwargs)
    thread.start()
    return thread

# 아두이노에서 데이터를 읽어오는 클래스
# matplotlib 를 위해서 async 로 논블럭으로 작성되어있습니다.
# 자세한 사항은 pyserial asyncio 라이브러리 문서 참조
# : https://pyserial-asyncio.readthedocs.io/en/latest/shortintro.html#protocol-example
class Arduino:
    async def testLoop(self,serial_port,baudrate):
        time=0
        while True:
            await self.callback("{},{}\n".format(int(time),int(math.sin(time/100*3.14)*20)))
            time+=1
            asyncio.sleep(1)
            if self.killed: break
    async def loop(self,serial_port,baudrate):
        self.reader, self.writer = await serial_asyncio.open_serial_connection(url=serial_port, baudrate=baudrate)
        while True:
            if self.killed: break
            if self.reader.at_eof(): continue
            try: await self.callback((await self.reader.readline()).decode("utf-8"))
            except: pass
    def connect(self,serial_port,baudrate):
        self.thread = run_async(self.test and self.testLoop or self.loop,serial_port,baudrate)
    def kill(self):
        self.killed = True
        if self.test: return
        self.thread.join(3)
    def __init__(self,test,callback):
        self.callback = callback
        self.test = test
        self.killed = False

# 그래프를 그립니다
class GraphHandler:
    def __init__(self):
        self.bufferX, self.bufferY, self.length = [],[],0
        self.fig, self.ax = pyplot.subplots()
        pyplot.set_loglevel('error')
        pyplot.show(block=False)
    def animate(self, x, y):
        # 최근 20 초의 기록만 보여줌
        self.bufferX.append(x)
        self.bufferY.append(y)
        self.length += 1
        if self.length > 200:
            self.length -= 1
            del self.bufferX[0]
            del self.bufferY[0]
        self.ax.clear()
        self.ax.set_ylim(0,40)
        self.ax.plot(self.bufferX, self.bufferY)
        pyplot.draw()
        self.fig.canvas.flush_events()

# 엑셀 파일을 작성합니다
class FileHandler:
    # 시간을 기준으로 출력 파일 이름을 생성합니다
    def makeFilename(self):
        now = datetime.datetime.now()
        return "{}월.{}일.{}시.{}분.{}초.xlsx".format(now.month,now.day,now.hour,now.minute,now.second)

    # 템플릿 파일을 template.xlsx 에서 불러옵니다
    def readTemplate(self):
        self.file = pandas.read_excel("./template.xlsx", sheet_name="Result")

    # 결과값을 하나 추가합니다
    def append(self,datas):
        self.file.loc[len(self.file)] = datas

    # 파일을 저장합니다
    def save(self):
        fileName = self.makeFilename()
        with pandas.ExcelWriter(fileName) as w:
            self.file.to_excel(w, sheet_name='Result', index=False)
        return fileName
    def __init__(self):
        self.readTemplate()

# 콘솔에서 값이 입력됨을 감지합니다
class Readline:
    async def loop(self,callback):
        while True:
            if DISABLE_AIOCONSOLE:
                await callback(input(''))
            else:
                await callback(await aioconsole.ainput(''))
    def __init__(self,callback):
        self.killed = False
        run_async(self.loop,callback)

# 메인로직
async def main():
    # 시작 시간을 따로 기록해, 기록이 시작된 시점을 t=0 으로 만들어줍니다
    startAt = False
    skipFirstByte = 0 # 연결전 쓰래기 값을 제거하기 위해 첫번째 20 개의 결과를 스킵합니다
    fileHandler = FileHandler()
    if not DISABLE_GRAPH: graph = GraphHandler()

    # 아두이노에서 읽은 데이터를 , 을 기준으로 나눠줍니다
    # 그런 후, 메모리에 집어넣고 그래프로 표시합니다
    async def arduinoCallback(str:str):
        nonlocal startAt
        nonlocal skipFirstByte

        if skipFirstByte<20:
            skipFirstByte += 1
            return

        # 0 번째 : 시간 (ms)
        # 1 번째 : 거리 cm
        datas = str.removesuffix("\n").split(",")
        if datas.__len__() != 2: return

        # 시작시간 기록
        if startAt == False:
            startAt = int(datas[0])

        # dt 를 구하기 위해 시작시간만큼 빼줌
        datas[0] = (int(datas[0])-startAt)/1000 # ms 를 s 로 변환
        datas[1] = int(datas[1])

        # 메모리 버퍼에 쓰기
        fileHandler.append(datas)

        # 그래프에 그리기, 출력하기
        sys.stdout.write("\033[K\r{},{}".format(datas[0],datas[1]))
        if not DISABLE_GRAPH:
            graph.animate(datas[0],datas[1])

    arduino = Arduino(TEST_MODE,arduinoCallback)

    # 입력이 들어오면 코드를 멈춥니다
    # 메모리에 있던 데이터들을 엑셀로 저장합니다
    async def inputCallback(str:str):
        arduino.kill()
        print("\033[K\r파일 저장중 . . .")
        print("파일이 "+fileHandler.save()+" 에 저장되었습니다")
        print("종료합니다")
        exit(0)

    # 안내 메시지
    print("엔터키를 눌러서 실행을 종료합니다")
    print("matplotlib 창을 통해 그래프를 미리보기 할 수 있습니다")

    # 실행부
    Readline(inputCallback) # 콘솔 읽기 시작
    arduino.connect(SERIAL_PORT,BAUDRATE) # 아두이노 연결 시작

# 메인 루프를 시작합니다
asyncio.run(main())
