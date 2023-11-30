import sys
import math
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsView
from PyQt6.QtGui import QPainter, QColor, QBrush
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsScene

class PieSlice(QGraphicsItem):
    def __init__(self, start_angle, span_angle, radius, parent=None):
        super().__init__(parent)
        self.start_angle = start_angle
        self.span_angle = span_angle
        self.radius = radius

    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 0, 0, 128)))
        painter.drawPie(self.boundingRect(), self.start_angle, self.span_angle)

class PieChart(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.data = data

        self.setGeometry(100, 100, 600, 600)
        self.view = QGraphicsView(self)
        self.setCentralWidget(self.view)

        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

        self.draw_pie_chart()

    def draw_pie_chart(self):
        total = sum(self.data)
        start_angle = 0

        for value in self.data:
            span_angle = int((value / total) * 360 * 16)  # 16 for scaling
            pie_slice = PieSlice(start_angle, span_angle, 150)
            self.scene.addItem(pie_slice)
            start_angle += span_angle

if __name__ == '__main__':
    app = QApplication(sys.argv)
    data = [30, 60, 90, 120]  # Replace with your data
    window = PieChart(data)
    window.show()
    sys.exit(app.exec())
