from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox, QApplication
from PyQt6.QtCore import QDateTime
from PyQt6.QtGui import QFont

def set_font_style(widget, label, style):
    """Set font style for a label based on widget size"""
    # Define font styles
    base_font_size = widget.width() // 80  # Dynamically adjust font size based on window width

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

def update_time(label, month_map):
    """Update the time display label"""
    # Get the current date and time
    current_time = QDateTime.currentDateTime()
    
    # Extract the components of the date
    day = current_time.date().day()
    month = current_time.date().toString("MM")  # Get month as a two-digit string (e.g., "04")
    year = current_time.date().year()
    
    # Convert the month using the MONTH_MAP
    month_name = month_map.get(month, "")
    
    # Get the time in 12-hour format with AM/PM
    time_str = current_time.toString("hh:mm:ss AP")
    
    # Format the date as "Month Day, Year" (e.g., "April 28, 2025")
    formatted_date = f"{month_name} {day}, {year} - {time_str}"
    
    # Update the label text with the formatted date and time
    label.setText(formatted_date)

def toggle_collapsible_content(result_table, combinations_table, checked):
    """Show or hide the contents of the collapsible group."""
    # Show or hide the content based on whether the group is checked
    result_table.setVisible(checked)
    combinations_table.setVisible(checked)

def resize_and_center(widget):
    """Resize the window and center it on the screen"""
    screen = QApplication.primaryScreen()
    screen_size = screen.size()

    width = int(screen_size.width() * 0.6)
    height = int(screen_size.height() * 0.75)

    widget.resize(width, height)

    screen_geometry = screen.geometry()
    x = (screen_geometry.width() - width) // 2
    y = (screen_geometry.height() - height) // 2
    widget.move(x, y)

def populate_table(table, number_counter):
    """Populate the frequency table with data"""
    table.setRowCount(len(number_counter))
    for i, (num, freq) in enumerate(number_counter.most_common()):
        table.setItem(i, 0, QTableWidgetItem(str(num)))
        table.setItem(i, 1, QTableWidgetItem(str(freq)))

def display_recent_results(table, recent_results):
    """Display recent lottery results in the table"""
    table.setRowCount(len(recent_results))
    for i, row_data in enumerate(recent_results):
        for j, item in enumerate(row_data):
            table.setItem(i, j, QTableWidgetItem(item))

def add_history(table, lottery_type, lucky_numbers):
    """Add a new entry to the history table"""
    row_count = table.rowCount()
    table.insertRow(row_count)
    table.setItem(row_count, 0, QTableWidgetItem(lottery_type))
    for i, num in enumerate(lucky_numbers):
        table.setItem(row_count, i+1, QTableWidgetItem(num))

def update_all_fonts(widget, labels_dict):
    """Update all fonts in the UI"""
    for label_name, style in labels_dict.items():
        label = getattr(widget, label_name)
        set_font_style(widget, label, style)