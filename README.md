# Coms — Version 1

A modular TCP communication system written in Python.

Coms is a custom communication protocol designed to provide structured communication between a client and server. The system uses TCP sockets for reliable transport and JSON packets for structured application-level communication.

Version 1 establishes the core communication architecture and provides the foundation for future modules, security improvements, UDP support, and eventually embedded/microcontroller implementations.

---

## Features

Version 1 currently provides:

- TCP client/server communication
- Length-prefixed packets
- JSON-based packet structure
- Protocol versioning
- Modular message handling
- `TEXT` module
- `SYSTEM` module
- Configurable maximum packet size
- Exact socket reads using `recv_exact()`
- Packet validation
- Invalid JSON detection
- UTF-8 validation
- Socket timeouts
- Connection error handling
- Dynamic module selection
- Separate packet-building and packet-processing logic

---

## Project Structure

```text
Coms/
│
└── tcp_layer/
    ├── client.py
    ├── server.py
    ├── protocol.py
    ├── handlers.py
    ├── config.py
    ├── startup.sh
    ├── LICENSE
    └── README.md
```

### `client.py`

The client establishes a TCP connection to the server.

Its responsibilities include:

- Connecting to the server
- Accepting user input
- Selecting the active module
- Building packets through the appropriate module builder
- Sending packets
- Receiving responses
- Dispatching received packets to their appropriate handlers
- Handling connection errors and timeouts

The client does not directly construct the low-level packet header. That responsibility belongs to `protocol.py`.

---

### `server.py`

The server listens for incoming TCP connections.

Its responsibilities include:

- Binding to the configured host and port
- Accepting client connections
- Receiving packets
- Processing and validating packets
- Dispatching packets to module handlers
- Building response packets
- Sending responses back to the client
- Handling malformed packets and connection failures

The server uses the same protocol implementation as the client.

---

### `protocol.py`

This file contains the core packet transport and processing logic.

It provides:

#### `recv_exact(sock, size)`

Receives exactly the requested number of bytes from a TCP socket.

This is necessary because TCP is a byte stream and does **not** guarantee that one `recv()` call will return an entire packet.

#### `send_packet(sock, packet)`

Serializes a Python dictionary into JSON, encodes it as UTF-8, creates the packet header, and sends the complete packet.

#### `receive_packet(sock)`

Receives the packet header, determines the payload length, checks the maximum packet size, receives the payload, and decodes the JSON data.

#### `process_packet(sock)`

Performs higher-level packet validation.

It verifies that:

- The packet is a dictionary
- The `version` field exists
- The protocol version is supported
- The `module` field exists
- The module is a valid string
- The requested module exists
- The `payload` field exists

---

## Packet Structure

Coms Version 1 uses a length-prefixed packet format.

The packet transmitted over TCP has the following structure:

```text
┌──────────────────────┬──────────────────────────────┐
│  4-byte header       │        JSON payload         │
│  payload length      │                              │
└──────────────────────┴──────────────────────────────┘
```

The header is encoded using:

```python
struct.pack("!I", packet_length)
```

`!I` means:

- `!` — network byte order (big-endian)
- `I` — unsigned 32-bit integer

The header therefore tells the receiver exactly how many bytes make up the JSON payload.

---

## Example Packet

A text message may look like this before serialization:

```json
{
    "version": 1,
    "module": "TEXT",
    "type": "MESSAGE",
    "payload": "Hello"
}
```

A system information packet may look like:

```json
{
    "version": 1,
    "module": "SYSTEM",
    "type": "INFO",
    "payload": {
        "hostname": "Linux-Mint",
        "platform": "Linux",
        "release": "..."
    }
}
```

---

# Modules

Coms is designed around modules.

The module name determines how a packet should be constructed and how received data should be handled.

## TEXT

The `TEXT` module handles ordinary text communication.

Example:

```text
> hello
Response: hello
```

Its packet builder creates a packet containing:

