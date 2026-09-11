import sys
import json
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QScrollArea, QTableWidget, QTableWidgetItem, 
                           QHeaderView, QMessageBox, QInputDialog, QDateEdit, QGridLayout,
                           QComboBox, QCheckBox, QRadioButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.Qt import QDate

class GolfHandicapCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scores = self.load_scores()
        self.migrate_old_scores()
        self.update_course_ratings()  
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Golf Handicap Calculator')
        self.setMinimumSize(1000, 700)  # Increased window size
        
        # Set the window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                min-width: 120px;
            }
            QLabel {
                font-size: 14px;
            }
            #handicapLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2C3E50;
                padding: 10px;
                background-color: #ECF0F1;
                border-radius: 4px;
                margin: 10px;
            }
            #handicapTitle {
                font-size: 18px;
                font-weight: bold;
                color: #2C3E50;
            }
            #instructionLabel {
                color: #7F8C8D;
                font-size: 12px;
            }
            #inputLabel {
                font-weight: bold;
                color: #2C3E50;
                font-size: 14px;
                padding: 5px;
            }
            QDateEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                min-width: 120px;
            }
            #formSection {
                background-color: #ECF0F1;
                border-radius: 8px;
                padding: 20px;
                margin: 10px;
            }
        """)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)

        # Handicap display
        handicap_frame = QWidget()
        handicap_frame.setStyleSheet("background-color: #ECF0F1; border-radius: 8px; padding: 15px;")
        handicap_layout = QHBoxLayout(handicap_frame)
        handicap_layout.setAlignment(Qt.AlignCenter)
        
        self.handicap_label = QLabel('Your Current USPGA Handicap Index:')
        self.handicap_label.setObjectName('handicapTitle')
        self.handicap_value = QLabel('N/A')
        self.handicap_value.setObjectName('handicapLabel')
        self.handicap_value.setAlignment(Qt.AlignCenter)
        
        handicap_layout.addWidget(self.handicap_label)
        handicap_layout.addWidget(self.handicap_value)
        
        main_layout.addWidget(handicap_frame)

        # Instructions
        instruction_label = QLabel('Enter your golf scores below. You need at least 5 scores to calculate a handicap.')
        instruction_label.setObjectName('instructionLabel')
        instruction_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(instruction_label)

        # Score input form
        form_widget = QWidget()
        form_widget.setObjectName('formSection')
        form_layout = QGridLayout(form_widget)
        form_layout.setAlignment(Qt.AlignCenter)

        # Section title
        section_title = QLabel('Add New Score')
        section_title.setObjectName('handicapTitle')
        section_title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(section_title, 0, 0, 1, 9)

        # Date input
        date_label = QLabel('Date:')
        date_label.setObjectName('inputLabel')
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form_layout.addWidget(date_label, 1, 0)
        form_layout.addWidget(self.date_input, 2, 0)

        # Score input
        score_label = QLabel('Score:')
        score_label.setObjectName('inputLabel')
        self.score_input = QLineEdit()
        self.score_input.setPlaceholderText('e.g., 85')
        form_layout.addWidget(score_label, 1, 2)
        form_layout.addWidget(self.score_input, 2, 2)

        # Course Rating input
        course_rating_label = QLabel('Course Rating:')
        course_rating_label.setObjectName('inputLabel')
        self.course_rating_input = QLineEdit()
        self.course_rating_input.setPlaceholderText('74.5')
        self.course_rating_input.setText('74.5')  # Set default value
        form_layout.addWidget(course_rating_label, 1, 4)
        form_layout.addWidget(self.course_rating_input, 2, 4)

        # Slope Rating input
        slope_rating_label = QLabel('Slope Rating:')
        slope_rating_label.setObjectName('inputLabel')
        self.slope_rating_input = QLineEdit()
        self.slope_rating_input.setPlaceholderText('122')
        self.slope_rating_input.setText('122')  # Set default value
        form_layout.addWidget(slope_rating_label, 1, 6)
        form_layout.addWidget(self.slope_rating_input, 2, 6)

        # Add Score button
        self.add_button = QPushButton('Add Score')
        form_layout.addWidget(self.add_button, 2, 8)
        self.add_button.clicked.connect(self.add_score)

        main_layout.addWidget(form_widget)

        # Scores table section
        table_section = QWidget()
        table_section.setObjectName('formSection')
        table_layout = QVBoxLayout(table_section)
        
        table_title = QLabel('Your Score History')
        table_title.setObjectName('handicapTitle')
        table_title.setAlignment(Qt.AlignCenter)
        table_layout.addWidget(table_title)
        
        self.scores_table = QTableWidget()
        self.scores_table.setColumnCount(5)
        self.scores_table.setHorizontalHeaderLabels(['Date', 'Score', 'Course Rating', 'Slope Rating', 'Actions'])
        self.scores_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.scores_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.scores_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.scores_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.scores_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        table_layout.addWidget(self.scores_table)
        
        main_layout.addWidget(table_section)

        # Status label
        self.status_label = QLabel('')
        self.status_label.setObjectName('instructionLabel')
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        self.update_scores_table()
        self.calculate_handicap()

    def load_scores(self):
        try:
            with open('scores.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is corrupted, start fresh
            return []

    def save_scores(self):
        with open('scores.json', 'w') as f:
            json.dump(self.scores, f)

    def add_score(self):
        try:
            # Get score
            score = float(self.score_input.text())
            if score < 0 or score > 200:
                QMessageBox.warning(self, 'Invalid Score', 'Please enter a valid golf score (0-200).')
                return

            # Get course rating
            try:
                course_rating = float(self.course_rating_input.text())
                if course_rating < 0 or course_rating > 100:
                    QMessageBox.warning(self, 'Invalid Course Rating', 'Please enter a valid course rating (0-100).')
                    return
            except ValueError:
                QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid course rating.')
                return

            # Get slope rating
            try:
                slope_rating = float(self.slope_rating_input.text())
                if slope_rating < 55 or slope_rating > 155:
                    QMessageBox.warning(self, 'Invalid Slope Rating', 'Please enter a valid slope rating (55-155).')
                    return
            except ValueError:
                QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid slope rating.')
                return
            
            # Calculate handicap differential
            differential = ((score - course_rating) * 113) / slope_rating
            
            self.scores.append({
                'date': self.date_input.date().toString('yyyy-MM-dd'),
                'score': score,
                'course_rating': course_rating,
                'slope_rating': slope_rating,
                'differential': round(differential, 1)
            })
            self.save_scores()
            
            # Clear inputs
            self.score_input.clear()
            self.course_rating_input.clear()
            self.slope_rating_input.clear()
            self.date_input.setDate(QDate.currentDate())
            
            self.update_scores_table()
            self.calculate_handicap()
        except ValueError:
            QMessageBox.warning(self, 'Invalid Input', 'Please enter valid numbers for all fields.')

    def remove_score(self, index):
        self.scores.pop(index)
        self.save_scores()
        self.update_scores_table()
        self.calculate_handicap()

    def update_scores_table(self):
        self.scores_table.setRowCount(0)
        for i, score_data in enumerate(self.scores):
            self.scores_table.insertRow(i)
            date_item = QTableWidgetItem(score_data['date'])
            score_item = QTableWidgetItem(str(score_data['score']))
            course_rating_item = QTableWidgetItem(str(score_data['course_rating']))
            slope_rating_item = QTableWidgetItem(str(score_data['slope_rating']))
            
            delete_button = QPushButton('Delete')
            delete_button.clicked.connect(lambda checked, index=i: self.remove_score(index))
            
            self.scores_table.setItem(i, 0, date_item)
            self.scores_table.setItem(i, 1, score_item)
            self.scores_table.setItem(i, 2, course_rating_item)
            self.scores_table.setItem(i, 3, slope_rating_item)
            self.scores_table.setCellWidget(i, 4, delete_button)

    def calculate_handicap(self):
        if len(self.scores) < 5:
            self.handicap_value.setText('Need 5+ Scores')
            self.status_label.setText(f'You have {len(self.scores)} scores. Add {5 - len(self.scores)} more to calculate your handicap.')
            return

        # Get all differentials
        differentials = [score['differential'] for score in self.scores]
        
        # Take the last 20 rounds
        recent_differentials = differentials[-20:] if len(differentials) > 20 else differentials
        
        # Sort differentials from lowest to highest
        sorted_differentials = sorted(recent_differentials)
        
        # Take the lowest 8 differentials (or fewer if less than 8 scores)
        num_scores_to_use = min(8, len(sorted_differentials))
        lowest_differentials = sorted_differentials[:num_scores_to_use]
        
        # Calculate average of lowest differentials
        average_differential = sum(lowest_differentials) / num_scores_to_use
        
        # Apply 0.96 multiplier
        handicap_index = average_differential * 0.96
        
        # Round to one decimal place
        handicap_index = round(max(0, handicap_index), 1)
        self.handicap_value.setText(f'{handicap_index}')
        self.status_label.setText(f'Handicap Index calculated using your {num_scores_to_use} lowest differentials from your last {len(recent_differentials)} rounds.')

    def migrate_old_scores(self):
        for score in self.scores:
            if 'course_rating' not in score:
                score['course_rating'] = 71.5  # Updated to typical par 72 course rating
            if 'slope_rating' not in score:
                score['slope_rating'] = 113.0  # Standard slope rating
            if 'differential' not in score:
                # Calculate differential for old scores
                differential = ((score['score'] - score['course_rating']) * 113) / score['slope_rating']
                score['differential'] = round(differential, 1)
        self.save_scores()

    def update_course_ratings(self):
        """Update all scores with new course and slope ratings"""
        for score in self.scores:
            score['course_rating'] = 74.5
            score['slope_rating'] = 122.0
            # Recalculate differential with new ratings
            differential = ((score['score'] - score['course_rating']) * 113) / score['slope_rating']
            score['differential'] = round(differential, 1)
        self.save_scores()

def main():
    app = QApplication(sys.argv)
    ex = GolfHandicapCalculator()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
