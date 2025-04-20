import sys
import re
from collections import defaultdict
import pandas as pd
import emoji
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PyQt6.QtWidgets import (QApplication, QMainWindow, QFileDialog, 
                            QPushButton, QLabel, QTextEdit, QVBoxLayout, QWidget)
from PyQt6.QtCore import Qt


class WhatsAppChatAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI."""
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
        """Load the chat file and enable the analyze button."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open WhatsApp Chat File", 
            "", 
            "Text Files (*.txt)"
        )
        if file_path:
            self.file_path = file_path
            self.generate_btn.setEnabled(True)
            self.label.setText(f"Loaded: {file_path.split('/')[-1]}")
            self.result_area.clear()
    
    def analyze_chat(self):
        """Main analysis function that coordinates parsing and visualization."""
        if not self.file_path:
            self.result_area.setText("⚠ Error: No file loaded!")
            return
            
        try:
            chat_data = self.parse_chat(self.file_path)
            
            if chat_data.empty:
                self.result_area.setText("⚠ Error: No valid messages found in the chat file!")
                return
                
            stats = self.generate_stats(chat_data)
            self.result_area.setText(stats)
            self.generate_word_cloud(chat_data)
            
        except Exception as e:
            self.result_area.setText(f"⚠ Error processing file: {str(e)}")
    
    def parse_chat(self, file_path):
        """Parse the WhatsApp chat file into a structured DataFrame."""
        messages = []
        media_messages = []
        pattern = re.compile(
            r"^(\[?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\]?,?\s?\[?(\d{1,2}:\d{2}(?::\d{2})?(?:\s?[AP]M)?)\]?\s?[-\]]\s?(.*?):\s?(.*))$",
            re.IGNORECASE
        )
        
        with open(file_path, "r", encoding="utf-8") as file:
            current_message = None
            
            for line in file:
                line = line.strip()
                if not line or "Messages and calls are end-to-end encrypted" in line:
                    continue
                
                match = pattern.match(line)
                if match:
                    if current_message and current_message[3]:  # If we have a previous message
                        messages.append(current_message)
                    
                    full_match, date, time, sender, message = match.groups()
                    if "<Media omitted>" in message:
                        media_messages.append([date, time, sender, "Media"])
                        current_message = [date, time, sender, ""]
                    else:
                        current_message = [date, time, sender, message]
                elif current_message:
                    if current_message[3]:
                        current_message[3] += " " + line
                    else:
                        current_message[3] = line
        
        if current_message and current_message[3]:
            messages.append(current_message)
            
        # Combine regular messages and media messages
        all_messages = messages + media_messages
        if not all_messages:
            print("⚠ No valid messages extracted! Check chat format.")
            return pd.DataFrame()
            
        return pd.DataFrame(all_messages, columns=["Date", "Time", "Sender", "Message"])
    
    def generate_stats(self, df):
        """Generate statistics from the chat data including media counts."""
        total_messages = len(df)
        
        # Calculate regular messages vs media messages
        media_messages = df[df['Message'] == 'Media']
        regular_messages = df[df['Message'] != 'Media']
        media_count = len(media_messages)
        
        # User-specific stats
        user_stats = defaultdict(lambda: {'total': 0, 'media': 0, 'text': 0})
        
        for _, row in df.iterrows():
            user = row['Sender']
            user_stats[user]['total'] += 1
            if row['Message'] == 'Media':
                user_stats[user]['media'] += 1
            else:
                user_stats[user]['text'] += 1
        
        # Emoji count (only for text messages)
        emoji_count = sum(
            char in emoji.EMOJI_DATA 
            for msg in regular_messages['Message'].dropna() 
            for char in msg
        )
        
        # Words per message (only for text messages)
        word_counts = regular_messages['Message'].str.split().str.len()
        avg_words = word_counts.mean()
        
        # Active hours
        df['Hour'] = pd.to_datetime(df['Time']).dt.hour
        active_hours = df['Hour'].value_counts().sort_index()
        
        # Format statistics
        stats = f"📊 Chat Analysis Report\n{'='*40}\n"
        stats += f"📝 Total Messages: {total_messages:,}\n"
        stats += f"📷 Media Files Shared: {media_count:,} ({media_count/total_messages:.1%})\n"
        stats += f"📋 Text Messages: {len(regular_messages):,}\n"
        stats += f"📊 Average Words per Text Message: {avg_words:.1f}\n"
        stats += f"😊 Total Emojis Used: {emoji_count:,}\n\n"
        
        stats += "👥 User Statistics:\n"
        for user, counts in sorted(user_stats.items(), key=lambda x: x[1]['total'], reverse=True):
            stats += (
                f"  • {user}:\n"
                f"    📌 Total: {counts['total']:,}\n"
                f"    ✏️ Text: {counts['text']:,} ({counts['text']/counts['total']:.1%})\n"
                f"    🖼️ Media: {counts['media']:,} ({counts['media']/counts['total']:.1%})\n"
            )
        
        stats += "\n🕒 Most Active Hours:\n"
        stats += "\n".join([f"  • {hour:02d}:00 - {count:,} messages" 
                          for hour, count in active_hours.head(5).items()])
        
        return stats
    
    def generate_word_cloud(self, df):
        """Generate and display a word cloud from text messages only."""
        text_messages = df[df['Message'] != 'Media']
        text = " ".join(msg for msg in text_messages['Message'].dropna() if msg.strip())
        
        if not text.strip():
            self.result_area.append("\n⚠ No valid words found for word cloud!")
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
            self.result_area.append(f"\n⚠ Error generating word cloud: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)
    
    window = WhatsAppChatAnalyzer()
    window.show()
    sys.exit(app.exec())
