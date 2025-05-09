from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon


class CircleButtonBack(QPushButton):
    def __init__(self, asset_manager, parent=None, on_back_pressed=None):
        super().__init__(parent)
        self.setFixedSize(50, 50)
        self.asset_manager = asset_manager

        icon_path = self.asset_manager.load_asset("Assets/Icons/back_icon.png")
        icon = QIcon(icon_path)
        if icon.isNull():
            print(f"Failed to load icon: {icon_path}")
        else:
            self.setIcon(icon)

        icon_size = self.size() * 0.5
        self.setIconSize(icon_size)

        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, 1),
                                stop: 1 rgba(245, 115, 35, 1));
                border-radius: 25px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, .75),
                                stop: 1 rgba(245, 115, 35, .75));
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, .25),
                                stop: 1 rgba(245, 115, 35, .25));
            }
        """)

        if on_back_pressed:
            self.clicked.connect(on_back_pressed)


class CircleButtonInfo(QPushButton):
    def __init__(self, asset_manager, parent=None, on_info_pressed=None):
        super().__init__(parent)
        self.setFixedSize(50, 50)
        self.asset_manager = asset_manager
        
        icon_path = self.asset_manager.load_asset("Assets/Icons/group_icon.png")  # Ensure this points to the correct image path
        icon = QIcon(icon_path)
        print(f"Resolved icon path: {icon_path}")
        if icon.isNull():
            print(f"Failed to load icon: {icon_path}")
        else:
            self.setIcon(icon)
        
        icon_size = self.size() * 0.4  # 40% of button size
        self.setIconSize(icon_size)

        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, 1),
                                stop: 1 rgba(245, 115, 35, 1));
                border-radius: 25px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, .75),
                                stop: 1 rgba(245, 115, 35, .75));
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, .25),
                                stop: 1 rgba(245, 115, 35, .25));
            }
        """)

        if on_info_pressed:
                self.clicked.connect(on_info_pressed)

class CircleButtonHelp(QPushButton):
    def __init__(self, asset_manager, parent=None, on_help_pressed=None):
        super().__init__(parent)
        self.setFixedSize(50, 50)
        self.asset_manager = asset_manager
        
        icon_path = self.asset_manager.load_asset("Assets/Icons/help_icon.png")  # Ensure this points to the correct image path
        icon = QIcon(icon_path)
        print(f"Resolved icon path: {icon_path}")
        if icon.isNull():
            print(f"Failed to load icon: {icon_path}")
        else:
            self.setIcon(icon)
        
        icon_size = self.size() * 0.4  # 40% of button size
        self.setIconSize(icon_size)

        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, 1),
                                stop: 1 rgba(245, 115, 35, 1));
                border-radius: 25px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, .75),
                                stop: 1 rgba(245, 115, 35, .75));
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, .25),
                                stop: 1 rgba(245, 115, 35, .25));
            }
        """)

        if on_help_pressed:
                self.clicked.connect(on_help_pressed)

class CircleButtonNext(QPushButton):
    def __init__(self, asset_manager, parent=None, on_next_pressed=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.asset_manager = asset_manager

        icon_path = self.asset_manager.load_asset("Assets/Icons/next_icon.png")
        icon = QIcon(icon_path)
        if icon.isNull():
            print(f"Failed to load icon: {icon_path}")
        else:
            self.setIcon(icon)

        icon_size = self.size() * 0.4
        self.setIconSize(icon_size)

        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, 1),
                                stop: 1 rgba(245, 115, 35, 1));
                border-radius: 20px;
                color: white;
                font-weight: bold;
                padding-left: 4px;  /* Move icon to the right */
                padding-right: 0px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, .75),
                                stop: 1 rgba(245, 115, 35, .75));
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, .25),
                                stop: 1 rgba(245, 115, 35, .25));
            }
        """)


class CircleButtonPrev(QPushButton):
    def __init__(self, asset_manager, parent=None, on_prev_pressed=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.asset_manager = asset_manager

        icon_path = self.asset_manager.load_asset("Assets/Icons/previous_icon.png")
        icon = QIcon(icon_path)
        if icon.isNull():
            print(f"Failed to load icon: {icon_path}")
        else:
            self.setIcon(icon)

        icon_size = self.size() * 0.4
        self.setIconSize(icon_size)

        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, 1),
                                stop: 1 rgba(245, 115, 35, 1));
                border-radius: 20px;
                color: white;
                font-weight: bold;
                padding-left: 0px;  /* Move icon to the right */
                padding-right: 4px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, .75),
                                stop: 1 rgba(245, 115, 35, .75));
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, .25),
                                stop: 1 rgba(245, 115, 35, .25));
            }
        """)
