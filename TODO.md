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
    - Eventually, interactive first-time setup

- [PARTIAL] Implement backup system
    - [x] Support various containers (zip, tar, 7z, etc.) and compression methods (gzip, etc.)
    - [x] Don't backup if server has been in stopped state
    - [x] Option to stop backup if no players have logged in
    - [ ] Automatic world rollback through dashboard
- [x] Implement shell script calls
- [x] Implement dashboard using Flask
    - [ ] Multi-user support with permissions
- [ ] Implement plugin API
    - [ ] Server object
        - [ ] Minecraft object
        - [ ] World object
        - [ ] Player object
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
    - [ ] Pre-1.7 server console parsing (e.g. `[11:11:11] [INFO] ...`)
- [ ] log_manager
    - [PARTIAL] Rotate logs
    - [x] Compress old logs using gzip
    - [x] Respect debug-mode settings
- [ ] Backups
    - [x] Purge old backups
    - [ ] Respect ingame-notification settings
    - [x] Console commands for controlling backups
    - [x] Ability to cancel ongoing backup
- [ ] Dashboard
    - [ ] Localize MaterializeCSS dependencies (don't use CDN)
- [ ] Plugins / API
    - [x] Events need to unhook upon plugin reload
    - [ ] Commands need to un-register upon plugin reload
    - [x] Rename player.message to something else, so that player.message can be used to send the player a message
- [ ] Misc. stuff
    - [ ] Make {"text": ""} objects universally encoded
    - [ ] Use curses to make console input a little nicer

# Plugin Ideas #
- [ ] Essentials Clone
- [ ] IRC bridge plugin
