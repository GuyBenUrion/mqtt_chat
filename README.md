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
To ensure the app runs smoothly, you need to install the necessary dependencies. You can easily do this by running the following command:

```bash
pip install -r requirements.txt
