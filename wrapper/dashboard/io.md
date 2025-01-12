This will be the documentation that contains the SocketIO methods for the dashboard.

# Resources

All resources are shared from the RESTful API.

## Subscribable Methods

The following methods can be subscribed to via SocketIO:

- `server`: Stream the current status of the server (online/offline, version, memory usage, etc.).
- `logs`: Stream the server logs in real-time.
- `chat`: Stream the chat history as it occurs.
- `players`: Stream updates on player status (join/leave events, player stats).
- `backups`: Stream the current status of backups, including completion notifications.

These methods allow clients to receive real-time updates and notifications from the server, enhancing the interactivity of the dashboard.
