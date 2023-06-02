import subprocess
import matplotlib.pyplot as plt
import sys
from matplotlib.animation import FuncAnimation

plt.set_loglevel('error')
fig, ax = plt.subplots()
plt.show(block=False)
plt.pause(0.1)
bg = fig.canvas.copy_from_bbox(fig.bbox)

x, y, length = [], [], 0
(line,) = ax.plot(x, y, animated=True)
fig.canvas.blit(fig.bbox)

fig.canvas.restore_region(bg)

self.thread = run_async(self.loop)
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
        self.
        pyplot.draw()


def update(frame):
    data = sys.stdin.readline()
    
fig.canvas.flush_events()
    

    x.append(frame)
    y.append(np.sin(frame))
    line.set_data(x, y)
    return line,


ani = FuncAnimation(fig, update, frames=np.linspace(0, 2*np.pi, 128))
plt.show()

subprocess.Popen(['C:\Windows\py.exe','f'],stdin=subprocess.PIPE)
