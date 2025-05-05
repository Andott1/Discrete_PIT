import sys
import os
import glob
import itertools
import random
import requests
import csv
from datetime import datetime
from collections import Counter
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox, QDateEdit,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidgetItem, QTableWidget, QAbstractItemView,
                             QFrame, QSizePolicy, QStackedWidget, QTextEdit, QDesktopWidget, QSpacerItem, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve, QDate, pyqtSignal, QThread
from PyQt5.QtGui import QPalette, QColor, QFont, QFontDatabase, QBrush, QPainter, QPainterPath, QIcon, QPixmap, QCursor

# Lottery configurations from config.py
LOTTERY_CONFIG = {
    "Ultra Lotto 6/58": (1, 58), 
    "Grand Lotto 6/55": (1, 55), 
    "Superlotto 6/49": (1, 49), 
    "Megalotto 6/45": (1, 45), 
    "Lotto 6/42": (1, 42)
}

MONTH_MAP = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December"
}

LOTTERY_TYPE_MAP = {
    "All Games": "0",
    "Ultra Lotto 6/58": "18",
    "Grand Lotto 6/55": "17",
    "Super Lotto 6/49": "1",
    "Mega Lotto 6/45": "2",
    "Lotto 6/42": "13",
}

def fetch_latest_winning_numbers(lottery_type, from_date, to_date):
    base_url = "https://www.pcso.gov.ph/SearchLottoResult.aspx"

    start_month, start_day, start_year = from_date.split('/')
    end_month, end_day, end_year = to_date.split('/')

    start_day = str(int(start_day))  
    start_year = str(int(start_year))  
    end_day = str(int(end_day))  
    end_year = str(int(end_year))  

    start_month_name = MONTH_MAP[start_month]
    end_month_name = MONTH_MAP[end_month]

    lottery_type_int = LOTTERY_TYPE_MAP.get(lottery_type, "0")

    session = requests.Session()
    response = session.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract hidden form fields
    viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]
    eventvalidation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]
    viewstategenerator = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
    event_target = soup.find("input", {"name": "__EVENTTARGET"})
    event_argument = soup.find("input", {"name": "__EVENTARGUMENT"})

    # Define POST payload (data from the website)
    payload = {
        "__EVENTTARGET": event_target,
        "__EVENTARGUMENT": event_argument,
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategenerator,
        "__EVENTVALIDATION": eventvalidation,
        "ctl00$ctl00$cphContainer$cpContent$ddlStartMonth": start_month_name,
        "ctl00$ctl00$cphContainer$cpContent$ddlStartDate": start_day,
        "ctl00$ctl00$cphContainer$cpContent$ddlStartYear": start_year,
        "ctl00$ctl00$cphContainer$cpContent$ddlEndMonth": end_month_name,
        "ctl00$ctl00$cphContainer$cpContent$ddlEndDay": end_day,
        "ctl00$ctl00$cphContainer$cpContent$ddlEndYear": end_year,
        "ctl00$ctl00$cphContainer$cpContent$ddlSelectGame": lottery_type_int,
        "ctl00$ctl00$cphContainer$cpContent$btnSearch": "Search Lotto"
    }

    # Simulate a browser request (important for some sites)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    session.cookies.update(response.cookies)

    try:
        response = session.post(base_url, data=payload, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")

        results = []
        if not table:
            return []

        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 4:
                continue

            draw_date = cols[2].get_text(strip=True)
            game_type = cols[0].get_text(strip=True)
            if lottery_type in game_type:
                winning_numbers = [num.zfill(2) for num in cols[1].get_text(strip=True).split('-') if num.isdigit()]
                if winning_numbers:
                    results.append((draw_date, winning_numbers))

                if len(results) >= 15:
                    break

    except requests.RequestException as e:
        print(f"Error fetching results: {e}")
        return []

    return results

class FetchResultsThread(QThread):
    results_fetched = pyqtSignal(list)
    
    def __init__(self, lottery_type, lucky_numbers, from_date, to_date):
        super().__init__()
        self.lottery_type = lottery_type
        self.lucky_numbers = lucky_numbers
        self.from_date = from_date
        self.to_date = to_date
    
    def run(self):
        try:
            recent_results = fetch_latest_winning_numbers(self.lottery_type, self.from_date, self.to_date)
            table_data = []
            for draw_date, res in recent_results:
                row = [draw_date] + res  # Use draw date as label
                table_data.append(row)
        except Exception as e:
            table_data = []
        self.results_fetched.emit(table_data)

def export_data_to_csv(file_path, lucky_numbers, frequency_table, combinations_table, recent_results_table, history_table):
        """Export all data to a CSV file"""
        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)
            
            writer.writerow(["Lucky Numbers:", lucky_numbers])
            writer.writerow([])
            
            writer.writerow(["Frequency Table:"])
            writer.writerow(["Number", "Frequency"])
            for row in range(frequency_table.rowCount()):
                writer.writerow([
                    frequency_table.item(row, 0).text(),
                    frequency_table.item(row, 1).text()
                ])
            writer.writerow([])

            if combinations_table:
                writer.writerow(["Random 1000 Combinations:"])
                writer.writerow(["Combination #", "Num1", "Num2", "Num3", "Num4", "Num5", "Num6"])
                for row in range(combinations_table.rowCount()):
                    writer.writerow([
                        combinations_table.item(row, col).text()
                        for col in range(combinations_table.columnCount())
                    ])
                writer.writerow([])
            
            writer.writerow(["Recent Results:"])
            writer.writerow(["Draw", "1", "2", "3", "4", "5", "6"])
            for row in range(recent_results_table.rowCount()):
                writer.writerow([
                    recent_results_table.item(row, col).text()
                    for col in range(recent_results_table.columnCount())
                ])
            writer.writerow([])

            writer.writerow(["Lucky Numbers History:"])
            writer.writerow(["Lotto Type", "1", "2", "3", "4", "5", "6"])
            for row in range(history_table.rowCount()):
                writer.writerow([
                    history_table.item(row, col).text()
                    for col in range(history_table.columnCount())
                ])
                
        return True

