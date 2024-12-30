import os
import socket
import base64
from PyQt5.QtCore import Qt
from datetime import datetime
import paho.mqtt.client as mqtt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox, QDialog, QDialogButtonBox, QFileDialog, QProgressBar)

# Main login window
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat App - Login")
        self.setGeometry(100, 100, 300, 200)

        # Create login form
        self.username_label = QLabel("Username:", self)
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Enter your username")

        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.login)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.login_button)

        # Container
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def login(self):
        username = self.username_input.text()
        if username:
            self.switch_to_chat(username)
        else:
            QMessageBox.warning(self, "Error", "Please enter a username.")

    # Turn off login page, turn on chat page
    def switch_to_chat(self, username):
        self.chat_window = ChatWindow(username)
        self.chat_window.show()
        self.close()


class ChatWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle(f"Chat App - {self.username}")
        self.setGeometry(100, 100, 400, 600)

        self.chat_display = QLabel(f"Welcome to the chat {self.username}!\nPlease enter your message, end it with '|' charecter following with addressee name.\nExample: Hey dear client!|client2\n\n\n\n\n", self)
        self.chat_display.setAlignment(Qt.AlignTop)
        self.chat_display.setStyleSheet("background-color: #f0f0f0; padding: 10px;")

        self.message_input = QLineEdit(self)
        self.message_input.setPlaceholderText("<Message using server>|<addressee>")

        self.send_button = QPushButton("Send Via Server", self)
        self.send_button.clicked.connect(self.send_message)

        self.address_api = QPushButton("Get IP Address API", self)
        self.address_api.clicked.connect(self.show_address_api)

        self.direct_message = QPushButton("Direct Message Chat", self)
        self.direct_message.clicked.connect(self.start_direct_message)

        self.file_button = QPushButton("Send File", self)
        self.file_button.clicked.connect(self.select_file)


        # Placeholder for dynamic widgets
        self.address_input = None
        self.ip_api_button = None
        self.collapse_address_api_button = None

        self.layout = QVBoxLayout()

        # Add widgets to the main layout
        self.layout.addWidget(self.chat_display)
        self.layout.addWidget(self.message_input)
        self.layout.addWidget(self.send_button)
        self.layout.addWidget(self.direct_message)
        self.layout.addWidget(self.file_button)
        self.layout.addWidget(self.address_api)

        # Container Widget
        self.layout_container = QWidget()
        self.layout_container.setLayout(self.layout)
        self.setCentralWidget(self.layout_container)

        self.connect_to_mqtt()

    def connect_to_mqtt(self):
        # MQTT client setup
        self.client = mqtt.Client(self.username)
        self.client.on_message = self.on_message
        self.client.connect("broker.emqx.io", 1883, 60)
        self.client.loop_start()
        
        # Register with the server, using username and ip   
        ip_address = socket.gethostbyname(socket.gethostname())
        self.client.publish("chat/server", f"REGISTER|{self.username}|{ip_address}")

        # Subscribe to the user's private topic
        self.client.subscribe(f"chat/{self.username}/#")

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode("utf-8")
        current_timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M]")

        if msg.topic.endswith("file"):
            self.download_file(message)
        else:
            self.chat_display.setText(f"{self.chat_display.text()}\n{current_timestamp} {message}")

    def send_message(self):
        message = self.message_input.text()
        if message:
            if "|" not in message:
                QMessageBox.warning(self, "Error", "Please add the addressee name at the end of the message, seperated by '|'.")
                return

            # Extract the addressee from the message
            addressee = message.split("|")[-1]
            # Check if the addressee is the same as the sender
            if addressee == self.username:
                QMessageBox.warning(self, "Error", "Cannot send a message to yourself.")
                return

            # Here, the message is sent to the server/topic for forwarding
            self.client.publish("chat/server", f"MESSAGE|{self.username}|{message}")
            self.message_input.clear()
        else:
            QMessageBox.warning(self, "Error", "Cannot send an empty message.")

    def show_address_api(self):
        # Hide the Address API button and create the input & new button
        self.layout.removeWidget(self.address_api)  # Remove the Address API button
        self.address_api.setParent(None)  # Also remove from parent

        # Add the collapse button to return to original form
        self.collapse_address_api_button = QPushButton("Collapse Address API", self)
        self.collapse_address_api_button.clicked.connect(self.collapse_address_api)
        self.layout.addWidget(self.collapse_address_api_button)

        # Create a text input for entering a username
        self.address_input = QLineEdit(self)
        self.address_input.setPlaceholderText("Enter username to get IP")
        self.layout.addWidget(self.address_input)

        # Create a button for sending the GET_IP request
        self.get_ip_button = QPushButton("Get User IP", self)
        self.get_ip_button.clicked.connect(self.get_ip)
        self.layout.addWidget(self.get_ip_button)

        # Trigger a layout update
        self.centralWidget().adjustSize()

    def collapse_address_api(self):
        # Remove the address input and IP API button
        self.layout.removeWidget(self.address_input)
        self.address_input.setParent(None)

        self.layout.removeWidget(self.get_ip_button)
        self.get_ip_button.setParent(None)

        self.layout.removeWidget(self.collapse_address_api_button)
        self.collapse_address_api_button.setParent(None)

        # Add the Address API button back
        self.layout.addWidget(self.address_api)

        # Trigger a layout update
        self.centralWidget().adjustSize()

    def get_ip(self):
        if self.address_input:
            target_username = self.address_input.text()
            if target_username:
                self.client.publish("chat/server", f"GET_IP|{target_username}|{self.username}")
            else:
                QMessageBox.warning(self, "Error", "Please enter a username.")

    def start_direct_message(self):
        target_username = self.select_username_popup()

        if not target_username:
            QMessageBox.warning(self, "Error", "Please enter a username.")
            return
        
        self.dm_window = DirectMessageWindow(target_username, self.username, self.client)
        self.dm_window.show()

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)")
        if file_path:
            # Display file name for confirmation
            QMessageBox.information(self, "File Selected", f"Selected file: {file_path}")
            self.send_file(file_path)

    def send_file(self, file_path):
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Select adresssee for the file
        target_username = self.select_username_popup()

        self.client.publish(f"chat/server", f"FILE_ALERT|{self.username}|{file_name}|{file_size}|{target_username}")

        bytes_sent = 0

        with open(file_path, "rb") as f:
            while chunk := f.read(1024):
                # Encode the binary chunk to base64 before sending
                encoded_chunk = base64.b64encode(chunk).decode("utf-8")
                self.client.publish(f"chat/{target_username}/file", f"{file_name}|{encoded_chunk}")
                bytes_sent += len(chunk)

        QMessageBox.information(self, "File Sent", f"File '{file_name}' sent.")


    def select_username_popup(self):
        # Open popup window for entering username to send a direct message
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Enter the target username")
        self.username_input.setFixedWidth(200)
        
        self.username_dialog = QDialog(self)
        self.username_dialog.setWindowTitle("Enter Target Username")
        self.username_dialog.setFixedSize(300, 100)
        
        layout = QVBoxLayout()
        layout.addWidget(self.username_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.username_dialog.accept)
        button_box.rejected.connect(self.username_dialog.reject)
        
        layout.addWidget(button_box)

        self.username_dialog.setLayout(layout)

        if self.username_dialog.exec_() == QDialog.Accepted:
            return self.username_input.text()

        else:
            QMessageBox.warning(self, "Error", "Please enter a target username.")
            return

    def download_file(self, msg):
        file_name, chunk = msg.split("|", 1)
        decoded_chunk = base64.b64decode(chunk)
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),file_name)

        # Append the chunk to the file
        try:
            with open(file_path, "ab") as f:
                f.write(decoded_chunk)
        except Exception as e:
            print(f"Error writing file: {e}")

        print(f"Received chunk for file {file_name}")

    def closeEvent(self, event):
        # Send disconnect message to the server
        self.client.publish("chat/server", f"DISCONNECT|{self.username}")

        # Ensure proper disconnect
        self.client.disconnect()

        # Close the window
        event.accept()

