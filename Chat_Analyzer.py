import sys
import re
import pandas as pd
import emoji
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QTextEdit, QVBoxLayout, QWidget

class WhatsAppAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("WhatsApp Chat Analyzer")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()
        
        self.label = QLabel("Upload a WhatsApp chat file (.txt)")
        layout.addWidget(self.label)
        
        self.upload_btn = QPushButton("Upload Chat File")
        self.upload_btn.clicked.connect(self.loadFile)
        layout.addWidget(self.upload_btn)
        
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)
        
        self.generate_btn = QPushButton("Generate Insights")
        self.generate_btn.clicked.connect(self.analyzeChat)
        self.generate_btn.setEnabled(False)
        layout.addWidget(self.generate_btn)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def loadFile(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open WhatsApp Chat File", "", "Text Files (*.txt)", options=options)
        if file_path:
            self.file_path = file_path
            self.generate_btn.setEnabled(True)
            self.label.setText(f"Loaded: {file_path}")

    def analyzeChat(self):
        chat_data = self.parseChat(self.file_path)
        stats = self.generateStats(chat_data)
        self.result_area.setText(stats)
        self.generateWordCloud(chat_data)

    def parseChat(self, file_path):
        messages = []
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                match = re.match(r"^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2} (?:AM|PM)?) - (.*?): (.*)$", line)
                if match:
                    date, time, sender, message = match.groups()
                    messages.append((date, time, sender, message))
        return pd.DataFrame(messages, columns=["Date", "Time", "Sender", "Message"])

    def generateStats(self, df):
        total_messages = len(df)
        users = df['Sender'].value_counts().to_dict()
        emoji_count = sum(1 for msg in df['Message'] if any(char in emoji.EMOJI_DATA for char in msg))
        stats = f"Total Messages: {total_messages}\n"
        stats += "Messages Per User:\n" + "\n".join([f"{user}: {count}" for user, count in users.items()])
        stats += f"\nTotal Emojis Used: {emoji_count}"
        return stats

    def generateWordCloud(self, df):
        text = " ".join(df['Message'].dropna())
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhatsAppAnalyzer()
    window.show()
    sys.exit(app.exec())
