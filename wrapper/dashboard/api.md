Built with Flask-RESTful. This API must be well-structured, with reusable components and well-designed endpoints.

Authentication will be handled with Flask-Login or a manually-generated API key from within the dashboard.

# Functionality Scope
- Server status and controls
    - Start/stop server
    - View server status (e.g. online/offline, version, memory usage, etc.) [Streamable from SocketIO]
    - View server logs [Streamable from SocketIO]
    - Change server settings
        - server.properties
        - java options
        - whitelist
    - Chat history [Streamable from SocketIO]
- View players and their stats [Streamable from SocketIO]
    - View player list
    - View player stats
    - Kick players
    - Ban players
    - Mute players
- Manage backups
    - Current backup status, if any [Streamable from SocketIO]
    - View backup list
    - Manually trigger a backup
    - Delete backups
- Manage plugins
    - View plugin list
    - Reload plugins
- Manage wrapper.py's own settings

# Authentication

All endpoints require authentication via token. Include the token in the Authorization header.

# Resources
All resources are represented as JSON objects. Resources make for reusable building blocks of this API.

## Response

This is the root response object. It indicates success or failure, and a payload of data specific to the request. All requests return a response object.

Successful example (200 OK): 
```json
{
    "success": true | false,
    "payload": <any, optional>
}
```

Error example (can be any non-2xx HTTP status code):

```json
{
    "success": false,
    "payload": <any, optional>,
    "error": <Error>
}
```

## Error

```json
{
    "message": "Error message", # Human-readable error message specific to the error
    "code": -1 # Internal error code, separate from HTTP status codes
}
```

## Player
```json
{
    "username": "<String: Player's username>",
    "uuid": "<UUID>",
    "online": true | false,
    "minecraft": {
        "position": <Position>,
        "skin": <Skin>,
        "op": true | false
    }
}
```

## PlayerStats

A player's stats are represented as a JSON object with the following properties:

```json
{
    "first_login": <Unix Timestamp>,
    "last_login": <Unix Timestamp>,
    "total_playtime_seconds": <Integer>,
    "login_history": <Array of PlayerLogin objects>
}
```

## PlayerLogin

A login is represented as a JSON object with the following properties:

```json
{
    "logged_in": <Unix Timestamp>,
    "logged_out": <Unix Timestamp>,
    "ip_address": "<String: IP address>"
}
```

## Server

The server object is represented as a JSON object with the following properties:

```json
{
    "status": "stopped" | "starting" | "running" | "stopping" | "frozen",
    "version": "<String: Minecraft server version>",
    "cpu_usage": <Integer: CPU usage percentage>,
    "memory_usage": <Integer: Memory usage in bytes>,
    "players": <Array of Player objects>,
}
```

## Chat

A chat message is represented as a JSON object with the following properties:

```json
{
    "player": "<Player>",
    "message": "<String: Chat message>",
    "timestamp": <Unix Timestamp>
}
```

# Custom Types
Types that aren't completely self-explanatory, like Strings, Integers, etc.

## UUID

A UUID is represented as a string of 32 hexadecimal characters, with dashes inserted at the 8th, 12th, 16th, and 20th positions. Used for player UUIDs, as well as other UUID-based identifiers.

```json
"123e4567-e89b-12d3-a456-426614174000"
```

## Unix Timestamp

A Unix timestamp is a 32-bit integer that represents the number of seconds since the Unix epoch (January 1, 1970).

```json
1710332400
```

## Position

A position is represented as a 3-element array, with the first element being the X coordinate, the second being the Y coordinate, and the third being the Z coordinate.

```json
[100, 100, 100]
```

## Skin

A Minecraft skin is represented as a URL.

```json
"https://minecraft.net/path/to/skin.png"
```

# Endpoints

All endpoints return a [Response](#response) object, and may return a payload of data specific to the request. 

If no payload is specified, the payload will be `null`. If successful, the response will be a 2xx HTTP status code, and if an error occurs, the response will be a non-2xx HTTP status code and an error payload. See [Error](#error) for more details.

Input, if provided, must be sent as JSON in the request body as `application/json`.

## GET /v1/server

Returns the server object, which contains the server's status, as well as other useful information.

### Payload
```
<Server>
```

## GET /v1/server/properties

Returns the parameters of server.properties.

### Payload
```
{
    "name": "<String: Name of the server>",
    "icon": "<String: URL to server icon>",
    "max_players": <Integer>,
    "online_mode": true | false,
    "server_ip": "<String: Server IP address>",
    "server_port": <Integer>,
    "whitelist": true | false,
    "whitelist_players": <Array of Player objects>,
    "accepts_transfers": true | false,
    "allow_flight": true | false,
    "allow_nether": true | false,
    "difficulty": "easy" | "normal" | "hard",
    "enable_command_block": true | false,
    "enable_query": true | false,
    "enable_rcon": true | false,
    "entity_broadcast_range_percentage": <Integer>,
    "resource_pack": "<String: URL to resource pack>",
    "resource_pack_id": "<String: Resource pack ID>",
    "resource_pack_prompt": "<String: Resource pack prompt>",
    "resource_pack_sha1": "<String: Resource pack SHA-1>",
    "force_gamemode": true | false,
    "gamemode": "survival" | "creative" | "adventure" | "spectator",
    "generate_structures": true | false,
    "hardcore": true | false,
    "log_ips": true | false,
    "max_players": <Integer>,
    "motd": "<String: Message of the day>",
    "pvp": true | false,
    "view_distance": <Integer>,
    "white_list": true | false
}
```

## PATCH /v1/server/properties

Updates the server's properties. Any properties that are not specified in the input payload will be left unchanged.

### Input Payload
```
{
    <any>
}
```

## GET /v1/server/java

Returns the Java options for the server.

### Payload
```
{
    "bin": "<String: Path to Java binary>",
    "xms": <Integer>,
    "xmx": <Integer>,
}
```

## PATCH /v1/server/java

Updates the server's Java options. Any options that are not specified in the input payload will be left unchanged.

### Input Payload
```
{
    <any>
}
```

## GET /v1/server/whitelist

Returns the whitelist.

### Payload
```
<Array of Player objects>
```

## PATCH /v1/server/whitelist

Updates the whitelist. Any players that are not specified in the input payload will be removed from the whitelist.

### Input Payload
```
<Array of UUIDs>
```

## GET /v1/server/banned

Returns the banned players.

### Payload
```
<Array of Player objects>
```

## GET /v1/server/ops

Returns the operators.

### Payload
```
<Array of Player objects>
```

## PATCH /v1/server/ops

Updates the operators. Any players that are not specified in the input payload will be removed from the operators.

### Input Payload
```
<Array of UUIDs>
```

## GET /v1/server/logs

Returns the server's logs.

### Payload
```
<Array of Log objects>
```

## GET /v1/server/chat

Returns the server's chat history, since the server was started. If the history exceeds 1000 messages, the oldest messages will be discarded.

#### Payload
```
<Array of Chat objects>
```

## GET /v1/server/players

Returns the list of players currently on the server.

### Payload
```
<Array of Player objects>
```

## GET /v1/players

Returns the list of all players that ever logged into the server.

### Payload
```
<Array of Player objects>
```

## GET /v1/players/<UUID>

Returns the player object for a given player UUID.

### Payload
```
<Player>
```

## GET /v1/players/<UUID>/stats

Returns the stats of a player.

### Payload
```
<PlayerStats>
```