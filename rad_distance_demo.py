import math
import time
from device_type.rad_distance_device import *
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen
from PyQt6.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton, QHBoxLayout, QGraphicsView, QLineEdit, \
    QVBoxLayout
import pyautogui as pg


num_regions = 8
colors = [QColor(000, 200, 100), QColor(255, 165, 0), QColor(255, 0, 0)]
clear_color = [QColor(220, 220, 220)]
# Calculate the angle of each region
angle = (5760 / 360 * 108) / num_regions

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.line_edit2 = None
        self.line_edit1 = None
        self.p = None
        self.stream = None
        self.button = None
        self.textEdit = None
        self.g = None
        self.duration = None
        self.timer = None
        self.initUI()
        self.device = RadDistance(4, num_zones=num_regions)

    def initUI(self):


        # Set the frequency of the sine wave

        # Set the duration of the note in seconds
        self.duration = 1.0
        # Set the size and position of the widget
        self.setWindowTitle('Time Triggered Paint Event')
        self.g = QGraphicsView()
        self.textEdit = QTextEdit()
        self.textEdit.setText("ASDASDSADS")
        self.button = QPushButton("Print Text")

        vbox = QVBoxLayout()
        vbox.setSpacing(10)
        #vbox.addWidget(self.g)

        #vbox.addWidget(self.textEdit)
        self.line_edit1 = QLineEdit(self)  # Create the first QLineEdit
        self.line_edit1.setPlaceholderText("Enter text 1 here")  # Set a placeholder text
        vbox.addWidget(self.line_edit1)  # Add the first line edit to the layout

        self.line_edit2 = QLineEdit(self)  # Create the second QLineEdit
        self.line_edit2.setPlaceholderText("Enter text 2 here")  # Set a placeholder text
        vbox.addWidget(self.line_edit2)  # Add the second line edit to the layout

        self.button = QPushButton("Print Text")  # Create a button
        vbox.addWidget(self.button)  # Add the button to the layout

        self.button.clicked.connect(self.printText)  # Connect the button's click event to a method

        #self.setLayout(vbox)

        # Set up the timer to trigger every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)  # connect timer to paint event
        self.timer.start(100)  # set timer interval to 1000ms (1 second)

    def printText(self):
        text1 = self.line_edit1.text()  # Get text from the first line edit
        text2 = self.line_edit2.text()  # Get text from the second line edit
        print(f"Text 1: {text1}")
        print(f"Text 2: {text2}")

        # You can use 'text1' and 'text2' as needed in your application.

        # ...
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
        note_to_play=0
        origin = (0, 200)  # Change the coordinates as needed
        play=False
        for i in range(num_regions):
            painter.setBrush(QBrush(clear_color[0]))
            painter.drawPie(0, 200, 900, 900, 600 + int(i * angle), round(angle + 1))
            length = int(300 * (3 - a[i]))
            #end_point = origin + QPointF(math.cos(math.radians(angle)) * length,
                                         #math.sin(math.radians(angle)) * length)
            offset = int(150 * a[i])

            if a[i] == 1:
                note_to_play+=i;


                #todo: play chord


            painter.setBrush(QBrush(colors[int(a[i])]))
            painter.drawPie(0 + offset, 200 + offset, length, length, 600 + int(i * angle), round(angle + 1))

        if not play and note_to_play==2:
            pg.press('space')
            play=True
        if play and note_to_play<1:
            pg.press('space')
            play=False

if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
    widget.resize(900, 900)
    widget.show()
    app.exec()
