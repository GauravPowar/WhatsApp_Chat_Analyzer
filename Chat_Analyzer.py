import sys
import re
from collections import defaultdict
import pandas as pd
import emoji
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QTextEdit,
    QVBoxLayout, QWidget
)
from PyQt6.QtCore import Qt


class WhatsAppChatAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("WhatsApp Chat Analyzer")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        self.label = QLabel("Upload a WhatsApp chat file (.txt)")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.label)

        self.upload_btn = QPushButton("Upload Chat File")
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.upload_btn.clicked.connect(self.load_file)
        layout.addWidget(self.upload_btn)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.result_area.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                padding: 10px;
                font-family: monospace;
            }
        """)
        layout.addWidget(self.result_area)

        self.generate_btn = QPushButton("Generate Insights")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #008CBA;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #007B9E;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.generate_btn.clicked.connect(self.analyze_chat)
        self.generate_btn.setEnabled(False)
        layout.addWidget(self.generate_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open WhatsApp Chat File", "", "Text Files (*.txt)"
        )
        if file_path:
            self.file_path = file_path
            self.generate_btn.setEnabled(True)
            self.label.setText(f"Loaded: {file_path.split('/')[-1]}")
            self.result_area.clear()

    def analyze_chat(self):
        if not self.file_path:
            self.result_area.setText("⚠ Error: No file loaded!")
            return

        try:
            chat_df = self.parse_chat(self.file_path)

            if chat_df.empty:
                self.result_area.setText("⚠ No valid messages found in the chat file.")
                return

            report = self.generate_stats(chat_df)
            self.result_area.setText(report)
            self.generate_word_cloud(chat_df)

        except Exception as e:
            self.result_area.setText(f"⚠ Error: {str(e)}")

    def parse_chat(self, file_path):
        messages = []
        media_messages = []
        msg_pattern = re.compile(
            r"^(\[?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\]?,?\s?\[?(\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM)?)\]?\s?[-\]]?\s?(.*?):\s?(.*))$",
            re.IGNORECASE
        )

        with open(file_path, "r", encoding="utf-8") as file:
            current_msg = None
            for line in file:
                line = line.strip()
                if not line or "end-to-end encrypted" in line.lower():
                    continue

                match = msg_pattern.match(line)
                if match:
                    if current_msg:
                        messages.append(current_msg)

                    _, date, time, sender, message = match.groups()
                    if "<Media omitted>" in message:
                        media_messages.append([date, time, sender, "Media"])
                        current_msg = [date, time, sender, ""]
                    else:
                        current_msg = [date, time, sender, message]
                elif current_msg:
                    current_msg[3] += " " + line if current_msg[3] else line

        if current_msg:
            messages.append(current_msg)

        all_msgs = messages + media_messages
        if not all_msgs:
            return pd.DataFrame()

        return pd.DataFrame(all_msgs, columns=["Date", "Time", "Sender", "Message"])

    def generate_stats(self, df):
        total = len(df)
        media_msgs = df[df['Message'] == 'Media']
        text_msgs = df[df['Message'] != 'Media']
        media_count = len(media_msgs)

        stats = defaultdict(lambda: {'total': 0, 'media': 0, 'text': 0})
        for _, row in df.iterrows():
            sender = row['Sender']
            stats[sender]['total'] += 1
            if row['Message'] == 'Media':
                stats[sender]['media'] += 1
            else:
                stats[sender]['text'] += 1

        emoji_count = sum(
            char in emoji.EMOJI_DATA
            for msg in text_msgs['Message'].dropna()
            for char in msg
        )

        avg_words = text_msgs['Message'].str.split().str.len().mean()

        try:
            df['Hour'] = pd.to_datetime(df['Time'], errors='coerce').dt.hour
            active_hours = df['Hour'].dropna().value_counts().sort_index()
        except Exception:
            active_hours = pd.Series()

        report = f"📊 Chat Analysis Report\n{'='*40}\n"
        report += f"📝 Total Messages: {total:,}\n"
        report += f"📷 Media Files: {media_count:,} ({media_count/total:.1%})\n"
        report += f"📋 Text Messages: {len(text_msgs):,}\n"
        report += f"📝 Avg. Words per Message: {avg_words:.1f}\n"
        report += f"😊 Total Emojis: {emoji_count:,}\n\n"

        report += "👥 Per User Breakdown:\n"
        for user, counts in sorted(stats.items(), key=lambda x: x[1]['total'], reverse=True):
            report += (
                f"  • {user}:\n"
                f"    ✉️ Total: {counts['total']:,}\n"
                f"    🖊️ Text: {counts['text']:,} ({counts['text']/counts['total']:.1%})\n"
                f"    📎 Media: {counts['media']:,} ({counts['media']/counts['total']:.1%})\n"
            )

        if not active_hours.empty:
            report += "\n🕒 Most Active Hours:\n"
            report += "\n".join([f"  • {hour:02d}:00 – {count:,} messages" for hour, count in active_hours.head(5).items()])
        else:
            report += "\n🕒 Most Active Hours: Unavailable due to time format parsing error."

        return report

    def generate_word_cloud(self, df):
        text = " ".join(df[df['Message'] != 'Media']['Message'].dropna())
        if not text.strip():
            self.result_area.append("\n⚠ No valid words for word cloud.")
            return

        try:
            wordcloud = WordCloud(
                width=1200,
                height=600,
                background_color='white',
                colormap='viridis',
                stopwords={'media', 'omitted', 'this', 'that', 'the', 'and', 'you'},
                max_words=200
            ).generate(text)

            plt.figure(figsize=(12, 6))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            plt.title("Word Cloud of Text Messages", pad=20)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            self.result_area.append(f"\n⚠ Word cloud error: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)

    analyzer = WhatsAppChatAnalyzer()
    analyzer.show()
    sys.exit(app.exec())
