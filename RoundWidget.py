from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QLinearGradient

class RoundedWidget(QWidget):
    def __init__(self, radius=20, color1=QColor(0, 0, 0, 50), color2=None, parent=None):
        super().__init__(parent)
        self.radius = radius
        self.color1 = color1
        self.color2 = color2 or color1  # Use solid color if no gradient
        self.setAttribute(Qt.WA_TranslucentBackground)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(self.rect())
        path = QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)

        gradient = QLinearGradient(0, 0, 0, rect.height())  # Vertical gradient (top to bottom)
        gradient.setColorAt(0, self.color1)
        gradient.setColorAt(1, self.color2)

        painter.fillPath(path, gradient)