# -----------------------------------------------
# Resource Manager and Finder
# -----------------------------------------------

class AssetManager:
    def __init__(self):
        """
        Initialize the AssetManager with proper path resolution for both development
        and PyInstaller bundled environments.
        """
        # Base directories to check for assets
        self.asset_dirs = [
            "Assets/App Screenshots",
            "Assets/Fonts",
            "Assets/Icons",
            "Assets/Screens",
        ]
        
        # Map to cache resolved asset paths
        self.asset_cache = {}
        
        # Print the base directory for debugging
        print(f"Base directory: {self.get_base_dir()}")
        
        # Pre-scan assets to populate cache
        self.scan_assets()
    
    def get_base_dir(self):
        """
            the base directory for assets, handling both development and PyInstaller environments.
        """
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Running in PyInstaller bundle
            return sys._MEIPASS
        else:
        # When running normally (like python main.py)
            return os.path.dirname(os.path.abspath(__file__))
    
    def scan_assets(self):
        """
        Scan all asset directories and populate the asset cache.
        """
        base_dir = self.get_base_dir()
        print(f"Scanning assets in: {base_dir}")
        
        # Scan each asset directory
        for asset_dir in self.asset_dirs:
            full_dir_path = os.path.join(base_dir, asset_dir)
            
            if os.path.exists(full_dir_path):
                print(f"Found asset directory: {full_dir_path}")
                
                # Scan all files in this directory and subdirectories
                for root, _, files in os.walk(full_dir_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        # Get the relative path from the base directory
                        rel_path = os.path.relpath(full_path, base_dir)
                        # Store in cache with normalized path
                        normalized_path = rel_path.replace('\\', '/')
                        self.asset_cache[normalized_path] = full_path
                        
                        # Also store with simplified path (for robustness)
                        simple_path = os.path.join(asset_dir, file).replace('\\', '/')
                        self.asset_cache[simple_path] = full_path
                        
                        print(f"Cached asset: {normalized_path} -> {full_path}")
            else:
                print(f"Asset directory not found: {full_dir_path}")
        
        print(f"Total assets cached: {len(self.asset_cache)}")
        
        # Try to find assets with recursive glob pattern (fallback method)
        self.find_assets_with_glob()
    
    def find_assets_with_glob(self):
        """
        Use glob to find assets recursively as a fallback method.
        """
        base_dir = self.get_base_dir()
        
        # Search for all files in the Assets directory
        for pattern in ["Assets/**/*.*", "Assets/*.*"]:
            for file_path in glob.glob(os.path.join(base_dir, pattern), recursive=True):
                if os.path.isfile(file_path):
                    # Get filename
                    filename = os.path.basename(file_path)
                    # Add to cache with just the filename as key (most permissive)
                    self.asset_cache[filename] = file_path
                    
                    # Also add with partial path
                    rel_path = os.path.relpath(file_path, base_dir)
                    self.asset_cache[rel_path.replace('\\', '/')] = file_path
    
    def resolve_asset(self, asset_path):
        """
        Resolve an asset path to its full path, handling both development and PyInstaller environments.
        
        Args:
            asset_path (str): The relative path to the asset (e.g., "Assets/Fonts/Roboto.ttf")
            
        Returns:
            str: The full path to the asset, or None if not found
        """
        # Normalize the path
        normalized_path = asset_path.replace('\\', '/')
        
        # Check if the asset is in the cache
        if normalized_path in self.asset_cache:
            return self.asset_cache[normalized_path]
        
        # Try with just the filename
        filename = os.path.basename(normalized_path)
        if filename in self.asset_cache:
            return self.asset_cache[filename]
        
        # If not in cache, try direct resolution
        base_dir = self.get_base_dir()
        full_path = os.path.join(base_dir, normalized_path)
        
        if os.path.exists(full_path):
            # Add to cache for future lookups
            self.asset_cache[normalized_path] = full_path
            return full_path
        
        # Try to find the file by searching all subdirectories
        for root, _, files in os.walk(base_dir):
            if filename in files:
                full_path = os.path.join(root, filename)
                self.asset_cache[normalized_path] = full_path
                return full_path
        
        # Asset not found
        print(f"Asset not found: {asset_path}")
        return None
    
    def load_asset(self, asset_path):
        """
        Resolve and return the full path to an asset.
        
        Args:
            asset_path (str): The relative path to the asset
            
        Returns:
            str: The full path to the asset, or None if not found
        """
        return self.resolve_asset(asset_path)
    
    def load_pixmap(self, image_path):
        """
        Load an image as a QPixmap, with robust error handling.
        
        Args:
            image_path (str): The relative path to the image
            
        Returns:
            QPixmap: The loaded pixmap, or an empty pixmap if loading failed
        """
        resolved_path = self.resolve_asset(image_path)
        if not resolved_path:
            print(f"Image not found: {image_path}")
            return QPixmap()
        
        pixmap = QPixmap(resolved_path)
        if pixmap.isNull():
            print(f"Failed to load image as pixmap: {resolved_path}")
            
            # Try alternative paths
            filename = os.path.basename(image_path)
            for key, path in self.asset_cache.items():
                if filename in key and key != image_path:
                    print(f"Trying alternative path: {path}")
                    alt_pixmap = QPixmap(path)
                    if not alt_pixmap.isNull():
                        return alt_pixmap
            
            return QPixmap()
        
        return pixmap
    
    def load_fonts(self):
        """
        Load all fonts in the Fonts directory.
        
        Returns:
            list: A list of loaded font family names
        """
        loaded_families = []
        font_dir = os.path.join(self.get_base_dir(), "Assets", "Fonts")
        
        if not os.path.exists(font_dir):
            print(f"Font directory not found: {font_dir}")
            # Try to find fonts using the asset cache
            for key, path in self.asset_cache.items():
                if "Fonts" in key and path.lower().endswith(('.ttf', '.otf')):
                    font_id = QFontDatabase.addApplicationFont(path)
                    if font_id != -1:
                        families = QFontDatabase.applicationFontFamilies(font_id)
                        print(f"Loaded font: {path} → {families}")
                        loaded_families.extend(families)
                    else:
                        print(f"Failed to load font: {path}")
            
            return loaded_families
        
        print(f"Loading fonts from: {font_dir}")
        
        # Find all font files
        font_files = []
        for ext in ['.ttf', '.otf']:
            font_files.extend(glob.glob(os.path.join(font_dir, f"**/*{ext}"), recursive=True))
        
        # Load each font
        for font_path in font_files:
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                print(f"Loaded font: {font_path} → {families}")
                loaded_families.extend(families)
            else:
                print(f"Failed to load font: {font_path}")
        
        return loaded_families
    
    def get_font_dir(self):
        """
        Get the directory containing fonts.
        
        Returns:
            str: The full path to the fonts directory, or None if not found
        """
        font_dir = "Assets/Fonts"
        resolved = self.resolve_asset(font_dir)
        if resolved:
            return os.path.dirname(resolved)
        
        # Fallback: try to find any font file and return its directory
        for key, path in self.asset_cache.items():
            if "Fonts" in key and os.path.exists(path):
                return os.path.dirname(path)
        
        # Last resort: return the base Assets directory
        return os.path.join(self.get_base_dir(), "Assets")

# Create a singleton instance
asset_manager = AssetManager()
    
# -----------------------------------------------
# Custom Widgets
# -----------------------------------------------

class RoundedWidget(QWidget):
    def __init__(self, parent=None, radius=20, bg_color="#FFFFFF"):
        super().__init__(parent)
        self.radius = radius
        self.bg_color = bg_color
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)
        
        painter.setClipPath(path)
        painter.fillPath(path, QBrush(QColor(self.bg_color)))


