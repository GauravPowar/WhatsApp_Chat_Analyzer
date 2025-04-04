import sys
import re
import pandas as pd
import emoji
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
from textblob import TextBlob
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, 
    QTextEdit, QVBoxLayout, QWidget, QCheckBox, QDateEdit, QHBoxLayout
)
from PyQt6.QtCore import QDate

class WhatsAppAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("WhatsApp Chat Analyzer")
        self.setGeometry(100, 100, 700, 500)

        layout = QVBoxLayout()

        self.label = QLabel("Upload a WhatsApp chat file (.txt)")
        layout.addWidget(self.label)

        self.upload_btn = QPushButton("Upload Chat File")
        self.upload_btn.clicked.connect(self.loadFile)
        layout.addWidget(self.upload_btn)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("From:"))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("To:"))
        date_layout.addWidget(self.end_date)
        layout.addLayout(date_layout)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)

        self.generate_btn = QPushButton("Generate Insights")
        self.generate_btn.clicked.connect(self.analyzeChat)
        self.generate_btn.setEnabled(False)
        layout.addWidget(self.generate_btn)

        self.export_btn = QPushButton("Export Report")
        self.export_btn.clicked.connect(self.exportReport)
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)

        self.dark_mode = QCheckBox("Dark Mode")
        self.dark_mode.stateChanged.connect(self.toggleDarkMode)
        layout.addWidget(self.dark_mode)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def loadFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open WhatsApp Chat File", "", "Text Files (*.txt)")
        if file_path:
            self.file_path = file_path
            self.generate_btn.setEnabled(True)
            self.label.setText(f"Loaded: {file_path}")

    def analyzeChat(self):
        chat_data = self.parseChat(self.file_path)

        if chat_data.empty:
            self.result_area.setText("⚠ Error: No valid messages found in the chat file!")
            return

        chat_data["Date"] = pd.to_datetime(chat_data["Date"], format="%d/%m/%Y")
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")

        chat_data = chat_data[(chat_data["Date"] >= start) & (chat_data["Date"] <= end)]

        if chat_data.empty:
            self.result_area.setText("⚠ No messages found in the selected date range!")
            return

        stats = self.generateStats(chat_data)
        self.result_area.setText(stats)
        self.export_btn.setEnabled(True)
        self.generateWordCloud(chat_data)

    def parseChat(self, file_path):
        messages = []
        pattern = re.compile(r"^(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}) - (.*?): (.*)$")

        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            current_date, current_time, current_sender, current_message = None, None, None, []

            for line in lines:
                line = line.strip()
                if "Messages and calls are end-to-end encrypted" in line or "<Media omitted>" in line:
                    continue  

                match = pattern.match(line)
                if match:
                    if current_date and current_sender:
                        messages.append((current_date, current_time, current_sender, " ".join(current_message)))

                    current_date, current_time, current_sender, message = match.groups()
                    current_message = [message]
                elif current_sender:
                    current_message.append(line)

        if current_date and current_sender and current_message:
            messages.append((current_date, current_time, current_sender, " ".join(current_message)))

        return pd.DataFrame(messages, columns=["Date", "Time", "Sender", "Message"])

    def generateStats(self, df):
        total_messages = len(df)
        users = df['Sender'].value_counts().to_dict()

        word_list = " ".join(df['Message']).split()
        most_common_words = Counter(word_list).most_common(10)

        emoji_list = [char for msg in df['Message'] for char in msg if char in emoji.EMOJI_DATA]
        most_common_emojis = Counter(emoji_list).most_common(5)

        sentiment_scores = [TextBlob(msg).sentiment.polarity for msg in df['Message']]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        sentiment_category = "Positive 😊" if avg_sentiment > 0 else "Negative 😞" if avg_sentiment < 0 else "Neutral 😐"

        stats = f"Total Messages: {total_messages}\n"
        stats += "Messages Per User:\n" + "\n".join([f"{user}: {count}" for user, count in users.items()])
        stats += "\n\nMost Common Words:\n" + ", ".join([f"{word} ({count})" for word, count in most_common_words])
        stats += "\n\nMost Used Emojis:\n" + ", ".join([f"{emoji} ({count})" for emoji, count in most_common_emojis])
        stats += f"\n\nOverall Sentiment: {sentiment_category}"

        return stats

    def generateWordCloud(self, df):
        text = " ".join(df['Message'].dropna())

        if not text.strip():
            self.result_area.append("\n⚠ No valid words found for word cloud!")
            return

        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()

    def exportReport(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.result_area.toPlainText())
            self.result_area.append("\n✅ Report saved successfully!")

    def toggleDarkMode(self, state):
        if state:
            self.setStyleSheet("background-color: #222; color: white;")
        else:
            self.setStyleSheet("")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhatsAppAnalyzer()
    window.show()
    sys.exit(app.exec())
