# UI

The frontend will consist of a single-page Vue application that allows for the management of wrapper.py and the server. It is built using Vue.js and Tailwind CSS.

The API will be interacted with using /static/js/wrapper-api.js.

# Design

Modern, clean, intuitive. Extremely desktop and mobile friendly. Dark and light themes available. Tight, information dense when appropriate; use stylistic fonts and sizes to inutitively convey data and controls. Touchscreen friendly. Try to avoid a "scrolly" webpagey UI, and instead focus on tabs, proper UI navigation practices, etc.

# Layout

The dashboard is organized into several key sections:

## Left-side Navigation Bar
Always-visible on desktop viewports, mobile can open via an easily accessible hamburger menu or gesture.

- Server name
- Quick server status indicator (green for running, red for stopped, yellow for starting/stopping)
- User account/settings menu
- Navigation menu

## Landing Dashboard (Grid Layout)

### 1. Server Control Panel (Top Left)
- Prominent power control buttons:
  - Start
  - Stop
  - Restart
  - Freeze
  - Force Stop/Kill
- Current server status details:
  - Uptime
  - CPU usage
  - Memory usage
  - Player count
  - Graph showing temporal history of RAM/CPU/player count, and points for any moments when server output tick lag warnings
- Quick actions:
  - Backup
  - Save

### 2. Live Chat Area (Bottom Left)
- Real-time server chat feed
- Chat input field with command autocomplete
- Toggle buttons for:
  - System messages
  - Player chat
  - Commands
- Chat history search
- Auto-scroll toggle

### 3. Player Management (Right Side)
- Current player list with:
  - Player avatars
  - Online time
  - Ping/latency
  - Quick actions (kick, ban, op)
- Online/offline player toggle
- Player search
- Basic player statistics

## "Config" page
Interface (tabbed to consolidate on smaller viewports) for different configuration categories:
- Java Settings:
  - Memory allocation
  - JVM arguments
  - Java version
- Server Settings:
  - Comprehensive GUI for editing server.properties with descriptions
  - Common-sense sub-navigation (underneath page's root nav) for organization
  - Quick-edit area common properties
  - Server Jar manager
    - Download vanilla jars quickly from Mojang directly
    - Download Spigot/Vanilla/Sponge/etc. directly
    - Delete existing jars

## "World" page
...TBD...

## "Players" page
- Maangement of all players ever logged into server
- Search/filter
- Open Player detail modals

## "Backups" page
...TBD...

## Responsive Design Considerations
- Collapsible sidebars for mobile view
- Responsive UI that feels suitable for smaller screens
- Touch-friendly controls
- Persistent essential controls in mobile view

## Reusale Modal Windows
- Detailed Player management
- Advanced configuration text editors (JSON, YAML, etc.)
- Console output viewer & log viewer w/ search & filter

## Quick Access Features
- Keyboard shortcuts for common actions
- Customizable dashboard layout
- Pinnable favorite commands/actions
- Context menus for quick actions