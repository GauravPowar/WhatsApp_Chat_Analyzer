# WhatsApp Chat Analyzer

## Overview
The **WhatsApp Chat Analyzer** is a GUI-based Python application that allows users to upload and analyze exported WhatsApp chat files (`.txt`). It extracts meaningful insights such as message statistics, emoji usage, and generates a word cloud visualization of frequently used words.

## Features
- **Upload WhatsApp Chat File**: Supports `.txt` files exported from WhatsApp.
- **Message Statistics**: Counts total messages, messages per user, and emoji usage.
- **Word Cloud Generation**: Visualizes frequently used words.
- **User-Friendly Interface**: Built with PyQt6 for ease of use.

## Requirements
### Dependencies
Ensure you have Python installed along with the required dependencies:
```sh
pip install pandas emoji matplotlib wordcloud PyQt6
```

## Installation & Usage
1. Clone the repository:
```sh
git clone https://github.com/GauravPowar/WhatsApp_Chat_Analyzer.git
cd Chat_Analyzer
```
2. Run the script:
```sh
python Chat_Analyzer.py
```
3. Click **"Upload Chat File"** and select your WhatsApp `.txt` file.
4. Click **"Generate Insights"** to analyze the chat and view results.

## How It Works
- Parses WhatsApp chat files to extract sender information, timestamps, and messages.
- Computes basic statistics like the total number of messages and emoji usage.
- Generates a word cloud from the chat messages.
- Displays all insights in a user-friendly GUI.

## Notes
- The tool **ignores media messages** (`<Media omitted>`) and system messages (`Messages and calls are end-to-end encrypted`).
- Ensure the chat format follows **WhatsApp's standard export format**.
- Ensure that you don't violate any of **WhatsApp's Privacy Policy**.

## License
This project is licensed under the *MIT License*.

## Contributions
Feel free to submit issues or pull requests to improve the project!

## Repository
GitHub: [WhatsApp Chat Analyzer](https://github.com/GauravPowar/WhatsApp_Chat_Analyzer/)

## Created With Love (and countless bug fixes) By Gaurav
