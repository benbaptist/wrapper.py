## 2020-09-26
- Features:
    - Implemented "Players" tab
    
- Fixed:
    - `wrapper.server.all_players` throwing AttributeErrror

## 2020-09-21
- Features:
    - Slightly improved Backups page design, added "Delete" button
    - Improved Overview tab

- Attempted to fix list_players() issues

## 2020-09-18
- Features:
    - Backups page partially implemented

## 2020-09-16
- Features:
    - Pre-1.7 server support (very experimental and unstable)

- Various bug fixes

## 2020-09-15
- Features:
    - RAM configuration settings

- Fixed:
    - Changing "Override Command" in web interface changed Custom Jar Name instead
    - Loop when server jar doesn't exist

## 2020-09-14
- Features:
    - Implemented server jar downloader
    - Server configurations

- API Changes:
    - Added Minecraft versions API to Mojang class

## 2020-06-06
- Fixed:
    - Crash on start when 'cmd' configuration setting is set to null
    - [#4] Crash when user runs tp command on player

## 2020-06-03
- Added "cmd" configuration setting to override server command

## 2020-05-31
- Fixed `player.position` always timing out due to a deadlock (by making all commands threaded)

## 2020-05-28
- Re-implemented `player.position`, now polls for position upon request
- Cleanup
- Added optional CLI arguments
    - --ignore-config-updates: Prevent Wrapper from halting when configuration file updates

## 2020-05-13
- Implementing world/chunks stuff

## 2020-04-30 / 0.0.5
- Fixed:
    - Duplicate player objects when joining/parting multiple times
    - Directory plugins (__init__.py) not loading

## 2020-04-28 / 0.0.4
- Fixed:
    - Crash when player runs command
    - Backup crashes/problems

## 2020-04-24 / 0.0.3
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
    - Backups causing crash
    - Fatal errors causing infinite loop

## 2020-04-23
- Added world object to server

## 2020-04-10
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