class CircleButtonBack(QPushButton):
    def __init__(self, parent=None, on_back_pressed=None):
        super().__init__(parent)
        self.setFixedSize(50, 50)

        icon_path = asset_manager.load_asset("Assets/Icons/back_icon.png")
        icon = QIcon(icon_path)
        if icon.isNull():
            print(f"Failed to load icon: {icon_path}")
        else:
            self.setIcon(icon)

        icon_size = self.size() * 0.5
        self.setIconSize(icon_size)

        self.setStyleSheet("""
            QPushButton {
                background-color: #9191DC;
                border-radius: 25px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7777B2;
            }
            QPushButton:pressed {
                background-color: #55557D;
            }
        """)

        if on_back_pressed:
            self.clicked.connect(on_back_pressed)

class CircleButtonInfo(QPushButton):
    def __init__(self, parent=None, on_info_pressed=None):
        super().__init__(parent)
        self.setFixedSize(50, 50)
        
        icon_path = asset_manager.load_asset("Assets/Icons/group_icon.png")  # Ensure this points to the correct image path
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
                background-color: #9191DC;
                border-radius: 25px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7777B2;
            }
            QPushButton:pressed {
                background-color: #55557D;
            }
        """)

        if on_info_pressed:
            self.clicked.connect(on_info_pressed)

# -----------------------------------------------
# Main Application
# -----------------------------------------------

class LotteryBall(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize instance variables
        self.lottery_balls = []
        self.lucky_numbers = []
        self.selected_lottery_type = "Lotto 6/42"  # Default lottery type
        
        self.initUI()
        icon_path = asset_manager.load_asset("Assets/Icons/app_icon.ico")
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
        outer_container = RoundedWidget(radius=30, bg_color=QColor(255, 255, 255, 250))
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
        
        self.set_image_background(asset_manager.load_asset("Assets/Screens/main_screen.png"))

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
        self.back_button = CircleButtonBack(on_back_pressed=self.back_to_splash)
        top_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        # Title section
        title_widget = QWidget()
        title_widget.setStyleSheet("background-color: rgba(200, 200, 200, 0); border-radius: 10px;")
        title_layout = QVBoxLayout(title_widget)
        title_layout.setAlignment(Qt.AlignVCenter)
        
        title_label = QLabel("LET\'S PLAY LOTTO")
        title_label.setFont(QFont("Roboto Condensed", 24, QFont.ExtraBold))
        title_label.setStyleSheet("color: #55557D;")  # Replace with your desired color
        title_label.setAlignment(Qt.AlignLeft)
        title_layout.addWidget(title_label)
        top_layout.addWidget(title_widget, 1)

        # DateTime section
        datetime_widget = self.create_datetime_section()
        top_layout.addWidget(datetime_widget, alignment=Qt.AlignRight)

        # Info button (circle)
        self.info_button = CircleButtonInfo(on_info_pressed=self.show_info_dialog)
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
        self.datetime_label.setStyleSheet("color: #55557D;")
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
        left_panel.setStyleSheet("background-color: rgba(145, 145, 220, 0.25); border-radius: 20px;")
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.setSpacing(25)
        left_layout.setContentsMargins(15, 15, 15, 15)

        control_panel = self.create_control_panel()
        control_panel.setStyleSheet("background-color: rgba(145, 145, 220, 0.9); border-radius: 20px;")
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
        lottery_game_label.setStyleSheet("color: #55557D; background-color: rgba(145, 145, 220, 0)")
        control_layout.addWidget(lottery_game_label)
        
        lottery_options = ["Lotto 6/42", "Megalotto 6/45", "Superlotto 6/49", "Grand Lotto 6/55", "Ultra Lotto 6/58"]
        self.lottery_dropdown = self.create_dropdown_field(lottery_options)
        self.lottery_dropdown.currentIndexChanged.connect(self.on_lottery_selection_changed)
        control_layout.addWidget(self.lottery_dropdown)

        control_layout.addSpacing(15)

        # Results Date
        date_range_label = QLabel("  Set Results Date")
        date_range_label.setFont(QFont("Roboto", 18, QFont.Bold))
        date_range_label.setStyleSheet("color: #55557D; background-color: rgba(145, 145, 220, 0)")
        control_layout.addWidget(date_range_label)

        # From Date
        from_layout = QHBoxLayout()
        from_label = QLabel("From:")
        from_label.setStyleSheet("color: white; font-size: 14px;")
        from_layout.addWidget(from_label)

        self.from_date_edit = QDateEdit()
        self.from_date_edit.setCalendarPopup(True)
        self.from_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.from_date_edit.setStyleSheet("""
            QDateEdit {
                border-radius: 10px;
                padding: 8px 12px;
                background-color: rgba(145, 145, 220, 0.25);
                font-family: 'Roboto Medium';
                font-size: 16px;
                color: #55557D;
            }

            QDateEdit:focus {
                border: 2px solid #7777B2;
                background-color: rgba(145, 145, 220, 0.15);
            }

            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid #7777B2;
            }

            QDateEdit::down-arrow {
                width: 16px;
                height: 16px;
            }
        """)
        from_layout.addWidget(self.from_date_edit)
        control_layout.addLayout(from_layout)

        # To date
        to_layout = QHBoxLayout()
        to_label = QLabel("To:")
        to_label.setStyleSheet("color: white; font-size: 14px;")
        to_layout.addWidget(to_label)

        self.to_date_edit = QDateEdit()
        self.to_date_edit.setCalendarPopup(True)
        self.to_date_edit.setDate(QDate.currentDate())
        self.to_date_edit.setStyleSheet("""
            QDateEdit {
                border-radius: 10px;
                padding: 8px 12px;
                background-color: rgba(145, 145, 220, 0.25);
                font-family: 'Roboto Medium';
                font-size: 16px;
                color: #55557D;
            }

            QDateEdit:focus {
                border: 2px solid #7777B2;
                background-color: rgba(145, 145, 220, 0.15);
            }

            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid #7777B2;
            }

            QDateEdit::down-arrow {
                width: 16px;
                height: 16px;
            }
        """)
        to_layout.addWidget(self.to_date_edit)
        control_layout.addLayout(to_layout)

        # Add button to fetch results
        fetch_button = QPushButton("Fetch Results")
        fetch_button.setStyleSheet("""
            QPushButton {
                background-color: #7777B2;
                color: white;
                border-radius: 10px;
                padding: 8px;
                font-family: 'Roboto';
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #55557D;
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
                background-color: rgba(145, 145, 220, 0.25); /* Actual line color */
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

    def create_dropdown_field(self, items):  # Styled dropdown (QComboBox)
        combo_box = QComboBox()
        combo_box.addItems(items)
        combo_box.setStyleSheet("""
            QComboBox {
                border-radius: 10px;
                padding: 10px;
                background-color: rgba(145, 145, 220, 0.25);
                font-family: 'Roboto Medium';
                font-size: 16px;
                color: #7777B2;
            }

            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: #7777B2;
                font-family: 'Roboto';
                font-size: 16px;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: #7777B2;
                border-left-style: solid;
            }
        """)
        combo_box.setMinimumHeight(40)
        return combo_box
    
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
                background-color: #9191DC;
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
        right_panel.setStyleSheet("background-color: rgba(145, 145, 220, 0.25); border-radius: 10px;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)

        # Top bar with Prev | Tab Title | Next
        top_bar = QHBoxLayout()

        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        for btn in (self.prev_button, self.next_button):
            btn.setFixedHeight(30)
            btn.setStyleSheet("background-color: #7777B2; color: white; border-radius: 6px; padding: 5px 10px;")

        self.tab_title_label = QLabel("Lucky Numbers")
        self.tab_title_label.setAlignment(Qt.AlignCenter)
        self.tab_title_label.setFont(QFont("Roboto", 16, QFont.Bold))
        self.tab_title_label.setStyleSheet("color: #55557D;")

        top_bar.addWidget(self.prev_button)
        top_bar.addStretch()
        top_bar.addWidget(self.tab_title_label)
        top_bar.addStretch()
        top_bar.addWidget(self.next_button)

        right_layout.addLayout(top_bar)

        # Stack for tabs
        self.stacked_widget = self.create_stacked_widget()
        right_layout.addWidget(self.stacked_widget)

        # Button logic
        self.tab_titles = [
            "Lucky Numbers",
            "See More Details",
            "Recent Lottery Results",
            "History of Generated Lucky Numbers"
        ]
        self.current_tab_index = 0
        self.prev_button.clicked.connect(self.show_previous_tab)
        self.next_button.clicked.connect(self.show_next_tab)
        
        return right_panel
    
    def create_stacked_widget(self):
        self.stacked_widget = QStackedWidget()

        # --------- Tab 1: Lucky Numbers ----------
        lucky_tab = QWidget()
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
        default_numbers = ["01", "02", "03", "04", "05", "06"]  # placeholder values

        for i in range(6):
            ball = BallWidget(default_numbers[i], ball_indices[i])
            self.lottery_balls.append(ball)
            if i < 3:
                self.first_row_layout.addWidget(ball)
            else:
                self.second_row_layout.addWidget(ball)

        lucky_label = QLabel("IS YOUR LUCKY COMBINATION")
        lucky_label.setAlignment(Qt.AlignCenter)
        lucky_label.setFont(QFont("Roboto", 14, QFont.Bold))
        lucky_label.setStyleSheet("color: #333366;")
        lucky_layout.addWidget(lucky_label)

        self.stacked_widget.addWidget(lucky_tab)

        # --------- Tab 2: See More Details (Frequency Table) ----------
        freq_tab = QWidget()
        freq_layout = QVBoxLayout(freq_tab)

        # Create a QTableWidget to hold the frequency data
        self.freq_table = QTableWidget()
        self.freq_table.setColumnCount(2)  # 2 columns: Number and Frequency
        self.freq_table.setHorizontalHeaderLabels(["Number", "Frequency"])
        self.freq_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.freq_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.freq_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 0.1);
                color: #333366;
                font-size: 14px;
                border-radius: 10px;
            }
            QHeaderView::section {
                background-color: #55557D;
                color: white;
                font-weight: bold;
                padding: 4px;
            }
        """)

        # Add the frequency table to the layout
        freq_layout.addWidget(self.freq_table)

        # Add the Tab to the stacked widget
        self.stacked_widget.addWidget(freq_tab)

        # --------- Tab 3: Recent Lottery Results ----------
        recent_tab = QWidget()
        recent_layout = QVBoxLayout(recent_tab)

        # Table setup
        self.recent_results_table = QTableWidget()
        self.recent_results_table.setColumnCount(7)  # Adjust as needed
        self.recent_results_table.setHorizontalHeaderLabels(["Date", "1", "2", "3", "4", "5", "6"])
        self.recent_results_table.horizontalHeader().setStretchLastSection(True)
        self.recent_results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.recent_results_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.recent_results_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 0.1);
                color: #333366;
                font-size: 14px;
                border-radius: 10px;
            }
            QHeaderView::section {
                background-color: #55557D;
                color: white;
                font-weight: bold;
                padding: 4px;
            }
        """)
        recent_layout.addWidget(self.recent_results_table)

        self.stacked_widget.addWidget(recent_tab)

        # --------- Tab 4: History of Lucky Numbers ----------
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels(["Lotto Type", "1", "2", "3", "4", "5", "6"])
        self.history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.history_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 0.1);
                color: #333366;
                font-size: 14px;
                border-radius: 10px;
            }
            QHeaderView::section {
                background-color: #55557D;
                color: white;
                font-weight: bold;
                padding: 4px;
            }
        """)
        history_layout.addWidget(self.history_table)

        self.stacked_widget.addWidget(history_tab)

        return self.stacked_widget
    
    def add_history(self, table, lottery_type, lucky_numbers, mirror_table=None):
        """Add a new entry to the history table and optionally mirror it"""
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

    def show_next_tab(self):
        if self.current_tab_index < len(self.tab_titles) - 1:
            self.current_tab_index += 1
            self.stacked_widget.setCurrentIndex(self.current_tab_index)
            self.tab_title_label.setText(self.tab_titles[self.current_tab_index])

    def show_previous_tab(self):
        if self.current_tab_index > 0:
            self.current_tab_index -= 1
            self.stacked_widget.setCurrentIndex(self.current_tab_index)
            self.tab_title_label.setText(self.tab_titles[self.current_tab_index])

    def update_datetime(self):  # Date time update realtime
        current_time = datetime.now().strftime("%A, %B %d, %Y - %I:%M:%S %p")
        self.datetime_label.setText(current_time)
    
    def back_to_splash(self):   # Back button logic
        self.close()
        self.splash = SplashScreen()
        self.splash.show()

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
            <span style="font-size: 16px; font-weight: regular; color: #333;">5. Yasser Tomawis</span>
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
        # Clear previous results before displaying new ones
        self.recent_results_table.setRowCount(0)

        self.recent_results_table.setRowCount(len(recent_results))
        for i, row_data in enumerate(recent_results):
            for j, item in enumerate(row_data):
                self.recent_results_table.setItem(i, j, QTableWidgetItem(str(item)))

    # --------- Functions related to populating the frequency table ---------

    def populate_table(self, table, number_counter):
        """Populate the frequency table with data"""
        table.setRowCount(len(number_counter))
        for i, (num, freq) in enumerate(number_counter.most_common()):
            table.setItem(i, 0, QTableWidgetItem(str(num)))
            table.setItem(i, 1, QTableWidgetItem(str(freq)))

    # Connected to GENERATE Button
    def generate_lucky_numbers(self):
        # Disable the generate button while processing
        self.generate_button.setEnabled(False)
        self.generate_button.setText("GENERATING...")

        # Get selected lottery type
        lottery_type = self.lottery_dropdown.currentText()
        min_num, max_num = LOTTERY_CONFIG[lottery_type]

        # Generate random combinations and pick top 6 numbers
        sampled_combinations = {tuple(sorted(random.sample(range(min_num, max_num + 1), 6))) for _ in range(2000)}
        sampled_combinations = list(sampled_combinations)[:1000]
        number_counter = Counter(num for comb in sampled_combinations for num in comb)
        top_6 = [str(num).zfill(2) for num, _ in number_counter.most_common(6)]
        
        # Store the lucky numbers
        self.lucky_numbers = top_6

        # Shuffle image indices for visual randomness (1–6)
        ball_indices = list(range(1, 7))
        random.shuffle(ball_indices)

        # Update the 6 BallWidgets
        for i, (widget, num_str) in enumerate(zip(self.lottery_balls, top_6)):
            widget.update_number(num_str, ball_indices[i])

        # Update the frequency table with the number counter
        self.populate_table(self.freq_table, number_counter)
        self.add_history(self.history_table, lottery_type, top_6)

        # Re-enable the button
        self.generate_button.setEnabled(True)
        self.generate_button.setText("GENERATE")
    
    # Connected to Save Data Button
    def save_data(self):
        """Export data to CSV"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv)")
        if file_path:
            # Collect numbers from the ball widgets
            numbers = [ball.number for ball in self.lottery_balls]
            
            success = export_data_to_csv(
                file_path,
                f"Lucky Numbers: {'-'.join(numbers)}",
                self.freq_table,
                None,  # No combinations table in new UI (set to None)
                self.recent_results_table,
                self.history_table  # Internal QTableWidget used for history
            )

            if success:
                QMessageBox.information(self, "Success", "Data exported successfully!")
            return success
        return False

    # Warning popup box for errors
    def warning(self, warning):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(warning)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec()


