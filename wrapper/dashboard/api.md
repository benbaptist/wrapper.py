Built with Flask-RESTful. This API must be well-structured, with reusable components and well-designed endpoints.

Authentication will be handled with Flask-Login or with manually-generated API keys managed within the dashboard (with optional expirations).

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

See openapi.yaml for actual API implementation details.