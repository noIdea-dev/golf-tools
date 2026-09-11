# Golf Handicap Calculator

A PyQt5-based desktop application for calculating golf handicaps according to USPGA Tour rules.

## Features
- Input and store golf scores
- Automatically calculate handicap based on recent scores
- Store scores locally in JSON format
- Clean and modern user interface
- Delete individual scores
- View handicap history

## Installation

1. Ensure you have Python 3.7+ installed
2. Create and activate the virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

After installing the requirements, run the application with:
```bash
python golf_handicap.py
```

## How to Use
1. Enter your golf score in the input field
2. Click "Add Score" to save the score
3. Your handicap will be automatically calculated once you have at least 5 scores
4. Use the delete button to remove any incorrect scores
5. Scores are automatically saved to a local JSON file

## Handicap Calculation
The handicap is calculated using the following method:
- Takes the lowest 8 scores from your last 20 rounds
- Calculates the average differential
- Applies the 0.96 multiplier as per USPGA rules
- Rounds to one decimal place
