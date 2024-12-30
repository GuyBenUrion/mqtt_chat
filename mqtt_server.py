import paho.mqtt.client as mqtt

# Store clients and their usernames
clients = {}
# Store messages for offline users (message queue)
message_queue = {}

def on_connect(client, userdata, flags, rc):
    print("Server connected to MQTT broker.")

def on_message(client, userdata, msg):
    global clients, message_queue
    topic = msg.topic
    message = msg.payload.decode('utf-8')
    if topic == "chat/server":

        if message.startswith("REGISTER"):
            # Register new client with its ip
            reg_msg = message.split("|")
            msg_type, username, ip = reg_msg
            print(f"Registering {username} with IP {ip}")
            clients[username] = {client: ip} # Store the MQTT client for the user
            print(f"{username} registered and is online.")

            # Check if there are any messages saved for this user
            if username in message_queue:
                for saved_message in message_queue[username]:
                    # Send saved messages to the user once they log in
                    client.publish(f"chat/{username}", f"From {saved_message['from']}: {saved_message['content']}")
                # Clear saved messages after sending
                del message_queue[username]

        elif message.startswith("GET_IP"):
            # Get the IP address of a client"
            msg_type, target_username, username = message.split("|")
            if target_username in clients:
                client_ip = clients[target_username]
                ip = list(client_ip.values())[0]
                client.publish(f"chat/{username}", f"{target_username} IP address is: {ip}")
            else:
                client.publish(f"chat/{username}", f"{target_username} is not online.")
                print(f"{target_username} is not online.")

        elif message.startswith("DISCONNECT"):
            # Disconnect a client: "DISCONNECT:username"
            username = message.split("|")[-1]
            if username in clients:
                del clients[username]  # Remove the user from the clients dictionary
                print(f"{username} disconnected and removed from the client list.")

        elif message.startswith("MESSAGE"):

            try:
                msg_type, sender, content, target = message.split("|")
            except ValueError:
                print("Invalid message format.")

            # If target is online, forward the message
            if target in clients:
                client.publish(f"chat/{target}", f"From {sender}: {content}")
                print(f"Message sent to {target}: {content}")
            else:
                # If the target is offline, save the message
                if target not in message_queue:
                    message_queue[target] = []

                message_queue[target].append({"from": sender, "content": content})
                print(f"{target} is offline. Message saved.")

        elif message.startswith("FILE_ALERT"):
            # Send a file alert to the target user
            msg_type, sender, file_name, file_size, target = message.split("|")
            if target in clients:
                client.publish(f"chat/{target}", f"{sender} sent you a file: {file_name}, with size: {file_size}")  
                print(f"File alert sent to {target}: {file_name}")
            else:
                print(f"{target} is offline. File alert not sent.")
        
        elif message.startswith("FILE"):
            # Send a file to the target user
            msg_type, file_name, target, chunk = message.split("|", 3)

            if target in clients:
                client.publish(f"chat/{target}/file", f"{file_name}|{chunk}")
                print(f"File sent to {target}: {file_name}")
            else:
                print(f"{target} is offline. File not sent.")
    else:
        print(f"Unhandled topic: {topic}")

# Create MQTT client for the server
server = mqtt.Client("chat_server")
server.on_connect = on_connect
server.on_message = on_message

# Connect to the public broker
server.connect("broker.emqx.io", 1883, 60)

# Subscribe to server topic
server.subscribe("chat/server")

# Start the server loop
print("MQTT server is running...")
server.loop_forever()
