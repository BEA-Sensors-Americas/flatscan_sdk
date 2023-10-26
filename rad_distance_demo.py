import math
import time
from device_type.rad_distance_device import *
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QBrush, QColor
from PyQt6.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton, QHBoxLayout, QGraphicsView
import pyaudio
import pychord


num_regions = 10
colors = [QColor(000, 200, 100), QColor(255, 165, 0), QColor(255, 0, 0)]
clear_color = [QColor(220, 220, 220)]
# Calculate the angle of each region
angle = (5760 / 360 * 108) / num_regions
note_dict = {0: 196.00,
             1: 220.00,
             2: 246.94,
             3: 261.63,
             4: 293.66,
             5: 329.63,
             6: 349.23,
             7: 392.00,
             8: 440.00,
             9: 493.88
             }

chord_dict={0: "C",
             1: "D",
             2: "E",
             3: "F",
             4: "G",
             5: "A",
             6: "B",
             7: "C",
             8: "D",
             9: "E"
             }


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.p = None
        self.stream = None
        self.button = None
        self.textEdit = None
        self.g = None
        self.duration = None
        self.timer = None
        self.initUI()
        self.device = RadDistance(6, num_zones=num_regions)

    def initUI(self):

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=True)

        # Set the frequency of the sine wave

        # Set the duration of the note in seconds
        self.duration = 1.0
        # Set the size and position of the widget
        self.setWindowTitle('Time Triggered Paint Event')
        self.g = QGraphicsView()
        self.textEdit = QTextEdit()
        self.textEdit.setText("ASDASDSADS")
        self.button = QPushButton("Print Text")

        vbox = QHBoxLayout()
        vbox.addWidget(self.g)

        vbox.addWidget(self.textEdit)

        #self.setLayout(vbox)

        # Set up the timer to trigger every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)  # connect timer to paint event
        self.timer.start(100)  # set timer interval to 1000ms (1 second)

    def paintEvent(self, event):
        # Initialize QPainter
        painter = QPainter(self)
        painter.setPen(Qt.PenStyle.SolidLine)
        painter.setPen(QColor(200, 200, 200))
        self.device.get_zone_info()
        a = self.device.zones
        # Set the number of regions and colors
        # Draw the regions
        play=False
        samples=[]
        chord_samples=[]
        note_to_play=0;
        for i in range(num_regions):
            painter.setBrush(QBrush(clear_color[0]))
            painter.drawPie(0, 200, 900, 900, 600 + int(i * angle), round(angle + 1))
            length = int(300 * (3 - a[i]))
            offset = int(150 * a[i])

            if a[i] == 1:
                note_to_play+=i;
                play=True

                chord_samples.append(chord_dict[i])
                #todo: play chord


            painter.setBrush(QBrush(colors[int(a[i])]))
            painter.drawPie(0 + offset, 200 + offset, length, length, 600 + int(i * angle), round(angle + 1))
        note_to_play=round(note_to_play/num_regions)
        if play:
            samples.append(np.sin(2*np.pi*np.arange(44100*self.duration)*note_dict[note_to_play]/44100.0))
            chord = np.sum(samples, axis=0)

            # Play the chord
            self.stream.write(chord.astype(np.float32))

if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
    widget.resize(900, 900)
    widget.show()
    app.exec()
