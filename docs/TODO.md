# Major Refactor for 0.2.0
- [ ] Better conformity to PEP8
- [x] Reorganizing codebase
- [x] Huge refactoring of the server and instance modules
- [ ] Complete rewrite of the dashboard (frontend and backend)
- [ ] IDEA: Move towards asynchronous operations (e.g. using eventlet, or asyncio)
- [ ] IDEA: Switch to blitz for event handling, if it's better than the current system

# Major Refactor for 0.3.0
- [ ] Backups overhaul
    - [ ] Native restic support

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
- [ ] Implement server.properties service for modifying the server.properties (permanently) in an abstracted, simple manner for use in configuration UX and the first-time setup wizard
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
    - [ ] Backups page should be dynamically loaded, show progress bar if during a backup
- [ ] Plugins / API
    - [ ] Permissions handling for commands
- [ ] Player object
    - [x] Make peristent (accessible when offline)
        - [x] Persistent storage
        - [ ] Delete persistent player objects if too many are used