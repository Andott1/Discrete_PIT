from PyQt6.QtWidgets import QTableWidgetItem, QFileDialog
from ui_utils import (update_time, toggle_collapsible_content, show_lucky_numbers_popup, 
                     populate_table, display_recent_results, add_history, update_all_fonts)
from utils import generate_lucky_numbers, export_data_to_csv
from threads import FetchResultsThread
from config import MONTH_MAP

def handle_update_time(parent):
    """Handle updating the time display"""
    update_time(parent.date_time_label, MONTH_MAP)

def handle_toggle_details(parent, checked):
    """Handle toggling the collapsible details section"""
    toggle_collapsible_content(parent.result_table, parent.combinations_table, checked)

def handle_resize_event(parent, event):
    """Handle window resize events"""
    # Update all fonts when window is resized
    labels = {
        'tlabel1': 'style_2',
        'tlabel2': 'style_2',
        'tlabel3': 'style_2',
        'tlabel4': 'style_2',
        'llabel1': 'style_3',
        'llabel2': 'style_4',
        'llabel3': 'style_4',
        'llabel4': 'style_3',
        'date_time_label': 'style_2'
    }
    update_all_fonts(parent, labels)
    event.accept()

def handle_generate_lucky_numbers(parent):
    """Handle generating lucky numbers"""
    # Disable the generate button while processing
    parent.generate_button.setEnabled(False)
    parent.generate_button.setText("Generating...")

    lottery_type = parent.lottery_selector.currentText()
    from_date = parent.from_date_edit.date().toString("MM/dd/yyyy")
    to_date = parent.to_date_edit.date().toString("MM/dd/yyyy")
    
    # Use the utility function to generate numbers
    top_6, sampled_combinations, number_counter = generate_lucky_numbers(lottery_type)

    # Populate the random combinations table with labels
    parent.combinations_table.setRowCount(len(sampled_combinations))
    for i, comb in enumerate(sampled_combinations):
        parent.combinations_table.setItem(i, 0, QTableWidgetItem(f"Combination {i+1}"))
        for j, num in enumerate(comb):
            parent.combinations_table.setItem(i, j+1, QTableWidgetItem(str(num)))

    parent.llabel4.setText(f"Lucky Numbers:\n\n{'-'.join(top_6)}")
    
    # Use utility functions for UI updates
    populate_table(parent.result_table, number_counter)
    handle_fetch_recent_results(parent, lottery_type, top_6, from_date, to_date)
    add_history(parent.history_table, lottery_type, top_6)

    # Show the lucky numbers in a popup message box
    show_lucky_numbers_popup(top_6)

    parent.generate_button.setEnabled(True)
    parent.generate_button.setText("Generate Lucky Numbers")

def handle_fetch_recent_results(parent, lottery_type, lucky_numbers, from_date, to_date):
    """Handle fetching recent lottery results"""
    if hasattr(parent, 'fetch_thread') and parent.fetch_thread is not None and parent.fetch_thread.isRunning():
        parent.fetch_thread.quit()
        parent.fetch_thread.wait()
    parent.fetch_thread = FetchResultsThread(lottery_type, lucky_numbers, from_date, to_date)
    parent.fetch_thread.results_fetched.connect(lambda results: handle_display_results(parent, results))
    parent.fetch_thread.finished.connect(lambda: parent.generate_button.setEnabled(True) or parent.generate_button.setText("Generate Lucky Numbers"))
    parent.fetch_thread.start()

def handle_display_results(parent, recent_results):
    """Handle displaying recent results"""
    display_recent_results(parent.recent_results_table, recent_results)

def handle_export_data(parent):
    """Handle exporting data to CSV"""
    file_path, _ = QFileDialog.getSaveFileName(parent, "Save File", "", "CSV Files (*.csv)")
    if file_path:
        export_data_to_csv(
            file_path, 
            parent.llabel4.text(), 
            parent.result_table, 
            parent.combinations_table, 
            parent.recent_results_table, 
            parent.history_table
        )