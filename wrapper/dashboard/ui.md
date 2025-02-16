# UI

The frontend will consist of a single-page application that allows for the management of wrapper.py and the server. It is built using Vue.js and Tailwind CSS.

The API will be interacted with using /static/js/wrapper-api.js.

# Design

The dashboard follows a modern, clean, and intuitive design philosophy with a focus on functionality and user experience. The color scheme should be dark-themed by default (with light theme option) to reduce eye strain during long server management sessions.

# Layout

The dashboard is organized into several key sections:

## Top Navigation Bar
- Server selection dropdown (if multiple servers are configured)
- Quick server status indicator (green for running, red for stopped, yellow for starting/stopping)
- User account/settings menu
- Theme toggle (dark/light)

## Main Content Area (Grid Layout)

### 1. Server Control Panel (Top Left)
- Prominent power control buttons:
  - Start
  - Stop
  - Restart
  - Freeze
- Current server status details:
  - Uptime
  - CPU usage
  - Memory usage
  - Player count
  - TPS (Ticks Per Second)
- Quick actions:
  - Backup
  - Force stop
  - Schedule restart

### 2. Live Chat Area (Center/Right, Expandable)
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

### 4. Server Configuration (Bottom Left)
Tabbed interface for different configuration categories:
- Java Settings:
  - Memory allocation
  - JVM arguments
  - Java version
- Server Properties:
  - Essential properties with descriptions
  - Search/filter options
  - Quick-edit common properties
- Backup Settings:
  - Backup schedule
  - Retention policy
  - Backup location

### 5. Performance Monitoring (Bottom Right)
- Real-time graphs for:
  - TPS history
  - Memory usage
  - Player count
  - Chunk loading
- Performance alerts and recommendations

## Responsive Design Considerations
- Collapsible sidebars for mobile view
- Responsive grid that stacks elements on smaller screens
- Touch-friendly controls
- Persistent essential controls in mobile view

## Modal Windows
- Detailed player management
- Advanced configuration editors
- Backup management
- Console output viewer
- Log viewer with search/filter

## Quick Access Features
- Keyboard shortcuts for common actions
- Customizable dashboard layout
- Pinnable favorite commands/actions
- Context menus for quick actions

The layout prioritizes the most commonly used features while keeping advanced options easily accessible. All sections should be collapsible/expandable to allow users to focus on specific aspects of server management as needed.

# etc...