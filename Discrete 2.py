import sys
import itertools
import random
import requests
import csv
from datetime import datetime
from collections import Counter
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import (QApplication, QDateEdit, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, 
                               QTableWidget, QTableWidgetItem, QCheckBox, QFileDialog, QHeaderView, QGridLayout)
from PyQt6.QtCore import QDate, Qt, QThread, pyqtSignal

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
    
    def init_ui(self):
        layout = QGridLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Lottery type selection
        self.lottery_selector = QComboBox()
        self.lottery_selector.addItems(LOTTERY_CONFIG.keys())
        layout.addWidget(QLabel("Select Lottery Type:"), 0, 0)
        layout.addWidget(self.lottery_selector, 1, 0)

        self.from_date_edit = QDateEdit()
        self.from_date_edit.setCalendarPopup(True)
        self.from_date_edit.setDate(QDate.currentDate().addDays(-7))
        layout.addWidget(QLabel("From Date:"), 2, 0)
        layout.addWidget(self.from_date_edit, 3, 0)

        self.to_date_edit = QDateEdit()
        self.to_date_edit.setCalendarPopup(True)
        self.to_date_edit.setDate(QDate.currentDate())
        layout.addWidget(QLabel("To Date:"), 4, 0)
        layout.addWidget(self.to_date_edit, 5, 0)
        
        # Generate lucky numbers button
        self.generate_button = QPushButton("Generate Lucky Numbers")
        self.generate_button.clicked.connect(self.generate_lucky_numbers)
        layout.addWidget(self.generate_button, 6, 0)
        
        # Lucky Numbers display
        self.lucky_numbers_label = QLabel("<b>Lucky Numbers:</b> ")
        self.lucky_numbers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lucky_numbers_label, 7, 0)

        # Export data button
        self.export_button = QPushButton("Export Data")
        self.export_button.clicked.connect(self.export_data)
        layout.addWidget(self.export_button, 8, 0)
        
        # Dark mode toggle
        self.dark_mode_toggle = QCheckBox("Dark Mode")
        self.dark_mode_toggle.stateChanged.connect(self.toggle_dark_mode)
        layout.addWidget(self.dark_mode_toggle, 9, 0)
        
        # Generation History table (7 columns: Lotto Type + 6 lucky numbers)
        self.history_table = QTableWidget(0, 7)
        self.history_table.setHorizontalHeaderLabels(["Lotto Type", "1", "2", "3", "4", "5", "6"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(QLabel("<b>Lucky Numbers History:</b>"), 0, 1)
        layout.addWidget(self.history_table, 1, 1, 2, 1)

        # Frequency table
        self.result_table = QTableWidget(0, 2)
        self.result_table.setHorizontalHeaderLabels(["Number", "Frequency"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(QLabel("<b>Frequency Table:</b>"), 3, 1)
        layout.addWidget(self.result_table, 4, 1, 2, 1)
           
        # Random combinations table (7 columns: Label + 6 numbers)
        self.combinations_table = QTableWidget(0, 7)
        self.combinations_table.setHorizontalHeaderLabels(["Combination #", "Num1", "Num2", "Num3", "Num4", "Num5", "Num6"])
        self.combinations_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(QLabel("<b>Randomly Picked 1000 Combinations:</b>"), 6, 1)
        layout.addWidget(self.combinations_table, 7, 1, 2, 1)
        
        # Recent results table (7 columns: Draw label + 6 winning numbers)
        self.recent_results_table = QTableWidget(0, 7)
        self.recent_results_table.setHorizontalHeaderLabels(["Draw", "1", "2", "3", "4", "5", "6"])
        self.recent_results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(QLabel("<b>Recent Results:</b>"), 9, 1)
        layout.addWidget(self.recent_results_table, 10, 1, 2, 1)
        
        self.setLayout(layout)
        self.setWindowTitle("Lottery Number Analyzer")
        self.setGeometry(100, 100, 900, 800)
    
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
        
        self.lucky_numbers_label.setText(f"Lucky Numbers: {'-'.join(top_6)}")
        self.populate_table(number_counter)
        self.fetch_recent_results(lottery_type, top_6, from_date, to_date)
        self.add_history(lottery_type, top_6)

        self.generate_button.setEnabled(True)
        self.generate_button.setText("Generate Lucky Numbers")
    
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

    def toggle_dark_mode(self, state):
        if state == Qt.CheckState.Checked.value:
            dark_stylesheet = """
                QWidget { background-color: #353535; color: white; }
                QPushButton { background-color: #555; color: white; border-radius: 5px; }
                QTableWidget { background-color: #252525; color: white; }
                QHeaderView::section { background-color: #454545; color: white; }
                QTableWidget QTableCornerButton::section { background-color: #454545; }
                QLabel { color: white; }  /* Ensure labels are also styled */
            """
        else:
            dark_stylesheet = """
                QWidget { background-color: white; color: black; }
                QPushButton { background-color: #ddd; color: black; border-radius: 5px; }
                QTableWidget { background-color: white; color: black; }
                QHeaderView::section { background-color: transparent; color: black; }
                QLabel { color: black; }  /* Reset label colors */
            """
        self.setStyleSheet(dark_stylesheet)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LotteryAnalyzer()
    window.show()
    sys.exit(app.exec())
