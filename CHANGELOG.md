## 2024-10-08 / 0.1.17 Alpha
- Updated dependencies
- Fixed:
    - Player disconnect events not firing

## 2023-07-14 / 0.1.16 Alpha
- Bumped required NBT to 1.5.1 (fixes newer Python versions)
- Added 'cmd' backup mode: Lets you run your own backup command

## 2022-12-20 / 0.1.15 Alpha
- Fixed duplicate console lines
- New backup mode "copy": copies path(s) directly to a new folder in the backup location, no archival method used (useful for shadow/de-duplication filesystems)
- Actually implemented zip backups

## 2022-12-16 / 0.1.14 Alpha
- Updated Socket.IO client
- Fixed requirements.txt

## 2022-11-17 / 0.1.13 Alpha
- Fixed:
    - Fatal crash when client doesn't completely connect (when server throws com.mojang crap)
    - Other fatal crashes when parsing doesn't go right
    - Attempts graceful shutdown of Java server now upon a fatal Wrapper crash

## 2022-08-30 / 0.1.12 Alpha
- Fixed:
    - Fatal crashes on modern versions of Minecraft server (or any?)
    - Possible fixes for player list

## 2021-07-06 / 0.1.11 Alpha
- Dashboard:
    - Java Version listed on Overview page
- Fixed:
    - Bootloops when server fails to start
- Technical:
    - Server output now fully read even when shutdown; no lines left behind

## 2021-01-26 / 0.1.10 Alpha
- Fixed:  
    - [#13] Paper-based servers not working with Wrapper.py
- Technical:
    - Player coordinates are now properly grabbed upon login

## 2021-01-12 / 0.1.9 Alpha
- Fixed:
    - Error when loading certain log files
    - Updated Socket.IO dependency to 4.3.2
- Technical:
    - Moved wizard code to wizard.py

## 2021-01-04 / 0.1.8 Alpha
- Fixed:
    - `b"..."` surrounding every log line on Logs page
    - Skinless players showing no face on Players page
    - Small UI fixes & improvements
- Technical:
    - Decreased `player.position` timeout from 2 sec to 1 sec

## 2020-12-12 / 0.1.7 Alpha
- Implemented Logs page
- Testing some weird new layout for the Overview page (it's ugly!)
- UI changes
- Fixed:
    - "backkup" typo
    - Crash on backup complete

## 2020-12-12 / 0.1.6 Alpha
- More Socket.IO stuff added to Backups list page
- Fixed:
    - Can't enable/disable backups from Dashboard
    - Small UI bugs

## 2020-12-07 / 0.1.5 Alpha
- Now serving socket.io.js locally
- Added "storage" chunk to API
- Fixed:
    - Command arguments not passed to plugins
    - Database contexts being duplicated, causing memory leak or conflicting databases
- Added 'coords' command to Essentials plugin

## 2020-10-31 / 0.1.4 Alpha
- Now serving filesize.js locally
- Fixed:
    - "It's a ghost town in here" message not disappearing when players on server
    - Backup causes fatal crash when out of disk space

## 2020-10-31 / 0.1.3 Alpha
- Automatic timed server reboots implemented
- Migrates old Wrapper configuration files during first-time wizard
- Small UI changes
- Fixed:
    - "Backup Mode" on Backup settings page
    - Wrapper doesn't start setup wizard if wrapper-data exists, even if config does not
    - Console suppressing not working

## 2020-10-29 / 0.1.2 alpha
- Added server jar configuration to first-time setup wizard

## 2020-10-15 / 0.1.1 alpha
- Started to implement Configuration page on server page
- Implemented Backup Settings page
- "Start Backup" button functionality added

## 2020-10-05 / 0.1 alpha
- First-time setup wizard
- Pretty little plugin list added to Dashboard
- Minor, cosmetic changes to Dashboard
- Fixed:
    - Players duplicating every time `/players` page was loaded
    - `Internal Server Error` when `/players` page loaded with server off
    - Green card when server was offline on Overview page

## 2020-10-04 / 0.0.7
- Added interactive table to Players page (DataTables)
- Did some stuff with server.get_player - super messy though. ugh.
- Fixed:
    - Wrapper attempting to retrieve skins for offline mode players

## 2020-09-30 / 0.0.6
- Fixed:
    - [Issue #6] Wrapper crash when starting fresh server/world
    - [Issue #7] Running newer, or unsupported Minecraft servers caused weird issues

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