```json
{
    "version": 1,
    "module": "TEXT",
    "type": "MESSAGE",
    "payload": "hello"
}
```

---

## SYSTEM

The `SYSTEM` module transmits system information.

The current implementation provides information such as:

- Hostname
- Operating system/platform
- OS release

Example:

```text
> /module SYSTEM
switched to SYSTEM
```

The system packet is then automatically constructed from the local system information.

This means the user does not need to manually type the system information.

---

# Module Architecture

Modules are registered using dictionaries.

For example:

```python
build_handlers = {
    "TEXT": build_text_packet,
    "SYSTEM": build_system_packet
}
```

When the active module is selected, the program retrieves its builder:

```python
builder = build_handlers.get(module_to_be_used)
```

This allows the communication system to select the appropriate function dynamically.

The same concept is used when receiving packets:

```python
receive_handlers = {
    "TEXT": text_handler,
    "SYSTEM": system_handler
}
```

The module field inside a received packet determines which handler processes it.

This architecture allows new modules to be added without rewriting the core networking logic.

---

# Configuration

`config.py` contains the central configuration values.

Current configuration includes:

```python
HOST = '127.0.0.1'
PORT = 6500

MAX_PACKET_LENGTH = 1024 * 1024

PROTOCOL_VERSION = 1

HEADER_SIZE = 4

DEFAULT_MODULE = "TEXT"

SOCKET_TIMEOUT = ...
```

### `HOST`

Determines the network address used by the server/client.

`127.0.0.1` currently restricts communication to the local machine.

### `PORT`

Defines the TCP port used by Coms.

### `MAX_PACKET_LENGTH`

Prevents the program from accepting packets larger than the configured limit.

This protects the application from blindly allocating resources for an excessively large packet.

### `PROTOCOL_VERSION`

Identifies the version of the Coms packet protocol.

Currently:

```text
1
```

### `HEADER_SIZE`

Defines the size of the packet length header.

Currently:

```text
4 bytes
```

### `DEFAULT_MODULE`

Defines the module selected when the program starts.

Currently:

```text
TEXT
```

### `SOCKET_TIMEOUT`

Defines how long socket operations may wait before timing out.

---

# Packet Validation

Before a packet is processed, Coms performs several checks.

The packet must:

1. Be valid JSON.
2. Decode successfully as UTF-8.
3. Be represented as a dictionary.
4. Contain a `version`.
5. Use the supported protocol version.
6. Contain a `module`.
7. Use a valid module name.
8. Contain a `payload`.
9. Stay below the maximum packet size.

Invalid packets are rejected rather than being passed directly to the module handlers.

---

# Why `recv_exact()` Exists

TCP does not preserve application-level message boundaries.

For example, if the sender transmits:

```text
[HEADER][PAYLOAD]
```

the receiver might receive:

```text
recv() → first part of HEADER
recv() → rest of HEADER + part of PAYLOAD
recv() → rest of PAYLOAD
```

Therefore, Coms cannot assume that one `recv()` call equals one packet.

`recv_exact()` repeatedly receives data until the requested number of bytes has been collected.

The receiver therefore performs:

```text
Receive 4-byte header
        ↓
Determine payload length
        ↓
Receive exactly that many bytes
        ↓
Decode JSON
        ↓
Validate packet
        ↓
Dispatch to module
```

This is one of the fundamental parts of the Coms protocol.

---

# Error Handling

Version 1 includes basic network and protocol error handling.

### Connection refused

```text
Server not listening
```

This occurs when the client attempts to connect while no server is listening on the configured port.

### Socket timeout

```text
Connection timed out
```

This prevents the application from waiting indefinitely for network activity.

### Invalid packet

Malformed or invalid packets are rejected.

Examples include:

```text
Missing required field: version
```

```text
Invalid packet version
```

```text
Invalid packet module
```

```text
Packet contains invalid JSON
```

### Connection errors

