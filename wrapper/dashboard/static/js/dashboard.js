// Initialize charts for performance monitoring
function initializeCharts() {
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                enabled: true,
                mode: 'index',
                intersect: false
            }
        },
        elements: {
            line: {
                tension: 0.1,
                borderWidth: 2
            },
            point: {
                radius: 0,
                hitRadius: 10,
                hoverRadius: 4
            }
        },
        layout: {
            padding: {
                left: 10,
                right: 10,
                top: 10,
                bottom: 10
            }
        },
        interaction: {
            intersect: false,
            mode: 'index'
        },
        scales: {
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    maxRotation: 0
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0, 0, 0, 0.1)'
                }
            }
        }
    };

    // TPS Chart
    const tpsChart = new Chart(
        document.getElementById('tpsChart'),
        {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'TPS',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    fill: true
                }]
            },
            options: {
                ...defaultOptions,
                scales: {
                    ...defaultOptions.scales,
                    y: {
                        ...defaultOptions.scales.y,
                        min: 0,
                        max: 20,
                        title: {
                            display: true,
                            text: 'Ticks per Second'
                        }
                    }
                }
            }
        }
    );

    // Memory Chart
    const memoryChart = new Chart(
        document.getElementById('memoryChart'),
        {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Memory Usage',
                    data: [],
                    borderColor: 'rgb(153, 102, 255)',
                    backgroundColor: 'rgba(153, 102, 255, 0.1)',
                    fill: true
                }]
            },
            options: {
                ...defaultOptions,
                scales: {
                    ...defaultOptions.scales,
                    y: {
                        ...defaultOptions.scales.y,
                        title: {
                            display: true,
                            text: 'Memory (MB)'
                        }
                    }
                }
            }
        }
    );

    // Players Chart
    const playersChart = new Chart(
        document.getElementById('playersChart'),
        {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Players',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    fill: true
                }]
            },
            options: {
                ...defaultOptions,
                scales: {
                    ...defaultOptions.scales,
                    y: {
                        ...defaultOptions.scales.y,
                        min: 0,
                        title: {
                            display: true,
                            text: 'Player Count'
                        }
                    }
                }
            }
        }
    );

    // Chunks Chart
    const chunksChart = new Chart(
        document.getElementById('chunksChart'),
        {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Loaded Chunks',
                    data: [],
                    borderColor: 'rgb(255, 159, 64)',
                    backgroundColor: 'rgba(255, 159, 64, 0.1)',
                    fill: true
                }]
            },
            options: {
                ...defaultOptions,
                scales: {
                    ...defaultOptions.scales,
                    y: {
                        ...defaultOptions.scales.y,
                        title: {
                            display: true,
                            text: 'Chunk Count'
                        }
                    }
                }
            }
        }
    );

    return {
        tpsChart,
        memoryChart,
        playersChart,
        chunksChart
    };
}

// Format time duration
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const remainingSeconds = seconds % 60

    return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
}

// Format bytes to appropriate unit
function formatBytes(bytes) {
    const units = ['B', 'KB', 'MB', 'GB']
    let size = bytes
    let unitIndex = 0

    while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024
        unitIndex++
    }

    return `${size.toFixed(1)} ${units[unitIndex]}`
}

