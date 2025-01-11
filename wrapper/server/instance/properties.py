from typing import Any, Dict, Optional
import os
import logging

logger = logging.getLogger("wrapper.properties")

class Properties:
    """Manages Minecraft server.properties with validation and disk synchronization."""
    
    # Define property types and valid ranges/values
    PROPERTY_VALIDATORS = {
        "server-port": lambda x: isinstance(x, int) and 1 <= x <= 65535,
        "max-players": lambda x: isinstance(x, int) and x > 0,
        "view-distance": lambda x: isinstance(x, int) and 3 <= x <= 32,
        "difficulty": lambda x: x in ["peaceful", "easy", "normal", "hard"],
        "gamemode": lambda x: x in ["survival", "creative", "adventure", "spectator"],
        "level-seed": lambda x: isinstance(x, (str, int)),
        "online-mode": lambda x: isinstance(x, bool),
        "enable-command-block": lambda x: isinstance(x, bool),
        "motd": lambda x: isinstance(x, str),
        "allow-flight": lambda x: isinstance(x, bool),
        "allow-nether": lambda x: isinstance(x, bool),
        "broadcast-console-to-ops": lambda x: isinstance(x, bool),
        "broadcast-rcon-to-ops": lambda x: isinstance(x, bool),
        "bug-report-link": lambda x: isinstance(x, str),
        "enable-jmx-monitoring": lambda x: isinstance(x, bool),
        "enable-query": lambda x: isinstance(x, bool),
        "enable-rcon": lambda x: isinstance(x, bool),
        "enable-status": lambda x: isinstance(x, bool),
        "enforce-secure-profile": lambda x: isinstance(x, bool),
        "enforce-whitelist": lambda x: isinstance(x, bool),
        "function-permission-level": lambda x: isinstance(x, int) and 0 <= x <= 4,
        "generate-structures": lambda x: isinstance(x, bool),
        "hardcore": lambda x: isinstance(x, bool),
        "initial-disabled-packs": lambda x: isinstance(x, str),
        "initial-enabled-packs": lambda x: isinstance(x, str),
        "level-name": lambda x: isinstance(x, str),
        "level-type": lambda x: isinstance(x, str),
        "log-ips": lambda x: isinstance(x, bool),
        "max-chained-neighbor-updates": lambda x: isinstance(x, int) and x >= 0,
        "max-tick-time": lambda x: isinstance(x, int) and x >= 0,
        "max-world-size": lambda x: isinstance(x, int) and x > 0,
        "network-compression-threshold": lambda x: isinstance(x, int) and x >= 0,
        "op-permission-level": lambda x: isinstance(x, int) and 0 <= x <= 4,
        "pause-when-empty-seconds": lambda x: isinstance(x, int) and x >= 0,
        "player-idle-timeout": lambda x: isinstance(x, int) and x >= 0,
        "prevent-proxy-connections": lambda x: isinstance(x, bool),
        "pvp": lambda x: isinstance(x, bool),
        "query.port": lambda x: isinstance(x, int) and 1 <= x <= 65535,
        "rate-limit": lambda x: isinstance(x, int) and x >= 0,
        "rcon.password": lambda x: isinstance(x, str),
        "rcon.port": lambda x: isinstance(x, int) and 1 <= x <= 65535,
        "region-file-compression": lambda x: x in ["deflate", "gzip", "none"],
        "require-resource-pack": lambda x: isinstance(x, bool),
        "resource-pack": lambda x: isinstance(x, str),
        "resource-pack-id": lambda x: isinstance(x, str),
        "resource-pack-prompt": lambda x: isinstance(x, str),
        "resource-pack-sha1": lambda x: isinstance(x, str),
        "server-ip": lambda x: isinstance(x, str),
        "simulation-distance": lambda x: isinstance(x, int) and x >= 1,
        "spawn-animals": lambda x: isinstance(x, bool),
        "spawn-monsters": lambda x: isinstance(x, bool),
        "spawn-npcs": lambda x: isinstance(x, bool),
        "spawn-protection": lambda x: isinstance(x, int) and x >= 0,
        "sync-chunk-writes": lambda x: isinstance(x, bool),
        "text-filtering-config": lambda x: isinstance(x, str),
        "text-filtering-version": lambda x: isinstance(x, int) and x >= 0,
        "use-native-transport": lambda x: isinstance(x, bool),
        "white-list": lambda x: isinstance(x, bool),
    }

    def __init__(self, server_path: str):
        """Initialize the properties manager.
        
        Args:
            server_path: Path to the Minecraft server directory
        """
        self.properties_file = os.path.join(server_path, "server.properties")
        self._properties: Dict[str, Any] = {}
        self._dirty = False
        
        # Load existing properties or create default ones
        self.load()

    def load(self) -> None:
        """Load properties from disk."""
        if not os.path.exists(self.properties_file):
            logger.warning("server.properties not found, will create with defaults")
            self._dirty = True
            return

        try:
            with open(self.properties_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        # Convert string values to appropriate types
                        if value.lower() == "true":
                            value = True
                        elif value.lower() == "false":
                            value = False
                        elif value.isdigit():
                            value = int(value)
                        self._properties[key] = value
            self._dirty = False
        except Exception as e:
            logger.error(f"Failed to load server.properties: {e}")
            raise

    def save(self) -> None:
        """Save properties to disk if they've been modified."""
        if not self._dirty:
            return

        try:
            # Create backup of existing file
            if os.path.exists(self.properties_file):
                backup_path = f"{self.properties_file}.bak"
                os.replace(self.properties_file, backup_path)

            with open(self.properties_file, "w", encoding="utf-8") as f:
                for key, value in sorted(self._properties.items()):
                    f.write(f"{key}={str(value).lower()}\n")
            
            self._dirty = False
            logger.info("Saved server.properties")
        except Exception as e:
            logger.error(f"Failed to save server.properties: {e}")
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """Get a property value.
        
        Args:
            key: Property name
            default: Default value if property doesn't exist
            
        Returns:
            Property value or default if not found
        """
        return self._properties.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a property value with validation.
        
        Args:
            key: Property name
            value: Property value
            
        Raises:
            ValueError: If the value is invalid for the property
        """
        if key in self.PROPERTY_VALIDATORS:
            validator = self.PROPERTY_VALIDATORS[key]
            if not validator(value):
                raise ValueError(f"Invalid value for {key}: {value}")

        if self._properties.get(key) != value:
            self._properties[key] = value
            self._dirty = True
            self.save()  # Auto-save on change

    @property
    def dirty(self) -> bool:
        """Check if properties have been modified since last server start."""
        return self._dirty

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access to properties."""
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dictionary-style setting of properties."""
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        """Allow 'in' operator for properties."""
        return key in self._properties
