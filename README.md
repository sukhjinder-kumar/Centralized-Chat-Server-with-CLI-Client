# Centralized CLI Chat System

A simple, centralized chat application built with Python’s standard library. It consists of a single TCP server (`server.py`) and multiple CLI clients (`client.py`) that can:

- Join named **channels** (group chats)  
- Send **broadcast** messages within a channel  
- Send **private messages** to individual users  
- Gracefully **join**, **switch**, and **quit**  

## 🚀 Features

- **Multi-threaded server** handles each client connection in its own thread  
- **Channels**: `/join <channel>` to switch or create channels  
- **Broadcast**: messages are relayed to all clients in the same channel  
- **Private messaging**: `/msg <username> <message>`  
- **Graceful disconnect**: `/quit` notifies other users and cleans up  
- **Timestamps & usernames** prefixed on every chat message  
- **Thread-safe** client and channel management  


## 🛠️ Requirements

- Python 3.6 or higher  
- No external dependencies—uses only the standard library  


## 📥 Installation

1. **Clone this repo**  
   ```bash
   git clone https://github.com/yourusername/cli-chat.git
   cd cli-chat
   ```

2. Verify your Python version
    ```bash
    python3 --version
    ```

## ⚙️ Usage

### 1. Start the Server

    ```bash
    python3 server.py
    ```

By default, the server listens on 127.0.0.1:12345. You’ll see log messages like:

    ```bash
    [Server] Running on 127.0.0.1:12345
    ```

### 2. Run a Client

In a separate terminal:

```bash
python3 client.py
```

1. You’ll see:

```bash
Enter username:
```

2. Type your username and press Enter.

3. You’ll receive a welcome message and join the default #general channel.

### 3. Chat Commands

- **Send a message**: simply type and press Enter

- **Switch channels**:

    ```bash
    /join <channel_name>
    ```
    Creates the channel if it doesn’t exist, and notifies others.

- **Private message**:

    ```bash
    msg <username> <your message here>
    ```

- **Quit**:

    ```bash
    \quit
    ```

    Notifies your channel, then cleanly disconnects.

### 4. Example Session

```bash
[Server] Alice connected from ('127.0.0.1', 52678)
[Server] Alice joined channel 'general'

[12:00:01] Alice: Hello everyone!
[12:00:05] Bob: Hi Alice!

# Alice switches to “random”:
> /join random
[12:01:00] Server: You’ve switched to channel ‘random’
[12:01:00] Alice joined random

# Send a private note to Bob:
> /msg Bob Are you free to test?
```