// Initialize Vue app
document.addEventListener('DOMContentLoaded', () => {
    const app = Vue.createApp({
        delimiters: ['[[', ']]'],
        data() {
            return {
                // Server state
                selectedServer: null,
                servers: [],
                serverStatus: 'unknown',
                isServerRunning: false,
                
                // Server stats
                uptime: '0:00:00',
                cpuUsage: 0,
                memoryUsage: 0,
                totalMemory: 0,
                playerCount: 0,
                maxPlayers: 0,
                tps: 20,
                
                // Chat
                chatMessages: [],
                chatInput: '',
                showSystemMessages: true,
                showPlayerChat: true,
                showCommands: true,
                
                // Players
                players: [],
                playerSearch: '',
                
                // Configuration
                configTabs: [
                    { id: 'java', name: 'Java Settings' },
                    { id: 'properties', name: 'Server Properties' },
                    { id: 'backup', name: 'Backup Settings' }
                ],
                activeConfigTab: 'java',
                javaSettings: {
                    memory: '2G',
                    version: '17',
                    args: '-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200'
                },
                javaVersions: ['8', '11', '16', '17', '18', '19'],
                
                // Theme
                isDarkMode: document.documentElement.classList.contains('dark'),
                showUserMenu: false,
                
                // Charts
                charts: null
            }
        },
        computed: {
            statusIndicatorClass() {
                const classes = {
                    'running': 'bg-green-500',
                    'stopping': 'bg-yellow-500',
                    'starting': 'bg-yellow-500',
                    'stopped': 'bg-red-500',
                    'unknown': 'bg-gray-500'
                }
                return classes[this.serverStatus] || classes.unknown
            },
            filteredMessages() {
                return this.chatMessages.filter(msg => {
                    if (msg.type === 'system' && !this.showSystemMessages) return false
                    if (msg.type === 'chat' && !this.showPlayerChat) return false
                    if (msg.type === 'command' && !this.showCommands) return false
                    return true
                })
            },
            filteredPlayers() {
                if (!this.playerSearch) return this.players
                const search = this.playerSearch.toLowerCase()
                return this.players.filter(p => 
                    p.name.toLowerCase().includes(search) ||
                    p.uuid.toLowerCase().includes(search)
                )
            }
        },
        methods: {
            async initialize() {
                this.api = new WrapperAPI()
                await this.setupEventListeners()
                await this.loadInitialData()
                // Initialize charts after Vue is mounted
                this.$nextTick(() => {
                    this.charts = initializeCharts()
                })
            },
            async setupEventListeners() {
                this.api.on('serverStatusChanged', this.handleServerStatusChange)
                this.api.on('chat', this.handleChatMessage)
                this.api.on('playerJoined', this.handlePlayerJoin)
                this.api.on('playerLeft', this.handlePlayerLeave)
            },
            async loadInitialData() {
                try {
                    // Load initial server status
                    const status = await this.api.server.getStatus()
                    this.handleServerStatusChange(status)
                    
                    // Load players
                    const players = await this.api.players.getAll()
                    this.players = players
                    
                    // Load chat history
                    const chat = await this.api.server.getChat()
                    this.chatMessages = chat
                } catch (error) {
                    console.error('Error loading initial data:', error)
                }
            },
            handleServerStatusChange(status) {
                if (!status) return
                
                this.serverStatus = status.status || 'unknown'
                this.isServerRunning = status.status === 'running'
                this.uptime = formatDuration(status.uptime || 0)
                this.cpuUsage = status.cpu_usage || 0
                this.memoryUsage = status.memory_usage || 0
                this.totalMemory = status.total_memory || 0
                this.playerCount = (status.players || []).length
                this.maxPlayers = status.max_players || 20
                this.tps = status.tps || 20
                
                // Update charts
                this.updateCharts(status)
            },
            updateCharts(status) {
                if (!status || !this.charts) return
                
                const time = new Date().toLocaleTimeString()
                const { tpsChart, memoryChart, playersChart, chunksChart } = this.charts
                
                // Update TPS chart
                tpsChart.data.labels.push(time)
                tpsChart.data.datasets[0].data.push(status.tps || 20)
                if (tpsChart.data.labels.length > 20) {
                    tpsChart.data.labels.shift()
                    tpsChart.data.datasets[0].data.shift()
                }
                tpsChart.update()
                
                // Update Memory chart
                memoryChart.data.labels.push(time)
                memoryChart.data.datasets[0].data.push(status.memory_usage || 0)
                if (memoryChart.data.labels.length > 20) {
                    memoryChart.data.labels.shift()
                    memoryChart.data.datasets[0].data.shift()
                }
                memoryChart.update()
                
                // Update Players chart
                playersChart.data.labels.push(time)
                playersChart.data.datasets[0].data.push((status.players || []).length)
                if (playersChart.data.labels.length > 20) {
                    playersChart.data.labels.shift()
                    playersChart.data.datasets[0].data.shift()
                }
                playersChart.update()
                
                // Update Chunks chart
                chunksChart.data.labels.push(time)
                chunksChart.data.datasets[0].data.push(status.chunks || 0)
                if (chunksChart.data.labels.length > 20) {
                    chunksChart.data.labels.shift()
                    chunksChart.data.datasets[0].data.shift()
                }
                chunksChart.update()
            },
            async startServer() {
                try {
                    await this.api.server.start()
                } catch (error) {
                    console.error('Error starting server:', error)
                }
            },
            async stopServer() {
                try {
                    await this.api.server.stop()
                } catch (error) {
                    console.error('Error stopping server:', error)
                }
            },
            async restartServer() {
                try {
                    await this.api.server.restart()
                } catch (error) {
                    console.error('Error restarting server:', error)
                }
            },
            async freezeServer() {
                // Implement freeze functionality
            },
            async sendMessage() {
                if (!this.chatInput.trim()) return
                
                try {
                    if (this.chatInput.startsWith('/')) {
                        await this.api.server.sendCommand(this.chatInput.slice(1))
                    } else {
                        await this.api.server.sendChat(this.chatInput)
                    }
                    
                    this.chatInput = ''
                } catch (error) {
                    console.error('Error sending message:', error)
                }
            },
            handleChatMessage(message) {
                this.chatMessages.push(message)
                // Keep only last 100 messages
                if (this.chatMessages.length > 100) {
                    this.chatMessages.shift()
                }
                
                // Auto-scroll chat
                this.$nextTick(() => {
                    const chatContainer = document.querySelector('.chat-messages')
                    if (chatContainer) {
                        chatContainer.scrollTop = chatContainer.scrollHeight
                    }
                })
            },
            handlePlayerJoin(player) {
                this.players.push(player)
            },
            handlePlayerLeave(player) {
                const index = this.players.findIndex(p => p.uuid === player.uuid)
                if (index !== -1) {
                    this.players.splice(index, 1)
                }
            },
            async kickPlayer(player) {
                if (!player || !player.uuid) {
                    console.error('Invalid player object');
                    return;
                }
                try {
                    await this.api.players.kick(player.uuid);
                } catch (error) {
                    console.error('Error kicking player:', error);
                }
            },
            async banPlayer(player) {
                if (!player || !player.uuid) {
                    console.error('Invalid player object');
                    return;
                }
                try {
                    await this.api.players.ban(player.uuid);
                } catch (error) {
                    console.error('Error banning player:', error);
                }
            },
            async opPlayer(player) {
                if (!player || !player.uuid) {
                    console.error('Invalid player object');
                    return;
                }
                try {
                    await this.api.players.op(player.uuid);
                } catch (error) {
                    console.error('Error opping player:', error);
                }
            },
            toggleTheme() {
                this.isDarkMode = !this.isDarkMode
                document.documentElement.classList.toggle('dark')
                localStorage.theme = this.isDarkMode ? 'dark' : 'light'
            },
            toggleUserMenu() {
                this.showUserMenu = !this.showUserMenu
            },
            async logout() {
                try {
                    await this.api.auth.logout()
                    window.location.href = '/login'
                } catch (error) {
                    console.error('Error logging out:', error)
                }
            }
        },
        mounted() {
            this.initialize()
        }
    }).mount('#app')
}) 