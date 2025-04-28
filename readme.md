# Lottery Number Generator

A Python application that generates lottery numbers and analyzes lottery results. This application provides a user-friendly interface for generating "lucky" lottery numbers for different lottery types, fetching recent lottery results, and analyzing number frequency patterns.

![Lottery Number Generator](assets/Splash_Screen.png)

## Features

- Generate "lucky" lottery numbers for different lottery types (Ultra Lotto 6/58, Grand Lotto 6/55, etc.)
- Fetch and display recent lottery results from PCSO website
- Analyze number frequency patterns
- Generate random combinations
- Export data to CSV
- Professional UI with splash screen

## Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Dependencies

The application requires the following Python packages:

- PyQt6 (for the GUI)
- requests (for web scraping)
- beautifulsoup4 (for parsing HTML)

### Installation Steps

1. Clone or download this repository:
git clone [https://github.com/yourusername/lottery-number-generator.git](https://github.com/yourusername/lottery-number-generator.git)
cd lottery-number-generator
2. Install the required dependencies:


## Running the Application

To run the application, simply execute the main.py file:

\`\`\`
python main.py
\`\`\`

The application will start with a splash screen, followed by the main application window.

## Project Structure

\`\`\`
lottery-number-generator/
├── assets/
│   ├── Splash_Screen.png     # Splash screen image
│   └── lottery_ball.png      # Optional: Icon for buttons
├── config.py                 # Configuration constants
├── lottery_service.py        # Web scraping for lottery results
├── utils.py                  # Core utility functions
├── ui_utils.py               # UI-specific utility functions
├── ui_builder.py             # UI construction and layout
├── threads.py                # Background processing threads
├── event_handlers.py         # Event handling logic
├── splash_screen.py          # Splash screen implementation
├── simple_splash.py          # Alternative simple splash screen
├── main.py                   # Main application
├── requirements.txt          # Dependencies list
└── README.md                 # This file
\`\`\`

## Usage

1. **Select Lottery Type**: Choose from different lottery types (Ultra Lotto 6/58, Grand Lotto 6/55, etc.)
2. **Set Date Range**: Select the date range for fetching lottery results
3. **Generate Lucky Numbers**: Click the "Generate Lucky Numbers" button to generate lucky numbers
4. **View Results**: View the generated numbers, recent results, and frequency analysis
5. **Export Data**: Export the data to a CSV file for further analysis

## Lottery Types Supported

- Ultra Lotto 6/58
- Grand Lotto 6/55
- Superlotto 6/49
- Megalotto 6/45
- Lotto 6/42

## Troubleshooting

### Common Issues

1. **Splash screen doesn't appear**:
- Make sure the splash screen image exists in the assets folder
- Check if the image format is supported (PNG, JPG)
- Try using the simple splash screen implementation

2. **Error fetching lottery results**:
- Check your internet connection
- The website structure might have changed, requiring an update to the scraping code
- Try using a different date range

3. **UI elements appear too small or large**:
- The application scales based on your screen resolution
- Adjust your display scaling settings if needed

### Debug Mode

To run the application in debug mode with additional logging:

\`\`\`
python main.py --debug
\`\`\`

## Development

### Adding New Lottery Types

To add a new lottery type, update the `LOTTERY_CONFIG` dictionary in `config.py`:

```python
LOTTERY_CONFIG = {
 "New Lottery Type": (min_number, max_number),
 # Existing lottery types...
}