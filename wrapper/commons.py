SERVER_STARTING= 0x00
SERVER_STARTED = 0x01
SERVER_STOPPING = 0x02
SERVER_STOPPED = 0x03
SERVER_ERROR = 0x04
SERVER_FROZEN = 0x05
SERVER_RESTART = 0x06

BACKUP_STARTED = 0x10
BACKUP_COMPLETE = 0x11
BACKUP_FAILED = 0x12
BACKUP_CANCELED = 0x13

COLOR_BLACK = "0"
COLOR_DARK_BLUE = "1"
COLOR_DARK_GREEN = "2"
COLOR_DARK_CYAN = "3"
COLOR_DARK_RED = "4"
COLOR_PURPLE = "5"
COLOR_GOLD = "6"
COLOR_GRAY = "7"
COLOR_DARK_GRAY = "8"
COLOR_BLUE = "9"
COLOR_BRIGHT_GREEN = "a"
COLOR_CYAN = "b"
COLOR_RED = "c"
COLOR_PINK = "d"
COLOR_YELLOW = "e"
COLOR_WHITE = "f"

STYLE_RANDOM = "k"
STYLE_BOLD = "l"
STYLE_STRIKETHROUGH = "m"
STYLE_UNDERLINED = "n"
STYLE_ITALIC = "o"
STYLE_RESET = "r"

# Translate byte size to human-readable size
def bytes_to_human(bytesize, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(bytesize) < 1024.0:
            return "%3.1f%s%s" % (bytesize, unit, suffix)
        bytesize /= 1024.0
    return "%.1f%s%s" % (bytesize, "Yi", suffix)

# Divide string
def args(i, string):
    try:
        return string.split(" ")[i]
    except:
        return

def args_after(i, string):
    try:
        return " ".join(string.split(" ")[i:])
    except:
        return

# Encode JSON chat objects
# https://wiki.vg/Chat
def str_to_json(string):
    extra = []

    b = ""
    style = None
    color = "white"
    escaped = False

    def pack():
        extra.append({
            "text": b,
            "color": color
        })
        b = ""

    for c in string:
        if escaped:
            if c == COLOR_WHITE:
                color = "white"
            elif c == COLOR_BLACK:
                color = "black"
        elif c == "&":
            escaped = True
        else:
            b += c

    return json.dumps({
        "extra": extra
    })

CONFIG_TEMPLATE = {
    "general": {
        "debug-mode": True
    },
    "server": {
        "jar": "server.jar",
        "arguments": "",
        "auto-restart": True,
        "custom-java-bin": None
    },
    "dashboard": {
        "enable": False,
        "bind": {
            "ip": "127.0.0.1",
            "port": 8025
        },
        "root-password": None
    },
    "scripts": {
        "enable": False,
        "scripts": {
            "server-started": None,
            "server-stopped": None,
            "backup-start": None,
            "backup-complete": None,
            "player-join": None,
            "player-part": None
        }
    },
    "backups": {
        "enable": False,
        "archive-format": {
            "format": "auto",
            "compression": {
                "enable": True
            }
        },
        "history": 50,
        "interval-seconds": 600,
        "only-backup-if-player-joins": True,
        "destination": "backups",
        "ingame-notification": {
            "enable": True,
            "only-ops": False,
            "verbose": False,
            "type": "action_bar"
        },
        "backup-mode": "auto",
        "include": {
            "world": True,
            "logs": False,
            "server-properties": False,
            "wrapper-data": True,
            "whitelist-ops-banned": True
        },
        "include-paths": ["wrapper-data"]
    }
}
