from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QPainter

class BallWidget(QLabel):
    def __init__(self, number, ball_index, asset_manager, parent=None, size=200, font_size=48):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)
        self.asset_manager = asset_manager

        self.number = number
        self.ball_index = ball_index
        self.pixmap = None
        self.font_size = font_size

        self.setStyleSheet("background-color: rgba(255, 255, 255, 0);")

        self.load_ball_image()

    def get_number(self):
        return self.number  # Return the current number of the ball

    def load_ball_image(self):
        image_path = f"Assets/Icons/lottery_ball_{self.ball_index}.png"
        self.pixmap = self.asset_manager.load_pixmap(image_path)

    def update_number(self, new_number, new_index=None):
        self.number = new_number
        if new_index is not None:
            self.ball_index = new_index
            self.load_ball_image()
        self.update()  # Triggers repaint

    def paintEvent(self, event):
        painter = QPainter(self)

        # Draw ball image if loaded
        if self.pixmap and not self.pixmap.isNull():
            scaled_pixmap = self.pixmap.scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(self.rect(), scaled_pixmap)
        else:
            painter.setBrush(Qt.GlobalColor.darkYellow)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(self.rect())

        # Draw centered number
        custom_color = QColor(25, 25, 75, 255)  # This is a dark blue color with full opacity
        painter.setPen(custom_color)
        painter.setFont(QFont("Roboto Condensed", self.font_size, QFont.Weight.Black))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, str(self.number))

    