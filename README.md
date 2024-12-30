# MQTT File and Message Transfer

This project implements a communication system between clients and a server using **MQTT** as the communication protocol. The system allows clients to send messages to each other via MQTT server, sending messages using Direct Message Chat, and transfer files directly between clients.

## Features

- **Server/Client Communication via MQTT**  
  All communication between the server and clients is handled over MQTT. Clients subscribe to topics and receive messages sent by other clients through the server or directly.

- **Client Registration**  
  Each client connects to the server and notifies it of its presence by providing a username. The server maintains a list of all active clients.

- **Message Sending**  
  Clients can send text messages to the server addressed to a specific username. The server then forwards the message to the appropriate client that is currently connected under that username.
  A message sent to an unsubscribed user will be saved and sent to them once they are connected.

- **Client Lookup API**  
  Clients can query the server to retrieve the connection address of a specific client using a provided username.

- **Direct Client-to-Client Messaging**  
  Clients can send direct messages to each other.

- **File Transfer Between Clients**  
  Clients can send files directly to each other in chunks. The receiving client reassembles the file as it receives each chunk, ensuring complete and accurate file transfers.

## Setup

### Requirements
- **Python 3.x**
- **Paho MQTT**: Python MQTT client library (`pip install paho-mqtt==1.6.1`)
        ***Notice that app support paho mqtt on version 1.1.6 !!!!***
- **PyQt5** : Python GUI library (`pip install PyQt5`)


### Running the Server
To start the server, run the following command:
```bash
python3 mqtt_server.py
 ```

### Running the Chat App
To start the Chat App, run the following command:
```bash
python3 chat_app.py
```

