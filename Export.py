import csv



def export_data_to_csv(file_path, lucky_numbers, frequency_data, combinations_table, recent_results_table, history_table):
    """Export all data to a CSV file"""
    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)
        
        writer.writerow(["Lucky Numbers:", lucky_numbers])
        writer.writerow([])
        
        writer.writerow(["Frequency Table:"])
        writer.writerow(["Number", "Frequency"])
        
        # Handle the frequency data which is now a list of tuples
        if isinstance(frequency_data, list):
            # Sort by frequency (highest to lowest)
            sorted_data = sorted(frequency_data, key=lambda x: int(x[1]) if x[1].isdigit() else 0, reverse=True)
            for num, freq in sorted_data:
                if freq != "0":  # Only include numbers with non-zero frequency
                    writer.writerow([num, freq])
        else:
            # Handle the old table format for backward compatibility
            for row in range(frequency_data.rowCount()):
                writer.writerow([
                    frequency_data.item(row, 0).text(),
                    frequency_data.item(row, 1).text()
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