Connection failures are caught and handled rather than allowing the program to terminate unexpectedly.

---

# Running Coms

Open two terminals.

## Terminal 1 — Server

Navigate to the project directory:

```bash
cd ~/Projects/Coms/tcp_layer
```

Run:

```bash
python3 server.py
```

The server should display:

```text
Server is listening on 127.0.0.1:6500
```

---

## Terminal 2 — Client

Navigate to the same directory:

```bash
cd ~/Projects/Coms/tcp_layer
```

Run:

```bash
python3 client.py
```

The client should connect to the server.

You can then send messages:

```text
> Hello
```

and receive a response from the server.

---

# Switching Modules

The active module can be changed using:

```text
/module MODULE_NAME
```

For example:

```text
/module SYSTEM
```

The client will switch to the `SYSTEM` module.

The next packet will therefore be constructed using the `SYSTEM` packet builder rather than the `TEXT` packet builder.

---

# Design Philosophy

Coms separates the system into several layers.

```text
┌─────────────────────────────┐
│           Client            │
│       User interaction      │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│          Handlers           │
│   Build / process modules   │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│          Protocol           │
│ JSON + length-prefixed TCP  │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│            TCP              │
│        Socket layer         │
└─────────────────────────────┘
```

This separation is intentional.

The application logic should not need to know how TCP packet framing works, while the protocol layer should not need to know what a `TEXT` or `SYSTEM` message means.

---

# Current Limitations

Version 1 is a foundational implementation and is **not intended to be production-grade communication software**.

Current limitations include:

- Communication is currently TCP-based.
- The default configuration uses localhost.
- Authentication has not been implemented.
- Encryption has not been implemented.
- There is no cryptographic identity verification.
- There is no persistent user/device identity system.
- The module system is currently limited.
- The server currently handles communication in a simple sequential manner.
- The protocol does not yet provide advanced reliability/application-level acknowledgements.
- No UDP transport layer has been implemented yet.
- No microcontroller implementation currently exists.

These are future development areas rather than failures of Version 1.

---

# Version 1 Milestone

Version 1 establishes the fundamental Coms architecture:

```text
TCP
 ↓
Packet framing
 ↓
JSON serialization
 ↓
Protocol validation
 ↓
Module selection
 ↓
Module handler
```

The important achievement of Version 1 is not the number of features.

It is the establishment of a working, modular communication protocol that can be extended without redesigning the entire system.

---

# Future Development

Possible future versions may introduce:

## Version 2

- Stronger protocol validation
- Authentication
- Cryptographic security
- Improved error codes
- Better connection management
- More robust module architecture

## Future Transport

- UDP support
- TCP/UDP transport selection
- Transport abstraction

## Additional Modules

Possible modules include:

```text
TEXT
SYSTEM
IMAGE
FILE
AUDIO
COMMAND
```

## Embedded Communication

A long-term goal is to implement Coms on microcontrollers and create dedicated devices capable of communicating over a local network.

The protocol architecture is being designed with this possibility in mind.

---

# Security Note

The current Version 1 implementation should be treated as an educational and experimental networking project.

The protocol currently provides **structure and validation**, but not cryptographic security.

In particular:

> Protocol validation is not the same thing as authentication or encryption.

A future secure version should address:

- Confidentiality
- Integrity
- Authentication
- Device identity
- Replay protection
- Key management

These should be implemented deliberately rather than added as superficial features.

---

# License

See `LICENSE` for the terms under which this project is distributed.

---

# Version

**Coms TCP Layer — Version 1**

Status:

```text
FOUNDATIONAL IMPLEMENTATION
```

Core TCP communication: **Complete**

Packet framing: **Complete**

JSON protocol: **Complete**

Module architecture: **Implemented**

Basic validation: **Implemented**

Basic timeout/error handling: **Implemented**

Security hardening: **Future work**

UDP: **Future work**

Embedded/microcontroller implementation: **Future work**
