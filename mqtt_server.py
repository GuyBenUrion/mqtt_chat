import logging
import paho.mqtt.client as mqtt
from dataclasses import dataclass
from typing import Dict, List, TypedDict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MQTT Configuration
BROKER_HOST = "broker.emqx.io"
BROKER_PORT = 1883
KEEP_ALIVE = 60
SERVER_TOPIC = "chat/server"

# Message types
class MessageType:
    REGISTER = "REGISTER"
    GET_IP = "GET_IP"
    DISCONNECT = "DISCONNECT"
    MESSAGE = "MESSAGE"
    FILE_ALERT = "FILE_ALERT"

@dataclass
class SavedMessage:
    sender: str
    content: str

class ClientInfo(TypedDict):
    client: mqtt.Client
    ip: str

# Global state
clients: Dict[str, ClientInfo] = {}
message_queue: Dict[str, List[SavedMessage]] = {}

def handle_register(client: mqtt.Client, username: str, ip: str) -> None:
    # Handle client registration
    clients[username] = {"client": client, "ip": ip}
    logger.info(f"User {username} registered with IP {ip}")

    # Send queued messages if any
    if username in message_queue:
        for saved_message in message_queue[username]:
            client.publish(
                f"chat/{username}",
                f"From {saved_message.sender}: {saved_message.content}"
            )
        del message_queue[username]
        logger.info(f"Delivered queued messages to {username}")

def handle_get_ip(client: mqtt.Client, target_username: str, username: str) -> None:
    # Handle IP address request
    if target_username in clients:
        client_ip = clients[target_username]["ip"]
        client.publish(f"chat/{username}", f"{target_username} IP address is: {client_ip}")
        logger.info(f"IP address for {target_username} sent to {username}")
    else:
        client.publish(f"chat/{username}", f"{target_username} is not online.")
        logger.info(f"IP request failed: {target_username} is not online")

def handle_disconnect(username: str) -> None:
    # Hamdle client disconnect
    if username in clients:
        del clients[username]
        logger.info(f"User {username} disconnected")

def handle_message(client: mqtt.Client, sender: str, content: str, target: str) -> None:
    if target in clients:
        client.publish(f"chat/{target}", f"From {sender}: {content}")
        logger.info(f"Message delivered from {sender} to {target}")
    else:
        if target not in message_queue:
            message_queue[target] = []
        message_queue[target].append(SavedMessage(sender=sender, content=content))
        logger.info(f"Message queued for offline user {target}")

def handle_file_alert(client: mqtt.Client, sender: str, file_name: str, file_size: str, target: str) -> None:
    if target in clients:
        client.publish(f"chat/{target}",f"{sender} sent you a file: {file_name}, with size: {file_size}")
        logger.info(f"File alert sent to {target} for file {file_name}")
    else:
        logger.info(f"File alert not sent: {target} is offline")

def on_connect(client: mqtt.Client, userdata: Optional[Dict], flags: Dict, rc: int) -> None:
    logger.info("Server connected to MQTT broker")

def on_message(client: mqtt.Client, userdata: Optional[Dict], msg: mqtt.MQTTMessage) -> None:
    # Handle incoming messages
    topic = msg.topic
    try:
        message = msg.payload.decode('utf-8')
        
        if topic != SERVER_TOPIC:
            logger.warning(f"Unhandled topic: {topic}")
            return

        parts = message.split("|")
        msg_type = parts[0]

        if msg_type == MessageType.REGISTER and len(parts) == 3:
            _, username, ip = parts
            handle_register(client, username, ip)
        
        elif msg_type == MessageType.GET_IP and len(parts) == 3:
            _, target_username, username = parts
            handle_get_ip(client, target_username, username)
        
        elif msg_type == MessageType.DISCONNECT and len(parts) == 2:
            _, username = parts
            handle_disconnect(username)
        
        elif msg_type == MessageType.MESSAGE and len(parts) == 4:
            _, sender, content, target = parts
            handle_message(client, sender, content, target)
        
        elif msg_type == MessageType.FILE_ALERT and len(parts) == 5:
            _, sender, file_name, file_size, target = parts
            handle_file_alert(client, sender, file_name, file_size, target)
        
        else:
            logger.warning(f"Invalid message format or unknown message type: {message}")

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")

def main() -> None:
    try:
        server = mqtt.Client("chat_server")
        server.on_connect = on_connect
        server.on_message = on_message

        server.connect(BROKER_HOST, BROKER_PORT, KEEP_ALIVE)
        server.subscribe(SERVER_TOPIC)

        logger.info("MQTT server is running...")
        server.loop_forever()
    except Exception as e:
        logger.error(f"Server error: {str(e)}")

if __name__ == "__main__":
    main()
