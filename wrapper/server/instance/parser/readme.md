# Log Events

`[16:39:07] [Server thread/INFO]: Starting minecraft server version 1.21.4`
`[16:39:07] [Server thread/INFO]: Starting Minecraft server on *:25565`
`[16:39:07] [Server thread/INFO]: Preparing level "world"`
`[16:39:08] [Server thread/INFO]: Done (0.977s)! For help, type "help"`
`[16:41:42] [Server thread/INFO]: [Not Secure] <benbaptist> test`
`[16:41:42] [Server thread/INFO]: benbaptist lost connection: Disconnected`
`[16:42:43] [Server thread/INFO]: [benbaptist: Teleported benbaptist to benbaptist]`
`[16:42:43] [Server thread/INFO]: The server will make no attempt to authenticate usernames. Beware.`

# Parsing Layers

- Version-determination; assume latest version until server announces version
- Breakdown timestamp, logging level, etc. into separate parts
    - e.g. for latest version (1.21.4): [12:34:56] [Server thread/INFO]: Preparing level "world"
        - [12:34:56] -> timestamp
        - [Server thread/INFO] -> logging level
        - Preparing level "world" -> message
    - 
- Breakdown message into separate parts
    - e.g. Preparing level "world"
        - Preparing level -> action
        - world -> target
    - e.g. <benbaptist> ohai
        - <benbaptist> -> player
        - ohai -> message
    - e.g. benbaptist[/192.168.1.92:57264] logged in with entity id 44 at (114.97037721541847, 81.0, 21.69999998807907)
        - benbaptist -> player.username
        - 192.168.1.92 -> player.ip_address
        - 44 -> player.entity_id
        - (114.97037721541847, 81.0, 21.69999998807907) -> player.position

# Event Structure

## Template
{
    "timestamp": int: unix timestamp,
    "logging_level": str: logging level,
    "message": str: message from console, unparsed,
    "event": {
        "name": str: event name,
        "data": dict: event data, if applicable
    }
}

## Example Events

### Player Join
{
    "timestamp": "12:34:56",
    "logging_level": "INFO",
    "message": "Preparing level world",
    "event": {
        "name": "player.join",
        "data": {
            "player": {
                "username": "benbaptist",
                "ip_address": "192.168.1.92",
                "entity_id": 44,
                "position": (114.97037721541847, 81.0, 21.69999998807907)
            }
        }
    }
}

### Player Message
{
    "timestamp": "12:34:56",
    "logging_level": "INFO",
    "message": "<benbaptist> ohai",
    "event": {
        "name": "player.message",
        "data": {
            "player": "benbaptist",
            "message": "ohai"
        }
    }
}