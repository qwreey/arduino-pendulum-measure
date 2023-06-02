import matplotlib.pyplot as plt
import sys

fig, ax = plt.subplots()
x, y, length = [], [], 0

plt.show(block=False)
(line,) = ax.plot(x, y)

plt.pause(.1)

def append(newX,newY):
    global length, x, y
    x.append(float(newX))
    y.append(float(newY))
    length += 1
    if length > 200:
        length -= 1
        del x[0]
        del y[0]

def updateLine():
    global line, ax
    line.set_data(x, y)
    ax.set_ylim(0,40)
    last = x[len(x)-1]
    ax.set_xlim(last-20,last)
    fig.canvas.draw()
    fig.canvas.flush_events()

updatedCount = 0

while True:
    stdinStr = sys.stdin.readline()
    if stdinStr == "READY\n":
        sys.stdout.write("OK\n")
        sys.stdout.flush()
        continue

    datas = stdinStr.removesuffix("\n").split(",")
    if len(datas) != 2: continue
    append(datas[0],datas[1])
    if updatedCount%2 == 0: updateLine()
    updatedCount += 1