class DirectMessageWindow(QMainWindow):
    def __init__(self, target_username, username, mqtt_client):
        super().__init__()
        self.setWindowTitle(f"Direct Message With {target_username}")
        self.setGeometry(100, 100, 400, 600)

        # Set the username, target username, and topics
        self.username = username
        self.target_username = target_username
        self.dm_topic = f"chat/{self.username}_{self.target_username}"
        self.publish_topic = f"chat/{self.target_username}_{self.username}"

        # Reuse the main client instance
        self.client = mqtt_client

        self.message_label = QLabel(f"Direct Message With {target_username}", self)
        self.message_label.setAlignment(Qt.AlignTop)
        self.message_label.setStyleSheet("background-color: #f0f0f0; padding: 10px;")

        self.message_input = QLineEdit(self)
        self.message_input.setPlaceholderText("Type your message here...")

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_message)

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.message_label)
        self.layout.addWidget(self.message_input)
        self.layout.addWidget(self.send_button)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        # subscribe to the DM topic
        self.subscribe_to_dm_topic()

    def subscribe_to_dm_topic(self):
        print(f"Subscribing to DM topic: {self.dm_topic}")
        self.client.message_callback_add(self.dm_topic, self.dm_message)
        self.client.subscribe(self.dm_topic)

    def send_message(self):
        message = self.message_input.text()

        if message:
            self.client.publish(self.publish_topic, message)  # Publish to the DM topic
            self.message_input.clear()
        else:
            QMessageBox.warning(self, "Error", "Cannot send an empty message.")
            return

    def dm_message(self, client, userdata, msg):
        message = msg.payload.decode("utf-8")
        print(f"Received DM: {message}")
        current_timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M]")
        self.message_label.setText(f"{self.message_label.text()}\n{current_timestamp} {message}")

    
app = QApplication([])
window = LoginWindow()
window.show()
app.exec_()
