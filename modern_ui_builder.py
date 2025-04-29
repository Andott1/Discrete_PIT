import os
import random
import sys
from datetime import datetime
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                            QComboBox, QWidget, QFrame, QDateEdit, QDialog,
                            QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea, QApplication, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QDate, QSize, QTimer
from PyQt6.QtGui import QPixmap, QIcon, QFont, QPalette, QColor, QBrush, QLinearGradient, QPainter

from config import LOTTERY_CONFIG
from ui_utils import populate_table, display_recent_results, add_history, resize_widget_percent

class BallWidget(QLabel):
    def __init__(self, number, ball_index, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 100)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.number = number
        self.ball_index = ball_index
        self.pixmap = None

        self.load_ball_image()

    def load_ball_image(self):
        assets_dir = os.path.join(os.path.dirname(__file__), "Assets")
        ball_path = os.path.join(assets_dir, "Balls", f"ball_{self.ball_index}.png")
        if os.path.exists(ball_path):
            self.pixmap = QPixmap(ball_path)
        else:
            self.pixmap = None

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
        painter.setPen(Qt.GlobalColor.black)
        painter.setFont(QFont("Figtree", 22, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, str(self.number))

class ImageLotteryBall(QLabel):
    """Custom widget for displaying a lottery ball using an image and number"""
    
    def __init__(self, number, ball_index, parent=None):
        super().__init__(parent)
        self.number = number
        self.ball_index = ball_index
        
        self.setFixedSize(100, 100)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Load the ball image
        self.load_ball_image()
    
    def load_ball_image(self):
        assets_dir = os.path.join(os.path.dirname(__file__), "Assets")
        ball_path = os.path.join(assets_dir, "Balls", f"ball_{self.ball_index}.png")
        print(f"Looking for image at: {ball_path}")
        print(f"File exists: {os.path.exists(ball_path)}")
        
        if os.path.exists(ball_path):
            self.pixmap = QPixmap(ball_path)
        else:
            self.pixmap = None

    def paintEvent(self, event):
        painter = QPainter(self)

        # Draw the ball image
        if self.pixmap and not self.pixmap.isNull():
            scaled_pixmap = self.pixmap.scaled(
                self.width(), 
                self.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(self.rect(), scaled_pixmap)
        else:
            painter.setBrush(Qt.GlobalColor.darkYellow)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(self.rect())
        
        # Draw the number text
        painter.setPen(Qt.GlobalColor.black)
        painter.setFont(QFont("figtree", 24, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, str(self.number))

class GroupInfoDialog(QDialog):
    """Dialog for displaying group information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Group Information")
        self.setFixedSize(400, 300)
        
        # Set up the layout
        layout = QVBoxLayout()
        
        # Add a title
        title = QLabel("Group Members")
        title.setFont(QFont("Figtree", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Add group members
        members = [
            "Kurt Andre Olaer",
            "James Dominic Tion",
            "Mariel Laplap",
            "Jeff Justin Bonior",
            "Gwynette Galleros"
        ]
        
        for member in members:
            label = QLabel(member)
            label.setFont(QFont("Figtree", 12))
            layout.addWidget(label)
        
        # Add a close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)

class ResultsDialog(QDialog):
    """Dialog for displaying lottery results"""
    
    def __init__(self, title, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        
        # Get the parent size and use it for this dialog
        if parent:
            self.setFixedSize(parent.size())
        else:
            self.setFixedSize(800, 600)
        
        # Set up the layout
        layout = QVBoxLayout()
        
        # Add a title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Create a table for the data
        table = QTableWidget()
        
        if title == "Recent Lottery Results":
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels(["Draw Date", "1", "2", "3", "4", "5", "6"])
            
            # Use the existing function to populate the table
            if hasattr(parent, 'recent_results_table') and parent.recent_results_table is not None:
                # Copy data from the existing table
                for row in range(parent.recent_results_table.rowCount()):
                    table.insertRow(row)
                    for col in range(parent.recent_results_table.columnCount()):
                        item = parent.recent_results_table.item(row, col)
                        if item:
                            table.setItem(row, col, QTableWidgetItem(item.text()))
            else:
                # Sample data if no real data is available
                for i in range(10):
                    table.insertRow(i)
                    table.setItem(i, 0, QTableWidgetItem(f"2025-03-{30-i}"))
                    for j in range(1, 7):
                        table.setItem(i, j, QTableWidgetItem(str((i+j*5) % 59 + 1)))
        
        elif title == "Lucky Numbers History":
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels(["Lotto Type", "1", "2", "3", "4", "5", "6"])
            
            # Use the existing function to populate the table
            if hasattr(parent, 'history_table') and parent.history_table is not None:
                # Copy data from the existing table
                for row in range(parent.history_table.rowCount()):
                    table.insertRow(row)
                    for col in range(parent.history_table.columnCount()):
                        item = parent.history_table.item(row, col)
                        if item:
                            table.setItem(row, col, QTableWidgetItem(item.text()))
            else:
                # Sample data if no real data is available
                for i in range(10):
                    table.insertRow(i)
                    table.setItem(i, 0, QTableWidgetItem(f"Grand Lotto 6/55"))
                    for j in range(1, 7):
                        table.setItem(i, j, QTableWidgetItem(str((i*j+10) % 59 + 1)))
        
        elif title == "More Details":
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["Number", "Frequency"])
            
            # Use the existing function to populate the table
            if hasattr(parent, 'result_table') and parent.result_table is not None:
                # Copy data from the existing table
                for row in range(parent.result_table.rowCount()):
                    table.insertRow(row)
                    for col in range(parent.result_table.columnCount()):
                        item = parent.result_table.item(row, col)
                        if item:
                            table.setItem(row, col, QTableWidgetItem(item.text()))
            else:
                # Sample data if no real data is available
                for i in range(59):
                    table.insertRow(i)
                    table.setItem(i, 0, QTableWidgetItem(str(i+1)))
                    table.setItem(i, 1, QTableWidgetItem(str((100-i) % 30 + 1)))
        
        # Set table properties
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f0f0f0;
            }
            QHeaderView::section {
                background-color: #2a3990;
                color: white;
                font-weight: bold;
                padding: 6px;
            }
        """)
        
        layout.addWidget(table)
        
        # Add a close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)

def restart_app():
    try:
        print("Restarting app in 2 seconds...")
        python = sys.executable
        script = sys.argv[0]
        
        # Add quotes around the script path to handle spaces
        if ' ' in script:
            script = f'"{script}"'

        os.execl(python, python, script, *sys.argv[1:])
    except Exception as e:
        print(f"Failed to restart the app: {e}")
        sys.exit(1)

def build_modern_ui(parent):
    """Build a modern UI for the lottery application"""
    
    # Set up the main layout
    main_layout = QVBoxLayout(parent)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    
    # Create a widget to hold the background
    background_widget = QWidget()
    
    # Get the size for the main window
    main_window_size = get_main_window_size()
    
    # Find the background image using the correct path
    assets_dir = os.path.join(os.path.dirname(__file__), "Assets")
    bg_path = os.path.join(assets_dir, "layout_main_screen.png")
    
    if os.path.exists(bg_path):
        print(f"Found background image: {bg_path}")
        
        # Load the background image
        bg_pixmap = QPixmap(bg_path)
        if not bg_pixmap.isNull():
            # Scale the image to match the main window size
            scaled_bg = bg_pixmap.scaled(
                main_window_size.width(),
                main_window_size.height(),
                Qt.AspectRatioMode.IgnoreAspectRatio,  # Fill the entire window
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Create a background label with the scaled image
            bg_label = QLabel(background_widget)
            bg_label.setPixmap(scaled_bg)
            bg_label.setGeometry(0, 0, main_window_size.width(), main_window_size.height())
            bg_label.lower()
            
            print(f"Scaled background image to: {scaled_bg.width()}x{scaled_bg.height()}")
        else:
            print(f"Failed to load background image from {bg_path}, using gradient fallback")
            background_widget.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                           stop:0 #1a237e, stop:0.5 #283593, stop:1 #303f9f);
            """)
    else:
        # Fallback to a gradient if the image doesn't exist
        print(f"Background image not found at {bg_path}, using gradient fallback")
        background_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                       stop:0 #1a237e, stop:0.5 #283593, stop:1 #303f9f);
        """)
    
    # Set up the layout for the background widget
    bg_layout = QVBoxLayout(background_widget)
    bg_layout.setContentsMargins(10, 10, 10, 10)
    
    # Create the top bar
    top_bar = QHBoxLayout()
    top_bar.setContentsMargins(30, 30, 30, 0)

    spacer_width = int(parent.width() * 0.015)

    # Create a QSpacerItem with the calculated width
    spacer = QSpacerItem(spacer_width, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
    top_bar.addItem(spacer)
    
    # Back button
    back_button = QPushButton(" Back")
    back_button.setIcon(QIcon.fromTheme("go-previous"))
    back_button.setStyleSheet("""
        QPushButton {
            background-color: rgba(0, 0, 0, 0.5);
            color: white;
            border-radius: 15px;
            padding: 1px 1px;
            font-size: 18px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: rgba(0, 0, 0, 0.7);
        }
    """)
    back_button.clicked.connect(lambda: (parent.close(), restart_app()))

    resize_widget_percent(back_button, width_percent=0.06, height_percent=0.04)

    top_bar.addWidget(back_button)

    spacer_width = int(parent.width() * 0.125)

    # Create a QSpacerItem with the calculated width
    spacer = QSpacerItem(spacer_width, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
    top_bar.addItem(spacer)
    
    # Group info button
    group_info_button = QPushButton("Group Info")
    group_info_button.setStyleSheet("""
        QPushButton {
            background-color: rgba(255, 255, 255, 0.2);
            color: white;
            border-radius: 15px;
            padding: 1px 1px;
            font-size: 18px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.3);
        }
    """)
    group_info_button.clicked.connect(lambda: GroupInfoDialog(parent).exec())

    resize_widget_percent(group_info_button, width_percent=0.06, height_percent=0.04)

    top_bar.addWidget(group_info_button)

    # Add a spacer
    top_bar.addStretch()
    
    # Date/time display
    parent.date_time_label = QLabel()
    parent.date_time_label.setStyleSheet("""
        color: white;
        font-size: 16px;
        font-weight: bold;
    """)
    update_datetime(parent)
    
    # Set up a timer to update the date/time every second
    timer = QTimer(parent)
    timer.timeout.connect(lambda: update_datetime(parent))
    timer.start(1000)
    
    top_bar.addWidget(parent.date_time_label)
    
    bg_layout.addLayout(top_bar)
    
    # Create the content area
    content_layout = QHBoxLayout()
    content_layout.setContentsMargins(30, 0, 30, 30)  
    
    # Left sidebar
    sidebar = QFrame()
    sidebar.setStyleSheet("""
        background-color: rgba(0, 0, 30, 0.5);
        border-radius: 25px;
        margin: 10px;
        padding: 10px;
    """)

    resize_widget_percent(sidebar, width_percent=0.175, height_percent=0.6)
    sidebar_layout = QVBoxLayout(sidebar)

    sidebar_layout.setSpacing(0)  # Adjust spacing between widgets
    sidebar_layout.setContentsMargins(10, 10, 10, 10)  # Set margins to reduce space around content
    
    # Lottery game section
    game_label = QLabel("Lottery Game")
    game_label.setStyleSheet("""
        color: white;
        font-size: 21px;
        font-weight: bold;
        background-color: transparent;
    """)
    sidebar_layout.addWidget(game_label)
    game_label.setMinimumHeight(1)  # Set the minimum height for the label
    #parent.lottery_selector.setMinimumHeight(40)  # Set the minimum height for the dropdown
    
    # Lottery game dropdown
    parent.lottery_selector = QComboBox()
    parent.lottery_selector.addItems(LOTTERY_CONFIG.keys())
    parent.lottery_selector.setStyleSheet("""
        QComboBox {
            background-color: white;
            border-radius: 15px;  /* Rounded corners for the combo box */
            padding: 15px 15px;
            font-size: 16px;
            font-weight: bold;
            color: #2a3990;
        }
        QComboBox::drop-down {
            background-color: white;
            border: 1px solid #2a3990;  /* Border for the dropdown button */
            width: 20px;
            subcontrol-origin: padding;
            subcontrol-position: right center;
            border-top-right-radius: 15px;
            border-bottom-right-radius: 15px;  /* Rounded corners for the dropdown button */
        }
        QComboBox QAbstractItemView {
            background-color: white;
            color: #2a3990;
            selection-background-color: #FFA500;
            selection-color: white;
            border-radius: 15px;  /* Rounded corners for the dropdown list */
        }
        QComboBox::item {
            padding: 10px;
            border-radius: 15px;  /* Rounded corners for each item in the dropdown */
        }
    """)
    sidebar_layout.addWidget(parent.lottery_selector)
    resize_widget_percent(parent.lottery_selector, width_percent=0.145, height_percent=0.065)
    
    # Add a separator
    separator = QFrame()
    separator.setFrameShape(QFrame.Shape.HLine)
    separator.setFrameShadow(QFrame.Shadow.Sunken)
    separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.3);")
    sidebar_layout.addWidget(separator)
    
    # Recent results date section
    results_label = QLabel("RECENT RESULTS DATE")
    results_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
    sidebar_layout.addWidget(results_label)
    
    # From date
    from_layout = QHBoxLayout()
    from_label = QLabel("From:")
    from_label.setStyleSheet("color: white; font-size: 14px;")
    from_layout.addWidget(from_label)
    
    parent.from_date_edit = QDateEdit()
    parent.from_date_edit.setCalendarPopup(True)
    parent.from_date_edit.setDate(QDate.currentDate().addDays(-30))
    parent.from_date_edit.setStyleSheet("""
        QDateEdit {
            background-color: white;
            border-radius: 15px;
            padding: 8px 15px;
            font-size: 14px;
            font-weight: bold;
            color: #2a3990;
        }
    """)
    from_layout.addWidget(parent.from_date_edit)
    sidebar_layout.addLayout(from_layout)
    
    # To date
    to_layout = QHBoxLayout()
    to_label = QLabel("To:")
    to_label.setStyleSheet("color: white; font-size: 14px;")
    to_layout.addWidget(to_label)
    
    parent.to_date_edit = QDateEdit()
    parent.to_date_edit.setCalendarPopup(True)
    parent.to_date_edit.setDate(QDate.currentDate())
    parent.to_date_edit.setStyleSheet("""
        QDateEdit {
            background-color: white;
            border-radius: 15px;
            padding: 8px 15px;
            font-size: 14px;
            font-weight: bold;
            color: #2a3990;
        }
    """)
    to_layout.addWidget(parent.to_date_edit)
    sidebar_layout.addLayout(to_layout)
    
    # Generate button
    parent.generate_button = QPushButton("GENERATE")
    parent.generate_button.setStyleSheet("""
        QPushButton {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFA500, stop:1 #FF8C00);
            color: white;
            border-radius: 15px;
            padding: 12px;
            font-size: 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF8C00, stop:1 #FF7F00);
        }
    """)
    parent.generate_button.clicked.connect(lambda: parent.generate_lucky_numbers())
    sidebar_layout.addWidget(parent.generate_button)
    
    # Export data button
    parent.export_button = QPushButton("EXPORT DATA")
    parent.export_button.setStyleSheet("""
        QPushButton {
            background-color: rgba(255, 255, 255, 0.2);
            color: white;
            border-radius: 15px;
            padding: 12px;
            font-size: 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.3);
        }
    """)
    parent.export_button.clicked.connect(lambda: parent.export_data())
    sidebar_layout.addWidget(parent.export_button)
    
    # Add a spacer at the bottom
    sidebar_layout.addStretch()
    
    content_layout.addWidget(sidebar)
    
    # Main content area
    main_content = QWidget()
    main_content_layout = QVBoxLayout(main_content)

    # Lottery balls area
    balls_layout = QHBoxLayout()
    balls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    balls_layout.setSpacing(-50)  # Set spacing to 0 to have the balls right next to each other

    # Optional: Remove layout margins if any
    balls_layout.setContentsMargins(0, 0, 0, 0)  # No margins between balls and layout edges

    # Add object name to the layout
    balls_layout.setObjectName("balls_layout")

    # Create lottery balls with images
    # Randomize the ball indices (1-6)
    ball_indices = list(range(1, 7))
    random.shuffle(ball_indices)

    # Default numbers (will be updated when generating)
    default_numbers = [42, 45, 49, 58, 55, 6]
    parent.lottery_balls = []

    for i, ball_index in enumerate(ball_indices):
        ball_widget = BallWidget(default_numbers[i], ball_index)
        balls_layout.addWidget(ball_widget)
        parent.lottery_balls.append(ball_widget)

    # Add the layout to the main content
    main_content_layout.addLayout(balls_layout)
    
    # Lucky combination text
    lucky_text = QLabel("IS YOUR LUCKY COMBINATION!")
    lucky_text.setStyleSheet("""
        color: white;
        font-size: 28px;
        font-weight: bold;
    """)
    lucky_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
    main_content_layout.addWidget(lucky_text)
    
    # Add some spacing
    main_content_layout.addSpacing(20)
    
    # See more details button
    see_more_button = QPushButton("See More Details")
    see_more_button.setStyleSheet("""
        QPushButton {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFA500, stop:1 #FF8C00);
            color: white;
            border-radius: 15px;
            padding: 10px 20px;
            font-size: 16px;
            font-weight: bold;
            max-width: 250px;
        }
        QPushButton:hover {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF8C00, stop:1 #FF7F00);
        }
    """)
    see_more_button.clicked.connect(lambda: ResultsDialog("More Details", None, parent).exec())
    
    # Center the button
    see_more_layout = QHBoxLayout()
    see_more_layout.addStretch()
    see_more_layout.addWidget(see_more_button)
    see_more_layout.addStretch()
    
    main_content_layout.addLayout(see_more_layout)
    
    # Add a spacer
    main_content_layout.addStretch()
    
    # Bottom navigation buttons
    bottom_nav = QFrame()
    bottom_nav.setStyleSheet("""
        background-color: rgba(0, 0, 30, 0.5);
        border-radius: 15px;
        margin: 20px;
        padding: 10px;
    """)
    
    bottom_nav_layout = QHBoxLayout(bottom_nav)
    
    # Recent lottery results button
    recent_results_button = QPushButton("Recent Lottery Results")
    recent_results_button.setIcon(QIcon.fromTheme("go-next"))
    recent_results_button.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    recent_results_button.setStyleSheet("""
        QPushButton {
            background-color: transparent;
            color: white;
            font-size: 16px;
            font-weight: bold;
            border: none;
            text-align: left;
            padding: 10px;
        }
        QPushButton:hover {
            color: #FFA500;
        }
    """)
    recent_results_button.clicked.connect(lambda: ResultsDialog("Recent Lottery Results", None, parent).exec())
    bottom_nav_layout.addWidget(recent_results_button)
    
    # Add a spacer
    bottom_nav_layout.addStretch()
    
    # Lucky numbers history button
    history_button = QPushButton("Lucky Numbers History")
    history_button.setIcon(QIcon.fromTheme("go-next"))
    history_button.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    history_button.setStyleSheet("""
        QPushButton {
            background-color: transparent;
            color: white;
            font-size: 16px;
            font-weight: bold;
            border: none;
            text-align: left;
            padding: 10px;
        }
        QPushButton:hover {
            color: #FFA500;
        }
    """)
    history_button.clicked.connect(lambda: ResultsDialog("Lucky Numbers History", None, parent).exec())
    bottom_nav_layout.addWidget(history_button)
    
    main_content_layout.addWidget(bottom_nav)
    
    content_layout.addWidget(main_content)
    
    bg_layout.addLayout(content_layout)
    
    main_layout.addWidget(background_widget)
    
    # Set the size of the parent widget to match the main window size
    parent.setFixedSize(main_window_size)
    
    # Create hidden tables for storing data
    parent.recent_results_table = QTableWidget()
    parent.recent_results_table.setColumnCount(7)
    parent.recent_results_table.setHorizontalHeaderLabels(["Draw Date", "1", "2", "3", "4", "5", "6"])
    parent.recent_results_table.hide()
    
    parent.history_table = QTableWidget()
    parent.history_table.setColumnCount(7)
    parent.history_table.setHorizontalHeaderLabels(["Lotto Type", "1", "2", "3", "4", "5", "6"])
    parent.history_table.hide()
    
    parent.result_table = QTableWidget()
    parent.result_table.setColumnCount(2)
    parent.result_table.setHorizontalHeaderLabels(["Number", "Frequency"])
    parent.result_table.hide()
    
    return main_layout

def get_main_window_size():
    """Get the size that will be used for the main window"""
    screen = QApplication.primaryScreen()
    screen_size = screen.size()
    
    width = int(screen_size.width() * 0.6)
    height = int(screen_size.height() * 0.75)
    
    return QSize(width, height)

def update_datetime(parent):
    """Update the date/time label"""
    now = datetime.now()
    date_str = now.strftime("%B %d, %Y")
    time_str = now.strftime("%I:%M %p")
    parent.date_time_label.setText(f"{date_str}  {time_str}")

def update_lottery_balls(parent, numbers):
    ball_indices = list(range(1, 7))
    random.shuffle(ball_indices)

    balls_layout = parent.findChild(QHBoxLayout, "balls_layout")
    if balls_layout:
        for ball in parent.lottery_balls:
            balls_layout.removeWidget(ball)
            ball.deleteLater()

        parent.lottery_balls = []

        for i, ball_index in enumerate(ball_indices):
            if i < len(numbers):
                ball_widget = BallWidget(numbers[i], ball_index)
                balls_layout.addWidget(ball_widget)
                parent.lottery_balls.append(ball_widget)
