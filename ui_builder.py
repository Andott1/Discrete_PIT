from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QLabel, 
                            QComboBox, QTableWidget, QDateEdit, QHeaderView)
from PyQt6.QtCore import QDate, Qt, QTimer
from config import LOTTERY_CONFIG
from ui_utils import set_font_style, toggle_collapsible_content

def build_left_panel(parent):
    """Build the left panel of the UI"""
    left_layout = QVBoxLayout()
    left_layout.setContentsMargins(20, 20, 20, 20)

    # Date and time label
    parent.date_time_label = QLabel(parent)
    set_font_style(parent, parent.date_time_label, "style_2")
    left_layout.addWidget(parent.date_time_label)

    # Set up a QTimer to update the time every second
    parent.timer = QTimer(parent)
    parent.timer.timeout.connect(parent.update_time_display)
    parent.timer.start(1000)  # Update every second

    # Lottery type selection
    parent.lottery_selector = QComboBox()
    parent.lottery_selector.addItems(LOTTERY_CONFIG.keys())
    parent.llabel1 = QLabel("Select Lottery Type:")
    set_font_style(parent, parent.llabel1, "style_3")

    left_layout.addWidget(parent.llabel1)
    left_layout.addWidget(parent.lottery_selector)

    # From date
    parent.from_date_edit = QDateEdit()
    parent.from_date_edit.setCalendarPopup(True)
    parent.from_date_edit.setDate(QDate.currentDate().addDays(-28))
    parent.llabel2 = QLabel("From Date:")
    set_font_style(parent, parent.llabel2, "style_4")

    left_layout.addWidget(parent.llabel2)
    left_layout.addWidget(parent.from_date_edit)

    # To date
    parent.to_date_edit = QDateEdit()
    parent.to_date_edit.setCalendarPopup(True)
    parent.to_date_edit.setDate(QDate.currentDate())

    parent.llabel3 = QLabel("To Date:")
    set_font_style(parent, parent.llabel3, "style_4")

    left_layout.addWidget(parent.llabel3)
    left_layout.addWidget(parent.to_date_edit)
    
    # Generate lucky numbers button
    parent.generate_button = QPushButton("Generate Lucky Numbers")
    parent.generate_button.clicked.connect(parent.generate_lucky_numbers)
    left_layout.addWidget(parent.generate_button)
    
    # Lucky Numbers display
    parent.llabel4 = QLabel("Lucky Numbers:")
    set_font_style(parent, parent.llabel4, "style_3")
    parent.llabel4.setAlignment(Qt.AlignmentFlag.AlignCenter)

    left_layout.addWidget(parent.llabel4)

    left_layout.addStretch()

    # Export data button
    parent.export_button = QPushButton("Export Data")
    parent.export_button.clicked.connect(parent.export_data)
    left_layout.addWidget(parent.export_button)
    
    return left_layout

def build_right_panel(parent):
    """Build the right panel of the UI"""
    right_layout = QVBoxLayout()
    right_layout.setContentsMargins(10, 10, 10, 10)
    right_layout.setSpacing(15)
    
    # Generation History table
    parent.tlabel1 = QLabel("Lucky Numbers History:")
    set_font_style(parent, parent.tlabel1, "style_2")
    right_layout.addWidget(parent.tlabel1)
    parent.history_table = QTableWidget(0, 7)
    parent.history_table.setHorizontalHeaderLabels(["Lotto Type", "1", "2", "3", "4", "5", "6"])
    parent.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    right_layout.addWidget(parent.history_table)

    # Recent results table
    parent.tlabel2 = QLabel("Recent Results:")
    set_font_style(parent, parent.tlabel2, "style_2")
    right_layout.addWidget(parent.tlabel2)
    parent.recent_results_table = QTableWidget(0, 7)
    parent.recent_results_table.setHorizontalHeaderLabels(["Draw", "1", "2", "3", "4", "5", "6"])
    parent.recent_results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    right_layout.addWidget(parent.recent_results_table)

    # Collapsible section
    collapsible_group = build_collapsible_section(parent)
    right_layout.addWidget(collapsible_group)
    
    return right_layout

def build_collapsible_section(parent):
    """Build the collapsible 'More Details' section"""
    collapsible_group = QGroupBox("More Details")
    collapsible_group.setCheckable(True)
    collapsible_group.setChecked(False)  # Start collapsed
    collapsible_layout = QVBoxLayout()

    # Frequency table
    parent.tlabel3 = QLabel("Frequency Table:")
    set_font_style(parent, parent.tlabel3, "style_2")
    collapsible_layout.addWidget(parent.tlabel3)
    parent.result_table = QTableWidget(0, 2)
    parent.result_table.setHorizontalHeaderLabels(["Number", "Frequency"])
    parent.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    collapsible_layout.addWidget(parent.result_table)
       
    # Random combinations table
    parent.tlabel4 = QLabel("Randomly Picked 1000 Combinations:")
    set_font_style(parent, parent.tlabel4, "style_2")
    collapsible_layout.addWidget(parent.tlabel4)
    parent.combinations_table = QTableWidget(0, 7)
    parent.combinations_table.setHorizontalHeaderLabels(["Combination #", "Num1", "Num2", "Num3", "Num4", "Num5", "Num6"])
    parent.combinations_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    collapsible_layout.addWidget(parent.combinations_table)
    
    collapsible_group.setLayout(collapsible_layout)
    
    # Connect the toggle signal to our custom function
    collapsible_group.toggled.connect(parent.toggle_details)
    
    return collapsible_group

def setup_main_layout(parent):
    """Set up the main layout of the application"""
    main_layout = QVBoxLayout()
    content_layout = QHBoxLayout()
    
    # Build left and right panels
    left_layout = build_left_panel(parent)
    right_layout = build_right_panel(parent)
    
    # Add panels to content layout
    content_layout.addLayout(left_layout, 1)
    content_layout.addLayout(right_layout, 3)
    
    # Add content layout to main layout
    main_layout.addLayout(content_layout)
    
    # Set the main layout
    parent.setLayout(main_layout)
    parent.setWindowTitle("Lottery Number Analyzer")
    
    # Initialize visibility of collapsible content
    toggle_collapsible_content(parent.result_table, parent.combinations_table, False)