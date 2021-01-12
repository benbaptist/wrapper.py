# Design Goals #
- Quick setup
- Robust, stable, set-it-and-forget-it design
    - Wrapper should always be able to start without user input (e.g. with a physical server boot)
    - Updates to Wrapper should never intrude or require user input to fix problems
    - Resilient to corruption, should repair itself
- No excess of functionality; only bare bone features will be implemented
- As few dependencies needed to operate
- Plugin API, to supplement any specific features or use cases not built into the wrapper
- Python 2.x and 3.x compatible

# Major To-Do #

- [x] Wrapper shuts down on first start, to allow user to edit generated config file
    - [x] Interactive first-time setup wizard

- [PARTIAL] Implement backup system
    - [x] Support various containers (zip, tar, 7z, etc.) and compression methods (gzip, etc.)
    - [x] Don't backup if server has been in stopped state
    - [x] Option to stop backup if no players have logged in
    - [ ] Automatic world rollback through dashboard
- [x] Implement shell script calls
- [x] Implement dashboard using Flask
    - [ ] Multi-user support with permissions
- [x] Implement plugin API
    - [x] Server object
        - [x] Minecraft object
        - [x] World object
        - [x] Player object
        - [ ] (if proxy mode is implemented) Entity object
- [ ] Implement server.properties hijacking (temporarily replace server.properties with custom values before starting server, and putting original one back after server booted)
- [ ] Implement Proxy mode
    - Utilize the [Quarry](https://github.com/barneygale/quarry) project to implement Minecraft's protocol

# Minor/Specific To-Do List #
- [ ] Server
    - [x] MCServer object's life should only be during the server's life; once the server stops, the MCServer object should be destroyed. A new one should be created when the server is started again
    - [x] Decouple console parsing from MCServer
    - [ ] Throttle server start attempts if failing to start (i.e. invalid CLI arguments, wrong server jar name, etc.)
    - [x] Respect arguments
    - [x] Respect auto-restart
    - [x] Custom java executable
    - [x] Auto-accept EULA
    - [x] Automatically turn on gamerule to hide command runs from ops, to prevent chat spam
    - [x] Pre-1.7 (or whatever version) server console parsing (e.g. `[11:11:11] [INFO] ...`)
- [ ] Log Management
    - [x] Rotate logs
    - [x] Compress old logs using gzip
    - [x] Respect debug-mode settings
- [ ] Backups
    - [ ] Respect ingame-notification settings
    - [ ] Ability to mark a backup as "important", so it does not auto-delete during rotation
    - [ ] Backups page should be dynamically loaded, show progress bar if during a B/U
- [ ] Dashboard
    - [ ] Localize MaterializeCSS dependencies (don't use CDN)
    - [ ] "400 Bad request" thru nginx proxy
    - [ ] Occasional deadlock condition shortly after starting
    - [ ] Get rid of SocketIO bull crap. Too unreliable and crappy. Bah! (No idea what I meant when I wrote this)
    - [ ] Server jar downloader only works for versions 1.2 and over
- [ ] Plugins / API
    - [ ] Permissions handling for commands
- [ ] Player object
    - [x] Check if operator on vanilla server
    - [x] Make peristent (accessible when offline)
        - [x] Persistent storage
        - [ ] Delete persistent player objects if too many are used
- [ ] Misc. stuff
    - [ ] Make {"text": ""} objects universally encoded [what? no idea what I meant here. Sometimes I drink while programming...]
    - [ ] Use curses to make console input a little nicer

# Plugin Ideas #
- [x] Essentials Clone
- [ ] IRC bridge plugin
