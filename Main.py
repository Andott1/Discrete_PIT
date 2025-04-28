import sys
import itertools
import random
import requests
import csv
from datetime import datetime
from collections import Counter
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import (QApplication, QDateEdit, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QLabel, QComboBox, 
                               QTableWidget, QTableWidgetItem, QFileDialog, QHeaderView, QMessageBox)
from PyQt6.QtCore import QDate, Qt, QThread, pyqtSignal, QTimer, QDateTime
from PyQt6.QtGui import QFont

# Lottery configurations
LOTTERY_CONFIG = {"Ultra Lotto 6/58": (1, 58), "Grand Lotto 6/55": (1, 55), "Superlotto 6/49": (1, 49), "Megalotto 6/45": (1, 45), "Lotto 6/42": (1, 42)}

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

class LotteryAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.resize_and_center()
    
    def init_ui(self):

        main_layout = QVBoxLayout()
        content_layout = QHBoxLayout() 

        left_layout = QVBoxLayout()   # Vertical (for left panel)
        left_layout.setContentsMargins(20, 20, 20, 20)

        # Add a QLabel for showing the current date and time
        self.date_time_label = QLabel(self)
        self.set_font_style(self.date_time_label, "style_2")
        left_layout.addWidget(self.date_time_label)

        # Set up a QTimer to update the time every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second

        # Lottery type selection
        self.lottery_selector = QComboBox()
        self.lottery_selector.addItems(LOTTERY_CONFIG.keys())
        self.llabel1 = QLabel("Select Lottery Type:")
        self.set_font_style(self.llabel1, "style_3")

        left_layout.addWidget(self.llabel1)
        left_layout.addWidget(self.lottery_selector)

        self.from_date_edit = QDateEdit()
        self.from_date_edit.setCalendarPopup(True)
        self.from_date_edit.setDate(QDate.currentDate().addDays(-28))
        self.llabel2 = QLabel("From Date:")
        self.set_font_style(self.llabel2, "style_4")

        left_layout.addWidget(self.llabel2)
        left_layout.addWidget(self.from_date_edit)

        self.to_date_edit = QDateEdit()
        self.to_date_edit.setCalendarPopup(True)
        self.to_date_edit.setDate(QDate.currentDate())

        self.llabel3 = QLabel("To Date:")
        self.set_font_style(self.llabel3, "style_4")

        left_layout.addWidget(self.llabel3)
        left_layout.addWidget(self.to_date_edit)
        
        # Generate lucky numbers button
        self.generate_button = QPushButton("Generate Lucky Numbers")
        self.generate_button.clicked.connect(self.generate_lucky_numbers)
        left_layout.addWidget(self.generate_button)
        
        # Lucky Numbers display
        self.llabel4 = QLabel("Lucky Numbers:")
        self.set_font_style(self.llabel4, "style_3")
        self.llabel4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        left_layout.addWidget(self.llabel4)

        left_layout.addStretch()

        # Export data button
        self.export_button = QPushButton("Export Data")
        self.export_button.clicked.connect(self.export_data)
        left_layout.addWidget(self.export_button)

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(15)
        
        # Generation History table (7 columns: Lotto Type + 6 lucky numbers)
        self.tlabel1 = QLabel("Lucky Numbers History:")
        self.set_font_style(self.tlabel1, "style_2")
        right_layout.addWidget(self.tlabel1)
        self.history_table = QTableWidget(0, 7)
        self.history_table.setHorizontalHeaderLabels(["Lotto Type", "1", "2", "3", "4", "5", "6"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right_layout.addWidget(self.history_table)

        # Recent results table (7 columns: Draw label + 6 winning numbers)
        self.tlabel2 = QLabel("Recent Results:")
        self.set_font_style(self.tlabel2, "style_2")
        right_layout.addWidget(self.tlabel2)
        self.recent_results_table = QTableWidget(0, 7)
        self.recent_results_table.setHorizontalHeaderLabels(["Draw", "1", "2", "3", "4", "5", "6"])
        self.recent_results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right_layout.addWidget(self.recent_results_table)

        collapsible_group = QGroupBox("More Details")
        collapsible_group.setCheckable(True)
        collapsible_group.setChecked(False)  # Start collapsed
        collapsible_layout = QVBoxLayout()

        # Frequency table
        self.tlabel3 = QLabel("Frequency Table:")
        self.set_font_style(self.tlabel3, "style_2")
        collapsible_layout.addWidget(self.tlabel3)
        self.result_table = QTableWidget(0, 2)
        self.result_table.setHorizontalHeaderLabels(["Number", "Frequency"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        collapsible_layout.addWidget(self.result_table)
           
        # Random combinations table (7 columns: Label + 6 numbers)
        self.tlabel4 = QLabel("Randomly Picked 1000 Combinations:")
        self.set_font_style(self.tlabel4, "style_2")
        collapsible_layout.addWidget(self.tlabel4)
        self.combinations_table = QTableWidget(0, 7)
        self.combinations_table.setHorizontalHeaderLabels(["Combination #", "Num1", "Num2", "Num3", "Num4", "Num5", "Num6"])
        self.combinations_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        collapsible_layout.addWidget(self.combinations_table)
        
        collapsible_group.setLayout(collapsible_layout)
        
        collapsible_group.toggled.connect(self.toggle_collapsible_content)

        right_layout.addWidget(collapsible_group)
        
        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 3)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)
        self.setWindowTitle("Lottery Number Analyzer")
        self.toggle_collapsible_content(collapsible_group.isChecked())

    def update_time(self):
        # Get the current date and time
        current_time = QDateTime.currentDateTime()
        
        # Extract the components of the date
        day = current_time.date().day()
        month = current_time.date().toString("MM")  # Get month as a two-digit string (e.g., "04")
        year = current_time.date().year()
        
        # Convert the month using the MONTH_MAP
        month_name = MONTH_MAP.get(month, "")
        
        # Get the time in 12-hour format with AM/PM
        time_str = current_time.toString("hh:mm:ss AP")
        
        # Format the date as "Month Day, Year" (e.g., "April 28, 2025")
        formatted_date = f"{month_name} {day}, {year} - {time_str}"
        
        # Update the label text with the formatted date and time
        self.date_time_label.setText(formatted_date)

    def toggle_collapsible_content(self, checked):
        """Show or hide the contents of the collapsible group."""
        # Show or hide the content based on whether the group is checked
        self.result_table.setVisible(checked)
        self.combinations_table.setVisible(checked)

    def resize_and_center(self):
        screen = QApplication.primaryScreen()
        screen_size = screen.size()

        width = int(screen_size.width() * 0.6)
        height = int(screen_size.height() * 0.75)

        self.resize(width, height)

        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - width) // 2
        y = (screen_geometry.height() - height) // 2
        self.move(x, y)
    
    def generate_lucky_numbers(self):
        # Disable the generate button while processing
        self.generate_button.setEnabled(False)
        self.generate_button.setText("Generating...")

        lottery_type = self.lottery_selector.currentText()
        from_date = self.from_date_edit.date().toString("MM/dd/yyyy")
        to_date = self.to_date_edit.date().toString("MM/dd/yyyy")
        min_num, max_num = LOTTERY_CONFIG[lottery_type]

        # Generate 2000 random combinations and take 1000 unique ones.
        sampled_combinations = {tuple(sorted(random.sample(range(min_num, max_num + 1), 6))) for _ in range(2000)}
        sampled_combinations = list(sampled_combinations)[:1000]

        # Populate the random combinations table with labels
        self.combinations_table.setRowCount(len(sampled_combinations))
        for i, comb in enumerate(sampled_combinations):
            self.combinations_table.setItem(i, 0, QTableWidgetItem(f"Combination {i+1}"))
            for j, num in enumerate(comb):
                self.combinations_table.setItem(i, j+1, QTableWidgetItem(str(num)))

        number_counter = Counter(num for comb in sampled_combinations for num in comb)
        top_6 = [str(num).zfill(2) for num, _ in number_counter.most_common(6)]

        self.llabel4.setText(f"Lucky Numbers:\n\n{'-'.join(top_6)}")
        self.populate_table(number_counter)
        self.fetch_recent_results(lottery_type, top_6, from_date, to_date)
        self.add_history(lottery_type, top_6)

        # Show the lucky numbers in a popup message box
        self.show_lucky_numbers_popup(top_6)

        self.generate_button.setEnabled(True)
        self.generate_button.setText("Generate Lucky Numbers")

    def show_lucky_numbers_popup(self, lucky_numbers):
        # Create a message box
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Generated Lucky Numbers")
        msg_box.setIcon(QMessageBox.Icon.Information)
        
        # Set the message to show the lucky numbers
        lucky_numbers_str = f"The lucky numbers are:\n{'-'.join(lucky_numbers)}"
        msg_box.setText(lucky_numbers_str)

        # Show the message box
        msg_box.exec()

    def resizeEvent(self, event):
        # Update the font size when the window is resized
        self.set_font_style(self.tlabel1, "style_2")
        self.set_font_style(self.tlabel2, "style_2")
        self.set_font_style(self.tlabel3, "style_2")
        self.set_font_style(self.tlabel4, "style_2")
        self.set_font_style(self.llabel1, "style_3")
        self.set_font_style(self.llabel2, "style_4")
        self.set_font_style(self.llabel3, "style_4")
        self.set_font_style(self.llabel4, "style_3")

        
        # Ensure proper updates to the tables or any other widgets if needed
        event.accept()

    def set_font_style(self, label, style):
        # Define font styles
        base_font_size = self.width() // 80  # Dynamically adjust font size based on window width

        font_style_1 = QFont("Roboto", base_font_size, QFont.Weight.Normal)
        font_style_2 = QFont("Roboto", base_font_size + 2, QFont.Weight.Bold)
        font_style_3 = QFont("Roboto", base_font_size - 1, QFont.Weight.Bold)
        font_style_4 = QFont("Roboto", base_font_size - 2, QFont.Weight.Bold)

        # Apply the selected font style to the label
        if style == "style_1":
            label.setFont(font_style_1)
        elif style == "style_2":
            label.setFont(font_style_2)
        elif style == "style_3":
            label.setFont(font_style_3)
        elif style == "style_4":
            label.setFont(font_style_4)
    
    def populate_table(self, number_counter):
        self.result_table.setRowCount(len(number_counter))
        for i, (num, freq) in enumerate(number_counter.most_common()):
            self.result_table.setItem(i, 0, QTableWidgetItem(str(num)))
            self.result_table.setItem(i, 1, QTableWidgetItem(str(freq)))
    
    def fetch_recent_results(self, lottery_type, lucky_numbers, from_date, to_date):
        if hasattr(self, 'fetch_thread') and self.fetch_thread is not None and self.fetch_thread.isRunning():
            self.fetch_thread.quit()
            self.fetch_thread.wait()
        self.fetch_thread = FetchResultsThread(lottery_type, lucky_numbers, from_date, to_date)
        self.fetch_thread.results_fetched.connect(self.display_recent_results)
        self.fetch_thread.finished.connect(lambda: self.generate_button.setEnabled(True) or self.generate_button.setText("Generate Lucky Numbers"))
        self.fetch_thread.start()
    
    def display_recent_results(self, recent_results):
        self.recent_results_table.setRowCount(len(recent_results))
        for i, row_data in enumerate(recent_results):
            for j, item in enumerate(row_data):
                self.recent_results_table.setItem(i, j, QTableWidgetItem(item))
    
    def add_history(self, lottery_type, lucky_numbers):
        row_count = self.history_table.rowCount()
        self.history_table.insertRow(row_count)
        self.history_table.setItem(row_count, 0, QTableWidgetItem(lottery_type))
        for i, num in enumerate(lucky_numbers):
            self.history_table.setItem(row_count, i+1, QTableWidgetItem(num))
    
    def export_data(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file)
                # Export Lucky Numbers
                writer.writerow(["Lucky Numbers:", self.lucky_numbers_label.text()])
                writer.writerow([])  # Blank row

                # Export Frequency Table
                writer.writerow(["Frequency Table:"])
                writer.writerow(["Number", "Frequency"])
                for row in range(self.result_table.rowCount()):
                    writer.writerow([
                        self.result_table.item(row, 0).text(),
                        self.result_table.item(row, 1).text()
                    ])
                writer.writerow([])  # Blank row

                # Export Random 1000 Combinations
                writer.writerow(["Random 1000 Combinations:"])
                writer.writerow(["Combination #", "Num1", "Num2", "Num3", "Num4", "Num5", "Num6"])
                for row in range(self.combinations_table.rowCount()):
                    writer.writerow([
                        self.combinations_table.item(row, col).text()
                        for col in range(self.combinations_table.columnCount())
                    ])
                writer.writerow([])  # Blank row

                # Export Recent Results
                writer.writerow(["Recent Results:"])
                writer.writerow(["Draw", "1", "2", "3", "4", "5", "6"])
                for row in range(self.recent_results_table.rowCount()):
                    writer.writerow([
                        self.recent_results_table.item(row, col).text()
                        for col in range(self.recent_results_table.columnCount())
                    ])
                writer.writerow([])  # Blank row

                # Export Generation History
                writer.writerow(["Lucky Numbers History:"])
                writer.writerow(["Lotto Type", "1", "2", "3", "4", "5", "6"])
                for row in range(self.history_table.rowCount()):
                    writer.writerow([
                        self.history_table.item(row, col).text()
                        for col in range(self.history_table.columnCount())
                    ])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LotteryAnalyzer()
    window.show()
    sys.exit(app.exec())