class BallWidget(QLabel):
    def __init__(self, number, ball_index, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 100)
        self.setAlignment(Qt.AlignCenter)

        self.number = number
        self.ball_index = ball_index
        self.pixmap = None

        self.load_ball_image()

    def load_ball_image(self):
        image_path = f"Assets/Icons/lottery_ball_{self.ball_index}.png"
        self.pixmap = asset_manager.load_pixmap(image_path)

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


# Splash screen logic
class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.load_custom_font()
        icon_path = asset_manager.load_asset("Assets/Icons/app_icon.ico")
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Welcome to Let's Play Lotto")
        self.setWindowFlag(Qt.FramelessWindowHint)

        # Center and scale window to percent of screen
        screen_geometry = QDesktopWidget().screenGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        window_width = int(screen_width * 0.55)
        window_height = int(screen_height * 0.6)

        self.setFixedSize(window_width, window_height)

        # Load and scale splash image
        splash_path = asset_manager.load_asset("Assets/Screens/splash_screen.png")
        splash_image = QPixmap(splash_path)

        if splash_image.isNull():
            print(f"Failed to load image: {splash_path}")
        else:
            print("Splash screen image loaded successfully.")

        scaled_image = splash_image.scaled(window_width, window_height, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        # Image label (background)
        self.image_label = QLabel(self)
        self.image_label.setPixmap(scaled_image)
        self.image_label.setGeometry(0, 0, window_width, window_height)
        self.image_label.setScaledContents(True)

        # Overlay layout on top of image
        overlay_layout = QVBoxLayout(self)
        overlay_layout.setContentsMargins(20, 20, 20, 50)
        overlay_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Start button
        self.start_button = QPushButton("Start Generating", self)
        button_width = int(screen_width * 0.125)
        button_height = int(screen_height * 0.075)
        self.start_button.setFixedSize(button_width, button_height)
        self.start_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.start_button.setVisible(False)
        self.start_button.clicked.connect(self.launch_main)

        # Button styling
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(145, 145, 220, 0.5);
                color: #FFFFFF;
                border-radius: 20px;
                padding: 10px;
                font-family: 'Roboto ExtraBold';
                font-size: 20px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: rgba(145, 145, 220, 0.75);
                color: #55557D;
            }
            QPushButton:pressed {
                background-color: #7777B2;
            }
        """)

        overlay_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        self.setLayout(overlay_layout)

        QTimer.singleShot(1000, self.animate_button)


    # Loads custom font in Assets/Fonts folder
    def load_custom_font(self):
        font_dir = asset_manager.get_font_dir()
        if not font_dir or not os.path.exists(font_dir):
            print(f"Font directory not found: {font_dir}")
            return

        print(f"Loading fonts from: {font_dir}")
        loaded_families = []

        # Use glob to find all .ttf files recursively
        font_paths = glob.glob(os.path.join(font_dir, '**', '*.ttf'), recursive=True)

        for font_path in font_paths:
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                print(f"Loaded font: {font_path} → {families}")
                loaded_families.extend(families)
            else:
                print(f"Failed to load font: {font_path}")

        if loaded_families:
            font = QFont(loaded_families[0] if loaded_families else "Arial")
            QApplication.setFont(font)
            print(f"Application font set to: {loaded_families[0] if loaded_families else 'Arial'}")
        else:
            print("No fonts were loaded.")

    # Simple button animation
    def animate_button(self):
        self.start_button.setVisible(True)
        self.start_button.update()

        self.anim = QPropertyAnimation(self.start_button, b"geometry")
        self.anim.setDuration(500)
        self.anim.setStartValue(QRect(
            self.start_button.x(),
            self.start_button.y() + 50,
            self.start_button.width(),
            self.start_button.height()
        ))
        self.anim.setEndValue(self.start_button.geometry())
        self.anim.setEasingCurve(QEasingCurve.OutBack)
        self.anim.start()

    # Splash screen show logic
    def launch_main(self):
        self.close()
        self.main = LotteryBall()
        self.main.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    sys.exit(app.exec_())