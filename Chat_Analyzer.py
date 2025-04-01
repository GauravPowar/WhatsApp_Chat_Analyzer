def parseChat(self, file_path):
    messages = []
    pattern = re.compile(r"^(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}) - (.*?): (.*)$")

    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        current_date, current_time, current_sender, current_message = None, None, None, []

        for line in lines:
            line = line.strip()
            match = pattern.match(line)

            if match:
                if current_date and current_sender:
                    messages.append((current_date, current_time, current_sender, " ".join(current_message)))
                
                current_date, current_time, current_sender, message = match.groups()
                current_message = [message]  # Start collecting a new message
            elif current_sender:
                current_message.append(line)  # Append multi-line messages
            
        if current_date and current_sender:
            messages.append((current_date, current_time, current_sender, " ".join(current_message)))

    if not messages:
        print("⚠ No valid messages extracted! Check chat format.")

    return pd.DataFrame(messages, columns=["Date", "Time", "Sender", "Message"])
