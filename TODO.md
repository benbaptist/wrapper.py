# Major Refactor for 0.2.0
- [ ] Better conformity to PEP8
- [x] Reorganizing codebase
- [x] Huge refactoring of the server and instance modules
- [ ] Complete rewrite of the dashboard (frontend and backend)
- [ ] IDEA: Move towards asynchronous operations (e.g. using eventlet, or asyncio)
- [ ] IDEA: Switch to blitz for event handling, if it's better than the current system

# Design Goals
- Quick setup
- Robust, stable, set-it-and-forget-it design
    - Wrapper should always be able to start without user input (e.g. with a physical server boot)
    - Updates to Wrapper should never intrude or require user input to fix problems
    - Resilient to corruption, should repair itself
- RESTful API & clean web dashboard
- No excess of functionality; only bare bone features will be implemented
- Plugin API, to supplement any specific features or use cases not built into the wrapper
- Python 3.x only

# Major To-Do

- [ ] Implement backup system
    - [ ] Native support for restic backups
    - [ ] Automatic world rollback through dashboard
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
- [ ] Make sure PaperMC/Spigot/etc. console parsing is supported

# Minor To-Do
- [ ] Server
    - [ ] Throttle server start attempts if failing to start (i.e. invalid CLI arguments, wrong server jar name, etc.)
    - [ ] Regression: Need to re-implement pre-1.7 (or whatever version) server console parsing (e.g. `[11:11:11] [INFO] ...`)
    - [ ] FIX: Server jar downloader only works for versions 1.2 and over
- [ ] Backups
    - [ ] Respect ingame-notification settings
    - [ ] Ability to mark a backup as "important", so it does not auto-delete during rotation
    - [ ] Backups page should be dynamically loaded, show progress bar if during a B/U
- [ ] Plugins / API
    - [ ] Permissions handling for commands
- [ ] Player object
    - [x] Make peristent (accessible when offline)
        - [x] Persistent storage
        - [ ] Delete persistent player objects if too many are used
- [ ] Misc. stuff
    - [ ] Make {"text": ""} objects universally encoded (I think I meant having a DataClass for Minecraft's Chat objects)
