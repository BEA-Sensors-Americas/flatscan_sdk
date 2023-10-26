import math
import time
import random
from device_type.rad_distance_device import *
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QBrush, QColor, QFont
from PyQt6.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton, QVBoxLayout, QGraphicsView, QGraphicsScene, \
    QLineEdit, QHBoxLayout



num_regions = 10
green=int("8ac926", 16)
orange=int("ffca3a", 16)
red=int("FF262D", 16)
blue=int("1982c4", 16)
purple=int("6a4c93", 16)

colors = [QColor(green), QColor(orange), QColor(red), QColor(blue),QColor(purple)]
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


class CustomGraphicsView(QGraphicsView):
    def __init__(self,scene, widget):
        super().__init__()
        self.device = RadDistance(6, num_zones=num_regions)
        self.widget=widget
        self.setScene(scene)
        self.timer = QTimer(self)
        self.gameTimer = QTimer(self)
        self.timer.timeout.connect(self.update_paint)  # connect timer to paint event
        self.gameTimer.timeout.connect(self.paint_target)
        self.gameTimer.start(10000)
        self.timer.start(100)  # set timer interval to 1000ms (1 second)
        self.random_number = 0
        self.score=0
        self.font=QFont("Arial", 30)
        self.textItem=self.scene().addText("Current Score:" + str(self.score), self.font)
        self.textItem.setPos(-1000, -1000)
        self.touchTime=101

    def paint_update_score(self):
        self.score += 1
        self.textItem.setPlainText("Current Score:" + str(self.score))
        # Draw text


    def reset_counter(self):
        self.score=0
        self.textItem.setPlainText("Current Score:" + str(self.score))
    def get_device_zones(self):
        self.device.get_zone_info()
        if self.device.zones[self.random_number]>0 and self.touchTime>10:
            self.widget.points+=1
            self.widget.textEdit.setText(str(self.widget.points))
            self.paint_update_score()
            self.paint_target()
            self.touchTime=0
        elif self.device.zones[self.random_number]>0:
            self.device.zones[self.random_number] = 4
            self.touchTime+=1
        else:
            self.device.zones[self.random_number]=3

    def paint_target(self):
        self.random_number = random.randint(0, num_regions-1)
        self.gameTimer.start(10000)


    def update_paint(self):
        self.get_device_zones()
        self.viewport().update()

    def drawBackground(self, painter: QPainter, rect):
        # Call the base implementation to draw the default background
        super().drawBackground(painter, rect)
        rect_w=rect.width()
        rect_h=rect.height()
        ad=(rect_w-rect_h)/2
        adh=rect_h/2-50
        offset=rect_h/5
        pie_rect = rect.adjusted(ad-offset, adh-offset, -ad+offset, adh+offset)
        # Get the current device zones
        a = self.device.zones
        # Custom drawing code
        painter.setPen(Qt.PenStyle.SolidLine)
        painter.setPen(QColor(200, 200, 200))

        # Set the number of regions and colors
        # Draw the regions

        for i in range(num_regions):
            painter.setBrush(QBrush(colors[int(a[i])]))
            painter.drawPie(pie_rect, 600 + int(i * angle), round(angle + 1))




class MyWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.points = 0
        self.p = None
        self.stream = None
        self.button = None
        self.textEdit = None
        self.g = None
        self.duration = None
        self.timer = None
        self.gameTimer = None
        self.initUI()
        self.random_number = 0

    def initUI(self):


        # Set the frequency of the sine wave

        # Set the duration of the note in seconds
        self.duration = 1.0
        # Set the size and position of the widget
        self.setWindowTitle('Time Triggered Paint Event')
        scene = QGraphicsScene(self)
        self.g = CustomGraphicsView(scene,self)
        self.textEdit = QLineEdit(self)
        self.button = QPushButton('Restart', self)
        self.button.clicked.connect(self.g.reset_counter)
        self.textEdit.setText("Current Point: 0")
        hbox=QHBoxLayout()
        hbox.addWidget(self.button)
        hbox.addWidget(self.textEdit)

        vbox = QVBoxLayout()
        self.setLayout(vbox)
        vbox.addWidget(self.g)
        vbox.addLayout(hbox)



        # Set up the timer to trigger every second



    def paintEvent(self, event):
        # Initialize QPainter
        painter = QPainter(self)


if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
    widget.resize(900, 900)
    widget.show()

    app.exec()
