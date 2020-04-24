*2020-04-24 / 0.0.3*
- Customize command prefix
- Built-in in-game commands (wrapper, reload)
- Player objects are now persistent (i.e. they remain when player logs off, useful for doing operations on offline players)
    - Persistent database for each player
    - Migrates old-style Wrapper player data (pickled crap)
    - Keeps track of player logins, IPs, etc.
- Events:
    - [server.player.command_response] Vanilla server commands ran by a player
        - This also allows players to see some command responses despite sendCommandFeedback being false
- Fixed:
    - Commands duplicating on plugin reload
*2020-04-23*
- Added world object to server

*2020-04-10*
- `waitress` now an optional dependency
- Most storify.py output is debug-only now, other than critical errors
- Wrapper console output no longer shows date
- Wrapper version number printed on start
- PROTOCOL_VERSIONS
- Added abstraction layer for wrapper-server communication to find best command for a given task for each server version
- Disabled player position polling due to negative consequences
    - Constantly running `tp` on a player causes block placement problems for player, possibly more aggressive rubber banding during times of lag
- Surpressed console output for:
    - "Showing new . for title ."
    - Server reload
- Code cleanup
- Fixed:
    - Dashboard enabled when 'enable' set to false in config
    - Dashboard password not being obfuscated in config file
    - Backups being enabled causing fatal crash
    - `restart` command was not restarting server
    - wrapper.cleanup() method running twice on shutdown
