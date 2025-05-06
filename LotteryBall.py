from itertools import combinations
import random
import Assets_rc
from datetime import datetime
from collections import Counter
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QComboBox, QDateEdit, QScrollArea, QGridLayout,
                             QHBoxLayout, QPushButton, QLabel, QTableWidgetItem, QTableWidget,
                             QFrame, QStackedWidget, QDesktopWidget, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtGui import QPalette, QColor, QFont, QBrush, QIcon, QPixmap

from BallWidget import BallWidget
from RoundWidget import RoundedWidget
from CircleButtons import CircleButtonBack, CircleButtonInfo, CircleButtonNext, CircleButtonPrev
from FetchResultsThread import FetchResultsThread


from Export import export_data_to_csv

LOTTERY_CONFIG = {
    "Ultra Lotto 6/58": (1, 58), 
    "Grand Lotto 6/55": (1, 55), 
    "Superlotto 6/49": (1, 49), 
    "Megalotto 6/45": (1, 45), 
    "Lotto 6/42": (1, 42)
}

class LotteryBall(QMainWindow):
    def __init__(self, asset_manager):
        super().__init__()
        # Initialize instance variables
        self.asset_manager = asset_manager
        self.lottery_balls = []
        self.lucky_numbers = []
        self.selected_lottery_type = "Lotto 6/42"  # Default lottery type
        
        self.initUI()
        icon_path = self.asset_manager.load_asset("Assets/Icons/app_icon.ico")
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
    
    def initUI(self):
        self.setWindowTitle('Let\'s Play Loto')
        self.resize_window_to_percentage()
        self.center_window()
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(50, 50, 50, 50)

        # Outer container with rounded corners
        outer_container = RoundedWidget(radius=30, color1=QColor(0, 0, 0, 50))
        outer_layout = QVBoxLayout(outer_container)
        outer_layout.setContentsMargins(30, 30, 30, 30)
        outer_layout.setSpacing(25)
        main_layout.addWidget(outer_container)
        
        # Top Section (Back Button, Title, and DateTime)
        top_layout = self.create_top_section()
        outer_layout.addLayout(top_layout)
        
        # Content Section (Left and Right Panels)
        content_layout = self.create_content_section()
        outer_layout.addLayout(content_layout, 1)

        # Set image background for the main window
        self.setAutoFillBackground(True)
        
        self.set_image_background(self.asset_manager.load_asset("Assets/Screens/main_screen_background.png"))

    def resize_window_to_percentage(self):
        # Get the screen's dimensions
        screen = QDesktopWidget().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

        # Define window size as a percentage of the screen size
        window_width_percentage = 0.75  # 75% of the screen width
        window_height_percentage = 0.8  # 80% of the screen height

        # Calculate window's size based on the percentages
        window_width = int(screen_width * window_width_percentage)
        window_height = int(screen_height * window_height_percentage)

        # Set initial window size but allow manual resizing
        self.resize(window_width, window_height)

    def center_window(self):
        # Get the screen's dimensions
        screen = QDesktopWidget().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

        # Get the window's current size after it is shown
        window_width = self.frameGeometry().width()
        window_height = self.frameGeometry().height()

        # Calculate the top-left position to center the window
        x_pos = (screen_width - window_width) // 2
        y_pos = (screen_height - window_height) // 2

        # Move the window to the calculated position
        self.move(x_pos, y_pos)
    
    def create_top_section(self):
        top_layout = QHBoxLayout()
        top_layout.setSpacing(25)

        # Back button (circle)
        self.back_button = CircleButtonBack(asset_manager=self.asset_manager,on_back_pressed=self.back_to_splash)
        top_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        # Title section
        title_widget = QWidget()
        title_widget.setStyleSheet("background-color: rgba(200, 200, 200, 0); border-radius: 10px;")
        title_layout = QVBoxLayout(title_widget)
        title_layout.setAlignment(Qt.AlignVCenter)
        
        title_label = QLabel("LET\'S PLAY LOTTO")
        title_label.setFont(QFont("Roboto Condensed", 24, QFont.ExtraBold))
        title_label.setStyleSheet("color: #FFFFFF;")  # Replace with your desired color
        title_label.setAlignment(Qt.AlignLeft)
        title_layout.addWidget(title_label)
        top_layout.addWidget(title_widget, 1)

        # DateTime section
        datetime_widget = self.create_datetime_section()
        top_layout.addWidget(datetime_widget, alignment=Qt.AlignRight)

        # Info button (circle)
        self.info_button = CircleButtonInfo(asset_manager=self.asset_manager,on_info_pressed=self.show_info_dialog)
        top_layout.addWidget(self.info_button, alignment=Qt.AlignCenter)
        
        return top_layout

    def create_datetime_section(self):
        datetime_widget = QWidget()
        datetime_widget.setStyleSheet("background-color: rgba(200, 200, 200, 0); border-radius: 10px;")
        datetime_layout = QVBoxLayout(datetime_widget)
        datetime_layout.setContentsMargins(10, 5, 10, 5)
        datetime_layout.setAlignment(Qt.AlignCenter)

        self.datetime_label = QLabel()
        self.datetime_label.setFont(QFont("Roboto", 14, QFont.Medium))
        self.datetime_label.setStyleSheet("color: #FFFFFF;")
        self.datetime_label.setAlignment(Qt.AlignCenter)

        self.datetime_timer = QTimer()
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(1000)
        self.update_datetime()

        datetime_layout.addWidget(self.datetime_label)
        
        return datetime_widget
    
    def create_content_section(self):
        content_layout = QHBoxLayout()
        content_layout.setSpacing(25)
        
        # Left Panel (controls)
        left_panel = self.create_left_panel()
        content_layout.addWidget(left_panel, 1)

        # Right Panel (Lucky Number, Generated Number Details, Recent Results, Generated Number History)
        right_panel = self.create_right_panel()
        content_layout.addWidget(right_panel, 2)
        
        return content_layout
    
    def create_left_panel(self):
        left_panel = QWidget()
        left_panel.setStyleSheet("background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1," \
                                "stop: 0 rgba(60, 85, 180, 0.25)," \
                                "stop: 1 rgba(55, 55, 150, 0.25));; border-radius: 20px;")
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.setSpacing(25)
        left_layout.setContentsMargins(15, 15, 15, 15)

        control_panel = self.create_control_panel()
        control_panel.setStyleSheet("background-color: rgba(145, 145, 220, 0); border-radius: 20px;")
        left_layout.addWidget(control_panel)
        left_layout.addStretch()

        return left_panel

    def create_control_panel(self):
        control_panel = RoundedWidget(radius=20)
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(20, 20, 20, 20)
        control_layout.setSpacing(10)

        # Lottery Game Selector
        lottery_game_label = QLabel("  Choose Lottery Game")
        lottery_game_label.setFont(QFont("Roboto", 18, QFont.Bold))
        lottery_game_label.setStyleSheet("color: #FFFFFF; background-color: rgba(145, 145, 220, 0)")
        control_layout.addWidget(lottery_game_label)
        
        lottery_options = ["Lotto 6/42", "Megalotto 6/45", "Superlotto 6/49", "Grand Lotto 6/55", "Ultra Lotto 6/58"]
        self.lottery_dropdown = self.create_dropdown_field(lottery_options)
        self.lottery_dropdown.currentIndexChanged.connect(self.on_lottery_selection_changed)
        control_layout.addWidget(self.lottery_dropdown)

        control_layout.addSpacing(15)

        # Results Date
        date_range_label = QLabel("  Set Results Date")
        date_range_label.setFont(QFont("Roboto", 18, QFont.Bold))
        date_range_label.setStyleSheet("color: #FFFFFF; background-color: rgba(145, 145, 220, 0)")
        control_layout.addWidget(date_range_label)

        icon_path = self.asset_manager.load_asset("Assets/Screens/splash_screen.png")

        # From Date
        from_layout = QHBoxLayout()
        from_label = QLabel("     From:")
        from_label.setStyleSheet("color: #FFFFFF; font-size: 16px;")
        from_layout.addWidget(from_label)

        self.from_date_edit = self.create_date_edit_field(QDate.currentDate().addDays(-30))
        from_layout.addWidget(self.from_date_edit)
        control_layout.addLayout(from_layout)

        # To date
        to_layout = QHBoxLayout()
        to_label = QLabel("     To:")
        to_label.setStyleSheet("color: #FFFFFF; font-size: 16px;")
        to_layout.addWidget(to_label)

        self.to_date_edit = self.create_date_edit_field(QDate.currentDate())
        to_layout.addWidget(self.to_date_edit)
        control_layout.addLayout(to_layout)

        control_layout.addSpacing(15)

        # Add button to fetch results
        fetch_button = QPushButton("Get Recent Results")
        fetch_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(55, 55, 150, 0.75);
                color: rgba(255, 255, 255, 1);
                border-radius: 20px;
                padding: 8px;
                font-family: 'Roboto Black';
                font-size: 20px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: rgba(55, 55, 150, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(55, 55, 150, 0.25);
            }                       

        """)
        fetch_button.clicked.connect(self.check_and_fetch_results)
        control_layout.addWidget(fetch_button)

        control_layout.addSpacing(10)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setFixedHeight(4)  # Fixed Height
        separator.setFixedWidth(300)  # Fixed Width

        separator.setStyleSheet("""
            QFrame {
                border-radius: 2px;
                color: #666666;          /* Line color (used for shadows) */
                background-color: rgba(255, 255, 255, 0.25); /* Actual line color */
            }
        """)

        control_layout.addWidget(separator)
        
        control_layout.setAlignment(separator, Qt.AlignHCenter)

        control_layout.addSpacing(10)

        # Buttons
        buttons_layout = self.create_main_buttons_layout()
        control_layout.addLayout(buttons_layout)
        
        control_layout.addSpacing(10)

        return control_panel

    def on_lottery_selection_changed(self):
        """Triggered when the lottery type selection changes"""
        self.selected_lottery_type = self.lottery_dropdown.currentText()
        self.check_and_fetch_results()

    def check_and_fetch_results(self):
        """Check if the date range is valid and trigger fetching of results"""
        from_date = self.from_date_edit.date()
        to_date = self.to_date_edit.date()

        # Check if the From date is earlier than the To date
        if from_date <= to_date:
            # Fetch results if the date range is valid
            from_date_str = from_date.toString("MM/dd/yyyy")
            to_date_str = to_date.toString("MM/dd/yyyy")
            
            # Start the fetch thread to get recent results
            self.start_fetch_results_thread(self.selected_lottery_type, from_date_str, to_date_str)
        else:
            # Display a warning if the date range is invalid
            QMessageBox.warning(self, "Invalid Date Range", "From date must not be later than To date.")

    def start_fetch_results_thread(self, lottery_type, from_date, to_date):
        """Start the thread to fetch lottery results"""
        self.fetch_results_thread = FetchResultsThread(lottery_type, self.lucky_numbers, from_date, to_date)
        self.fetch_results_thread.results_fetched.connect(self.display_recent_results)
        self.fetch_results_thread.start()
    
    def update_lucky_label(self):
        # Check if any of the balls still have the default "00" number
        if any(ball.get_number() == "00" for ball in self.lottery_balls):
            self.lucky_label.setText("")  # Set to blank if any ball has the default number
        else:
            self.lucky_label.setText("IS YOUR LUCKY COMBINATION!")  # Set text when numbers are updated

    def create_dropdown_field(self, items):
        combo_box = QComboBox()
        combo_box.addItems(items)

        # Get the down arrow icon path through the asset manager
        down_arrow_path = self.asset_manager.load_asset("Assets/Icons/down_icon.png")

        combo_box.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: none;
                border-radius: 10px;
                background-color: rgba(55, 55, 150, 0.75);
                font-family: 'Roboto SemiBold';
                font-size: 16px;
                color: rgba(255, 255, 255, 1);
            }

            QComboBox QAbstractItemView {
                padding: 10px;
                background: rgba(255, 255, 255, 0);;
                background-color: rgba(255, 255, 255, 0.75);  /* Dropdown background */
                selection-background-color: #19194B;
                font-family: 'Roboto Medium';
                font-size: 16px;
                color: rgba(25, 25, 75, 0.75);
                border: none;
                outline: 0;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            }
                                
            QComboBox QAbstractItemView::item:selected {
                background-color: #19194B;  /* Selected item background color */
            }

            QComboBox QAbstractItemView::item {
                padding: 10px;
                margin-bottom: 6px;
                background-color: #19194B;
            }   

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border: none;
                background: transparent;
            }

            QComboBox::down-arrow {
                image: url(:/Assets/Icons/down_icon.png);
                width: 12px;
                height: 12px;
                margin-right: 10px;
            }
        """)

        combo_box.setMinimumHeight(40)
        return combo_box
    
    def create_date_edit_field(self, date: QDate) -> QDateEdit:
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(date)
        date_edit.setFixedWidth(200)  # Adjust to your preferred size
        date_edit.setFixedHeight(40)  # Adjust to your preferred size

        # Get the down arrow icon path through the asset manager
        down_arrow_path = self.asset_manager.load_asset("Assets/Icons/down_icon.png")

        date_edit.setStyleSheet("""
            QDateEdit {
                border-radius: 10px;
                padding: 8px 12px;
                background-color: rgba(55, 55, 150, 0.75);
                font-family: 'Roboto Medium';
                font-size: 16px;
                color: #FFFFFF;
            }

            QDateEdit:focus {
                border: 2px solid #FFFFFF;
                background-color: rgba(55, 55, 150, 0.25);
            }

            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 35px;
                border-left: 2px solid rgba(255, 255, 255, 0);
            }

            QDateEdit::down-arrow {
                width: 12;
                height: 12;
                image: url(:/Assets/Icons/down_icon.png);
            }

            QCalendarWidget {
                background-color: white;
                border-radius: 10px;
                border: none;
            }

            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #f8f8f8;
                padding: 4px;
            }

            QCalendarWidget QToolButton {
                background-color: transparent;
                color: #55557D;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 10px;
            }

            QCalendarWidget QToolButton:hover {
                background-color: rgba(145, 145, 220, 0.2);
            }

            QCalendarWidget QToolButton:pressed {
                background-color: rgba(145, 145, 220, 0.3);
            }

            QCalendarWidget QToolButton::menu-indicator {
                image: none;
            }

            QCalendarWidget QToolButton#qt_calendar_prevmonth {
                qproperty-icon: none;
                qproperty-text: "<";
                font-weight: bold;
            }

            QCalendarWidget QToolButton#qt_calendar_nextmonth {
                qproperty-icon: none;
                qproperty-text: ">";
                font-weight: bold;
            }

            QCalendarWidget QWidget#qt_calendar_calendarview {
                background-color: white;
                selection-background-color: #9191DC;
                selection-color: white;
                alternate-background-color: white;
            }

            QCalendarWidget QAbstractItemView:enabled {
                background-color: white;
                color: #333333;
                selection-background-color: #9191DC;
                selection-color: white;
                font-size: 13px;
                outline: none;
            }

            QCalendarWidget QAbstractItemView::item {
                padding: 6px;
                margin: 1px;
                border-radius: 4px;
            }

            QCalendarWidget QAbstractItemView::item:selected {
                background-color: #9191DC;
                color: white;
            }

            QCalendarWidget QAbstractItemView::item:hover {
                background-color: rgba(145, 145, 220, 1);
                border: none;
            }

            QCalendarWidget QAbstractItemView::item[today="true"] {
                background-color: rgba(145, 145, 220, 0.1);
                color: #9191DC;
                font-weight: bold;
            }

            QCalendarWidget QAbstractItemView::item[weekend="true"] {
                color: #7777B2;
            }

            QCalendarWidget QHeaderView {
                background-color: white;
            }

            QCalendarWidget QHeaderView::section {
                background-color: #f8f8f8;
                color: #55557D;
                font-size: 12px;
                font-weight: bold;
                padding: 6px;
                border: none;
            }

            QCalendarWidget QSpinBox {
                background-color: white;
                color: #55557D;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 3px;
                margin: 2px;
            }

            QCalendarWidget QMenu {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }

            QCalendarWidget QMenu::item {
                padding: 6px 20px;
            }

            QCalendarWidget QMenu::item:selected {
                background-color: #9191DC;
                color: white;
            }
        """)
        return date_edit

    def create_main_buttons_layout(self):
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        self.generate_button = self.create_main_buttons("GENERATE")
        self.generate_button.clicked.connect(self.generate_lucky_numbers)     #Connect to Generate Function
        save_button = self.create_main_buttons("Save Data")
        save_button.clicked.connect(self.save_data)         #Connect to Save Data to CSV
        
        buttons_layout.addWidget(self.generate_button)
        buttons_layout.addWidget(save_button)

        return buttons_layout

    def create_main_buttons(self, text): # Plot, Save Graph buttons styling
        button = QPushButton(text)

        button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, 0.9),
                                stop: 1 rgba(245, 115, 35, 0.9));
                color: white;
                border-radius: 20px;
                padding: 10px;
                font-family: 'Roboto Black';
                font-size: 20px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #7777B2;
            }
            QPushButton:pressed {
                background-color: #55557D;
            }
        """)
        return button

    def create_right_panel(self):
        right_panel = QWidget()
        right_panel.setStyleSheet("background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1," \
                                "stop: 0 rgba(60, 85, 180, 0.25)," \
                                "stop: 1 rgba(55, 55, 150, 0.25));; border-radius: 20px;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(20)

        # Top bar with Prev | Tab Title | Next
        top_bar = QHBoxLayout()

        self.prev_button = CircleButtonPrev(asset_manager=self.asset_manager)
        self.next_button = CircleButtonNext(asset_manager=self.asset_manager)

        self.tab_title_label = QLabel("Lucky Numbers")
        self.tab_title_label.setAlignment(Qt.AlignCenter)
        self.tab_title_label.setFont(QFont("Roboto", 16, QFont.Bold))
        self.tab_title_label.setStyleSheet("color: #FFFFFF; background-color: rgba(255, 255, 255, 0);")

        top_bar.addSpacing(20)  
        top_bar.addWidget(self.prev_button)
        top_bar.addStretch()
        top_bar.addWidget(self.tab_title_label)
        top_bar.addStretch()
        top_bar.addWidget(self.next_button)
        top_bar.addSpacing(20)  

        right_layout.addLayout(top_bar)

        # Stack for tabs
        self.stacked_widget = self.create_stacked_widget()
        right_layout.addWidget(self.stacked_widget)

        # Button logic
        self.tab_titles = [
            "Lucky Numbers",
            "Number Frequency",
            "Recent Lottery Results",
            "Lucky Numbers History"
        ]
        self.current_tab_index = 0
        self.prev_button.clicked.connect(self.show_previous_tab)
        self.next_button.clicked.connect(self.show_next_tab)
        
        return right_panel
    
    def create_stacked_widget(self):
        self.stacked_widget = QStackedWidget()
        
        # Initialize the number_labels dictionary
        self.number_labels = {}

        # --------- Tab 1: Lucky Numbers ----------
        lucky_tab = RoundedWidget(radius=20)
        lucky_layout = QVBoxLayout(lucky_tab)
        lucky_layout.setSpacing(15)

        self.first_row_layout = QHBoxLayout()
        self.first_row_layout.setSpacing(10)
        self.first_row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        lucky_layout.addLayout(self.first_row_layout)
        
        self.second_row_layout = QHBoxLayout()
        self.second_row_layout.setSpacing(10)
        self.second_row_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        lucky_layout.addLayout(self.second_row_layout)

        # Create and store the ball widgets
        self.lottery_balls = []
        ball_indices = list(range(1, 7))  # Initially from 1 to 6
        random.shuffle(ball_indices)
        default_numbers = ["00", "00", "00", "00", "00", "00"]  # placeholder values

        for i in range(6):
            ball = BallWidget(default_numbers[i], ball_indices[i], asset_manager=self.asset_manager)
            self.lottery_balls.append(ball)
            if i < 3:
                self.first_row_layout.addWidget(ball)
            else:
                self.second_row_layout.addWidget(ball)

        self.lucky_label = QLabel("IS YOUR LUCKY COMBINATION!")
        self.lucky_label.setAlignment(Qt.AlignCenter)
        self.lucky_label.setFont(QFont("Roboto", 24, QFont.Bold))
        self.lucky_label.setStyleSheet("color: #FFFFFF; background-color: rgba(255, 255, 255, 0);")
        lucky_layout.addWidget(self.lucky_label)

        # Call the update function after initializing the balls
        self.update_lucky_label()

        # Add the label to the layout
        lucky_layout.addWidget(self.lucky_label)

        self.stacked_widget.addWidget(lucky_tab)

        # --------- Tab 2: See More Details (Frequency Grid with Boxes) ----------
        freq_tab = RoundedWidget(radius=20)
        freq_layout = QVBoxLayout(freq_tab)
        
        # Create a scroll area for the frequency grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: transparent; border: none;")
        
        # Create a container widget for the grid
        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background-color: transparent;")
        
        # Create a grid layout for the frequency boxes
        self.freq_grid = QGridLayout(self.grid_container)
        self.freq_grid.setSpacing(10)
        
        # Set the grid container as the scroll area's widget
        scroll_area.setWidget(self.grid_container)
        
        # Add the scroll area to the frequency tab layout
        freq_layout.addWidget(scroll_area)
        
        # Add a label explaining the display
        info_label = QLabel("Numbers are displayed with their frequency. Top 6 most frequent numbers are highlighted.")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setFont(QFont("Roboto", 12))
        info_label.setStyleSheet("color: white; padding: 10px; background-color: rgba(55, 55, 150, 0);")
        freq_layout.addWidget(info_label)
        
        # Initialize the frequency grid
        self.update_frequency_grid()
        
        self.stacked_widget.addWidget(freq_tab)

        # --------- Tab 3: Recent Lottery Results ----------
        recent_tab = RoundedWidget(radius=20)
        recent_layout = QVBoxLayout(recent_tab)
        recent_layout.setContentsMargins(15, 15, 15, 15)
        recent_layout.setSpacing(15)

        # Create a scroll area for the results
        results_scroll = QScrollArea()
        results_scroll.setWidgetResizable(True)
        results_scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Create a container widget for the results
        results_container = QWidget()
        results_container.setStyleSheet("background-color: transparent;")
        self.results_layout = QVBoxLayout(results_container)
        self.results_layout.setSpacing(15)
        self.results_layout.setContentsMargins(5, 5, 5, 5)

        # Add a placeholder message when no results are available
        self.no_results_label = QLabel("No recent results available. Use the 'Get Recent Results' button to fetch data.")
        self.no_results_label.setAlignment(Qt.AlignCenter)
        self.no_results_label.setFont(QFont("Roboto", 14))
        self.no_results_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); padding: 20px;")
        self.no_results_label.setWordWrap(True)
        self.results_layout.addWidget(self.no_results_label)

        # Set the container as the scroll area's widget
        results_scroll.setWidget(results_container)

        # Add the scroll area to the tab layout
        recent_layout.addWidget(results_scroll)

        self.stacked_widget.addWidget(recent_tab)

        # --------- Tab 4: History of Lucky Numbers ----------
        history_tab = RoundedWidget(radius=20)
        history_layout = QVBoxLayout(history_tab)
        history_layout.setContentsMargins(15, 15, 15, 15)
        history_layout.setSpacing(15)

        # Create a scroll area for the history
        history_scroll = QScrollArea()
        history_scroll.setWidgetResizable(True)
        history_scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Create a container widget for the history
        history_container = QWidget()
        history_container.setStyleSheet("background-color: transparent;")
        self.history_cards_layout = QVBoxLayout(history_container)
        self.history_cards_layout.setSpacing(15)
        self.history_cards_layout.setContentsMargins(5, 5, 5, 5)

        # Add a placeholder message when no history is available
        self.no_history_label = QLabel("No history available. Generate lucky numbers to see them here.")
        self.no_history_label.setAlignment(Qt.AlignCenter)
        self.no_history_label.setFont(QFont("Roboto", 14))
        self.no_history_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); padding: 20px;")
        self.no_history_label.setWordWrap(True)
        self.history_cards_layout.addWidget(self.no_history_label)

        # Set the container as the scroll area's widget
        history_scroll.setWidget(history_container)

        # Add the scroll area to the tab layout
        history_layout.addWidget(history_scroll)

        # Create a hidden table for CSV export compatibility
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels(["Lotto Type", "1", "2", "3", "4", "5", "6"])
        self.history_table.hide()  # Hide the table as we're using cards instead

        self.stacked_widget.addWidget(history_tab)

        return self.stacked_widget
    
    def add_history(self, table, lottery_type, lucky_numbers, mirror_table=None):
        """Add a new entry to the history table and the history cards layout"""
        # Add to the hidden table for CSV export
        row_count = table.rowCount()
        table.insertRow(row_count)
        table.setItem(row_count, 0, QTableWidgetItem(lottery_type))
        for i, num in enumerate(lucky_numbers):
            table.setItem(row_count, i + 1, QTableWidgetItem(num))

        if mirror_table is not None:
            mirror_row = mirror_table.rowCount()
            mirror_table.insertRow(mirror_row)
            mirror_table.setItem(mirror_row, 0, QTableWidgetItem(lottery_type))
            for i, num in enumerate(lucky_numbers):
                mirror_table.setItem(mirror_row, i + 1, QTableWidgetItem(num))
        
        # Remove the placeholder if it exists
        if hasattr(self, 'no_history_label') and self.no_history_label.isVisible():
            self.no_history_label.setVisible(False)
        
        # Create a card for the history entry
        history_card = QFrame()
        history_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                            stop: 0 rgba(55, 55, 150, 0.7),
                            stop: 1 rgba(60, 85, 180, 0.7));
                border-radius: 15px;
                padding: 5px;
            }
            QFrame:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                            stop: 0 rgba(60, 85, 180, 0.8),
                            stop: 1 rgba(70, 95, 200, 0.8));
            }
        """)
        
        card_layout = QVBoxLayout(history_card)
        card_layout.setSpacing(10)
        
        # Lottery type
        type_label = QLabel(f"Lottery Game: {lottery_type}")
        type_label.setFont(QFont("Roboto", 16, QFont.Bold))
        type_label.setStyleSheet("color: white; background: rgba(255, 255, 255, 0)")
        type_label.setAlignment(Qt.AlignLeft)
        card_layout.addWidget(type_label)
        
        # Numbers container
        numbers_widget = QWidget()
        numbers_layout = QHBoxLayout(numbers_widget)
        numbers_layout.setSpacing(0)
        numbers_layout.setContentsMargins(0, 0, 0, 0)
        
        # Generate random ball indices
        # Method 1: Using a similar approach to display_recent_results
        # Use a random seed based on the current time to ensure different randomization each time
        random_seed = int(datetime.now().timestamp())
        random.seed(random_seed)
        
        # Method 2: Shuffle a list of indices
        ball_indices = list(range(1, 7))  # Indices 1-6
        random.shuffle(ball_indices)
        
        # Add lottery balls for each number using BallWidget with custom size
        for i, num in enumerate(lucky_numbers):
            # Method 1: Generate a random index using a formula
            # ball_index = (random_seed + i) % 6 + 1
            
            # Method 2: Use the shuffled indices
            ball_index = ball_indices[i]
            
            # Create a BallWidget with custom size and font size
            ball = BallWidget(num, ball_index, size=100, font_size=24, asset_manager=self.asset_manager)
            
            numbers_layout.addWidget(ball)

        # Center the numbers
        numbers_layout.addStretch()
        numbers_layout.insertStretch(0)
        
        card_layout.addWidget(numbers_widget)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_label = QLabel(f"Generated: {timestamp}")
        time_label.setFont(QFont("Roboto Medium", 10))
        time_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); background: rgba(255, 255, 255, 0)")
        time_label.setAlignment(Qt.AlignRight)
        card_layout.addWidget(time_label)
        
        # Add the card to the history layout at the top (newest first)
        self.history_cards_layout.insertWidget(0, history_card)

    def show_next_tab(self):
        # Increment tab index and wrap around using modulo if necessary
        self.current_tab_index = (self.current_tab_index + 1) % len(self.tab_titles)
        self.stacked_widget.setCurrentIndex(self.current_tab_index)
        self.tab_title_label.setText(self.tab_titles[self.current_tab_index])

    def show_previous_tab(self):
        # Decrement tab index and wrap around using modulo if necessary
        self.current_tab_index = (self.current_tab_index - 1) % len(self.tab_titles)
        self.stacked_widget.setCurrentIndex(self.current_tab_index)
        self.tab_title_label.setText(self.tab_titles[self.current_tab_index])

    def update_datetime(self):  # Date time update realtime
        current_time = datetime.now().strftime("%A, %B %d, %Y - %I:%M:%S %p")
        self.datetime_label.setText(current_time)
    
    def back_to_splash(self):   # Back button logic
        from SplashScreen import SplashScreen
        self.close()
        self.splash = SplashScreen(asset_manager=self.asset_manager)
        self.splash.show()
        QTimer.singleShot(100, self.close)  # Close after new splash is shown

    def show_info_dialog(self): # Info button logic
        QMessageBox.information(
            self,
            "Group Members",
            """
            <span style="font-size: 18px; font-weight: bold; color: #333;">GROUP MEMBERS:</span><br><br>
            <span style="font-size: 16px; font-weight: regular; color: #333;">1. Kurt Andre Olaer</span><br>
            <span style="font-size: 16px; font-weight: regular; color: #333;">2. James Dominic Tion</span><br>
            <span style="font-size: 16px; font-weight: regular; color: #333;">3. Mariel Laplap</span><br>
            <span style="font-size: 16px; font-weight: regular; color: #333;">4. Gwynette Galleros</span><br>
            <span style="font-size: 16px; font-weight: regular; color: #333;">5. Jeff Justin Bonior</span>
            """,
            QMessageBox.Ok
        )
    
    # Main app background logic 1
    def set_image_background(self, image_path): 
        self.image_path = image_path
        self.update_background()

    # Main app background logic 2
    def update_background(self):    
        palette = self.palette()
        pixmap = QPixmap(self.image_path)
        
        # Scale the image based on the current window size
        pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        
        # Set the image as the background
        palette.setBrush(QPalette.Background, QBrush(pixmap))
        self.setPalette(palette)

    # Update the image background whenever the window is resized
    def resizeEvent(self, event):
        self.update_background()
        super().resizeEvent(event)
        
    def display_recent_results(self, recent_results):
        """Display recent lottery results in a card-based layout with BallWidget"""
        # Clear previous results
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Show placeholder if no results
        if not recent_results:
            self.no_results_label = QLabel("No recent results available. Use the 'Get Recent Results' button to fetch data.")
            self.no_results_label.setAlignment(Qt.AlignCenter)
            self.no_results_label.setFont(QFont("Roboto", 14))
            self.no_results_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); padding: 20px;")
            self.no_results_label.setWordWrap(True)
            self.results_layout.addWidget(self.no_results_label)
            return
        
        # Add result cards
        for i, result_data in enumerate(recent_results):
            # Create a card for each result
            result_card = QFrame()
            result_card.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(55, 55, 150, 0.7),
                                stop: 1 rgba(60, 85, 180, 0.7));
                    border-radius: 15px;
                    padding: 5px;
                }
                QFrame:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(60, 85, 180, 0.8),
                                stop: 1 rgba(70, 95, 200, 0.8));
                }
            """)
            
            card_layout = QVBoxLayout(result_card)
            card_layout.setSpacing(10)
            
            # Draw date
            draw_date = result_data[0]
            date_label = QLabel(f"Draw Date: {draw_date}")
            date_label.setFont(QFont("Roboto", 16, QFont.Bold))
            date_label.setStyleSheet("color: white; background: rgba(255, 255, 255, 0);")
            date_label.setAlignment(Qt.AlignLeft)
            card_layout.addWidget(date_label)
            
            # Numbers container
            numbers_widget = QWidget()
            numbers_layout = QHBoxLayout(numbers_widget)
            numbers_layout.setSpacing(0)
            numbers_layout.setContentsMargins(0, 0, 0, 0)
            
            # Add lottery balls for each number using BallWidget with custom size
            for j in range(1, min(7, len(result_data))):
                number = result_data[j]
                if number:  # Only create a ball if there's a number
                    # Create a random ball index (1-6)
                    ball_index = (i + j) % 6 + 1
                    
                    # Create a BallWidget with custom size and font size
                    ball = BallWidget(number, ball_index, asset_manager=self.asset_manager, size=100, font_size=24)
                    
                    numbers_layout.addWidget(ball)
            
            # Center the numbers
            numbers_layout.addStretch()
            numbers_layout.insertStretch(0)
            
            card_layout.addWidget(numbers_widget)
            
            # Add the card to the results layout
            self.results_layout.addWidget(result_card)
        
        # Add a spacer at the end
        self.results_layout.addStretch()
        
        # Also update the table for CSV export compatibility
        self.update_results_table(recent_results)

    def update_results_table(self, recent_results):
        """Update the hidden table for CSV export compatibility"""
        # Create the table if it doesn't exist
        if not hasattr(self, 'recent_results_table'):
            self.recent_results_table = QTableWidget()
            self.recent_results_table.setColumnCount(7)
            self.recent_results_table.setHorizontalHeaderLabels(["Date", "1", "2", "3", "4", "5", "6"])
        
        # Clear previous results
        self.recent_results_table.setRowCount(0)
        
        # Add the results to the table
        self.recent_results_table.setRowCount(len(recent_results))
        for i, row_data in enumerate(recent_results):
            for j, item in enumerate(row_data):
                if j < self.recent_results_table.columnCount():
                    self.recent_results_table.setItem(i, j, QTableWidgetItem(str(item)))

    # --------- Functions related to populating the frequency table ---------

    def populate_table(self, table, number_counter):
        """Populate the frequency table with data"""
        table.setRowCount(len(number_counter))
        for i, (num, freq) in enumerate(number_counter.most_common()):
            table.setItem(i, 0, QTableWidgetItem(str(num)))
            table.setItem(i, 1, QTableWidgetItem(str(freq)))

    def update_frequency_display(self, number_counter):
        """Update the frequency display with the number frequencies."""
        # Get the top 6 numbers based on frequency
        top_6 = [num for num, _ in number_counter.most_common(6)]
        
        # Reset all boxes to default style first
        for num, (box, freq_label) in self.number_labels.items():
            box.setStyleSheet("""
                QFrame {
                    background-color: rgba(55, 55, 150, 0.5);
                    border-radius: 10px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
            """)
            
            # Set frequency to 0 by default
            freq_label.setText("0")
        
        # Update frequencies from the counter
        for num, freq in number_counter.items():
            if num in self.number_labels:
                box, freq_label = self.number_labels[num]
                freq_label.setText(str(freq))
                
                # Highlight top 6 numbers
                if num in top_6:
                    box.setStyleSheet("""
                        QFrame {
                            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                            stop: 0 rgba(255, 210, 80, 0.9),
                                            stop: 1 rgba(245, 115, 35, 0.9));
                            border-radius: 10px;
                            border: 2px solid white;
                        }
                    """)

    def on_lottery_selection_changed(self):
        """Triggered when the lottery type selection changes"""
        self.selected_lottery_type = self.lottery_dropdown.currentText()
        
        # Update the frequency grid for the new lottery type
        self.update_frequency_grid()
        
        # Check and fetch results for the new lottery type
        self.check_and_fetch_results()

    def update_frequency_grid(self):
        """Update the frequency grid based on the current lottery type"""
        # Clear the existing grid
        if hasattr(self, 'freq_grid') and self.freq_grid:
            # Remove all widgets from the grid
            while self.freq_grid.count():
                item = self.freq_grid.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
        # Clear the number_labels dictionary
        self.number_labels = {}
        
        # Get the lottery type and its range
        lottery_type = self.selected_lottery_type
        min_num, max_num = LOTTERY_CONFIG[lottery_type]
        
        # Create number boxes for the grid
        cols = 10  # Number of columns in the grid
        for num in range(min_num, max_num + 1):
            row = (num - 1) // cols
            col = (num - 1) % cols
            
            # Create a box for each number
            box = QFrame()
            box.setFixedSize(60, 60)
            box.setStyleSheet("""
                QFrame {
                    background-color: rgba(55, 55, 150, 0.5);
                    border-radius: 10px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
            """)
            
            # Create layout for the box
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(5, 5, 5, 5)
            box_layout.setSpacing(2)
            
            # Number label
            num_label = QLabel(str(num))
            num_label.setAlignment(Qt.AlignCenter)
            num_label.setFont(QFont("Roboto", 16, QFont.Bold))
            num_label.setStyleSheet("color: white; background-color: transparent; border: none;")
            
            # Frequency label
            freq_label = QLabel("0")
            freq_label.setAlignment(Qt.AlignCenter)
            freq_label.setFont(QFont("Roboto", 12))
            freq_label.setStyleSheet("color: white; background-color: transparent; border: none;")
            
            # Add labels to box
            box_layout.addWidget(num_label)
            box_layout.addWidget(freq_label)
            
            # Add box to grid
            self.freq_grid.addWidget(box, row, col)
            
            # Store reference to the box and frequency label
            self.number_labels[num] = (box, freq_label)

    # Connected to GENERATE Button
    def generate_lucky_numbers(self):
        # Disable the generate button while processing
        self.generate_button.setEnabled(False)
        self.generate_button.setText("GENERATING...")

        # Get selected lottery type
        lottery_type = self.lottery_dropdown.currentText()
        min_num, max_num = LOTTERY_CONFIG[lottery_type]

        # Generate all valid combinations
        all_combinations = list(combinations(range(min_num, max_num + 1), 6))

        # Randomly select 1000 unique combinations
        sampled_combinations = random.sample(all_combinations, 1000)

        # Count frequency of each number in the 1000 combinations
        number_counter = Counter(num for comb in sampled_combinations for num in comb)

        # Pick top 6 most frequent numbers
        top_6 = [str(num).zfill(2) for num, _ in number_counter.most_common(6)]
        
        # Store the lucky numbers
        self.lucky_numbers = top_6

        # Shuffle image indices for visual randomness (1–6)
        ball_indices = list(range(1, 7))
        random.shuffle(ball_indices)

        # Update the 6 BallWidgets
        for i, (widget, num_str) in enumerate(zip(self.lottery_balls, top_6)):
            widget.update_number(num_str, ball_indices[i])

        # Make sure the frequency grid is updated for the current lottery type
        if lottery_type != self.selected_lottery_type:
            self.selected_lottery_type = lottery_type
            self.update_frequency_grid()

        self.update_lucky_label()

        # Update the frequency display with the number counter
        self.update_frequency_display(number_counter)
        self.add_history(self.history_table, lottery_type, top_6)

        # Re-enable the button
        self.generate_button.setEnabled(True)
        self.generate_button.setText("GENERATE")
    
    # Connected to Save Data Button
    def save_data(self):
        """Export data to CSV"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv)")
        if file_path:
            try:
                # Collect numbers from the ball widgets and ensure they're clean
                numbers = [ball.number.replace("`", "") for ball in self.lottery_balls]
                
                # Create a frequency data structure from the number_labels
                frequency_data = []
                for num, (_, freq_label) in sorted(self.number_labels.items()):
                    frequency = freq_label.text().replace("`", "")
                    frequency_data.append((str(num), frequency))
                
                # Check if recent_results_table exists, if not create an empty one
                if not hasattr(self, 'recent_results_table'):
                    self.recent_results_table = QTableWidget()
                    self.recent_results_table.setColumnCount(7)
                    self.recent_results_table.setHorizontalHeaderLabels(["Date", "1", "2", "3", "4", "5", "6"])
                
                # Check if history_table exists, if not create an empty one
                if not hasattr(self, 'history_table'):
                    self.history_table = QTableWidget()
                    self.history_table.setColumnCount(7)
                    self.history_table.setHorizontalHeaderLabels(["Lotto Type", "1", "2", "3", "4", "5", "6"])
                
                success = export_data_to_csv(
                    file_path,
                    f"Lucky Numbers: {'-'.join(numbers)}",
                    frequency_data,  # Pass the frequency data instead of freq_table
                    None,  # No combinations table in new UI (set to None)
                    self.recent_results_table,
                    self.history_table  # Internal QTableWidget used for history
                )

                if success:
                    QMessageBox.information(self, "Success", "Data exported successfully!")
                return success
            except Exception as e:
                # Show error message with details
                QMessageBox.warning(self, "Error Saving Data", 
                                f"An error occurred while saving data:\n{str(e)}")
                return False
        return False

    # Warning popup box for errors
    def warning(self, warning):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(warning)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec()
