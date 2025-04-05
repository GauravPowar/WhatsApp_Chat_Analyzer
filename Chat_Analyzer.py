import sys
import re
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit
from PyQt6.QtGui import QPixmap
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

class WhatsAppChatAnalyzer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("WhatsApp Chat Analyzer")
        self.setGeometry(100, 100, 600, 500)

        # Layout
        self.layout = QVBoxLayout()

        # File selection button
        self.fileButton = QPushButton("Load Chat File")
        self.fileButton.clicked.connect(self.loadFile)
        self.layout.addWidget(self.fileButton)

        # Label to show loaded file name
        self.fileLabel = QLabel("No file selected")
        self.layout.addWidget(self.fileLabel)

        # Display area for chat preview
        self.chatPreview = QTextEdit()
        self.chatPreview.setReadOnly(True)
        self.layout.addWidget(self.chatPreview)

        # Analyze button
        self.analyzeButton = QPushButton("Analyze Chat")
        self.analyzeButton.clicked.connect(self.analyzeChat)
        self.layout.addWidget(self.analyzeButton)

        # WordCloud display
        self.wordCloudLabel = QLabel()
        self.layout.addWidget(self.wordCloudLabel)

        self.setLayout(self.layout)

    def loadFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Open WhatsApp Chat", "", "Text Files (*.txt)")
        if filePath:
            self.fileLabel.setText(f"Loaded: {os.path.basename(filePath)}")
            with open(filePath, "r", encoding="utf-8") as file:
                self.chatData = file.readlines()
            preview_text = "".join(self.chatData[:10])  # Show first 10 lines as preview
            self.chatPreview.setText(preview_text)

    def analyzeChat(self):
        if not hasattr(self, "chatData"):
            self.fileLabel.setText("⚠ No file loaded! Please load a chat file first.")
            return
        
        # Extract messages from chat
        chat_text = self.extractMessages(self.chatData)

        if not chat_text.strip():
            self.fileLabel.setText("⚠ Error: No valid messages found in the chat file!")
            return

        # Generate WordCloud
        self.generateWordCloud(chat_text)

    def extractMessages(self, chat_lines):
        """ Extracts actual messages from the WhatsApp chat """
        message_pattern = re.compile(r"^\[\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}(:\d{2})? (AM|PM)?\] .*?: (.*)")
        messages = [match.group(3) for line in chat_lines if (match := message_pattern.match(line))]
        return " ".join(messages)

    def generateWordCloud(self, text):
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
        
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")

        # Save wordcloud image
        wordcloud_path = "wordcloud.png"
        plt.savefig(wordcloud_path)
        plt.close()

        # Display in PyQt Label
        self.wordCloudLabel.setPixmap(QPixmap(wordcloud_path))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhatsAppChatAnalyzer()
    window.show()
    sys.exit(app.exec())
