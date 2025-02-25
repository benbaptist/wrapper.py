class WrapperAPI {
    constructor() {
        this.eventHandlers = {};
        this.cache = {
            serverStatus: null,
            players: null,
            properties: null
        };
        
        // Initialize modules
        this.server = new ServerModule(this);
        this.auth = new AuthModule(this);
        this.players = new PlayersModule(this);
        
        // Initialize Socket.IO with correct path
        this.socket = io({
            path: '/socket.io'
        });
        this._setupSocketHandlers();
    }

    // Event handling
    on(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }

    off(event, handler) {
        if (!this.eventHandlers[event]) return;
        this.eventHandlers[event] = this.eventHandlers[event].filter(h => h !== handler);
    }

    _emit(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => handler(data));
        }
    }

    _setupSocketHandlers() {
        this.socket.on('server', (data) => {
            const oldStatus = this.cache.serverStatus;
            this.cache.serverStatus = data;
            
            if (!oldStatus || oldStatus.status !== data.status) {
                this._emit('serverStatusChanged', data);
            }

            // Check for player changes
            if (oldStatus) {
                const oldPlayers = new Set(oldStatus.players.map(p => p.uuid));
                const newPlayers = new Set(data.players.map(p => p.uuid));

                // Find joined players
                data.players.forEach(player => {
                    if (!oldPlayers.has(player.uuid)) {
                        this._emit('playerJoined', player);
                    }
                });

                // Find left players
                oldStatus.players.forEach(player => {
                    if (!newPlayers.has(player.uuid)) {
                        this._emit('playerLeft', player);
                    }
                });
            }
        });

        this.socket.on('chat', (data) => {
            this._emit('chat', data);
        });
    }

    // Helper for making API requests
    async _request(method, endpoint, data = null) {
        try {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json'
                }
            };

            if (data) {
                options.body = JSON.stringify(data);
            }

            const baseUrl = '/v1'; // Changed from '/api' to '/v1' to match the actual API structure
            const response = await fetch(`${baseUrl}${endpoint}`, options);
            
            // Handle different response status codes
            if (!response.ok) {
                // Check if response is HTML (likely a redirect to login page)
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('text/html')) {
                    if (response.status === 401 || response.status === 403) {
                        throw new Error('Unauthorized');
                    } else {
                        throw new Error(`Server returned HTML: ${response.statusText}`);
                    }
                }
                
                // Try to parse error as JSON
                try {
                    const errorData = await response.json();
                    if (errorData.error && errorData.error.message) {
                        throw new Error(errorData.error.message);
                    }
                } catch (parseError) {
                    // If we can't parse JSON, just use the status text
                }
                
                throw new Error(response.statusText);
            }

            // Parse successful response
            try {
                return await response.json();
            } catch (parseError) {
                console.error('Error parsing JSON response:', parseError);
                throw new Error('Invalid JSON response from server');
            }
        } catch (error) {
            console.error(`API request failed: ${error.message}`);
            throw error;
        }
    }
}

class ServerModule {
    constructor(api) {
        this.api = api;
        this._lastPlayersFetch = 0;
        this._playersFetchInterval = 5000; // 5 seconds
    }

    get status() {
        return this.api.cache.serverStatus?.status || 'unknown';
    }

    async getStatus() {
        return await this.api._request('GET', '/server');
    }

    async getChat() {
        return await this.api._request('GET', '/chat');
    }

    get players() {
        // If we haven't fetched recently, fetch now
        const now = Date.now();
        if (now - this._lastPlayersFetch > this._playersFetchInterval) {
            this._lastPlayersFetch = now;
            this.api.players.getAll().then(players => {
                this.api.cache.players = players;
            });
        }
        // Return cached players from server status, or full player list if available
        return this.api.cache.players || this.api.cache.serverStatus?.players || [];
    }

    async start() {
        return await this.api._request('POST', '/server/action', { action: 'start' });
    }

    async stop() {
        return await this.api._request('POST', '/server/action', { action: 'stop' });
    }

    async restart() {
        return await this.api._request('POST', '/server/action', { action: 'restart' });
    }

    get properties() {
        if (!this.api.cache.properties) {
            // Fetch properties if not cached
            this.getProperties();
            return {};
        }
        return this.api.cache.properties;
    }

    async getProperties() {
        const props = await this.api._request('GET', '/server/properties');
        this.api.cache.properties = props;
        return props;
    }

    async updateProperties(changes) {
        await this.api._request('PATCH', '/server/properties', changes);
        // Refresh cache
        await this.getProperties();
    }

    async sendChat(message) {
        return await this.api._request('POST', '/server/chat', { message });
    }

    async sendCommand(command) {
        return await this.api._request('POST', '/server/command', { command });
    }
}

class PlayersModule {
    constructor(api) {
        this.api = api;
    }

    async getAll() {
        return await this.api._request('GET', '/players');
    }

    async get(uuid) {
        return await this.api._request('GET', `/players/${uuid}`);
    }

    async getStats(uuid) {
        return await this.api._request('GET', `/players/${uuid}/stats`);
    }

    async kick(uuid) {
        if (!uuid) {
            throw new Error('Player UUID is required');
        }
        return await this.api._request('POST', `/players/${uuid}/action`, { action: 'kick' });
    }

    async ban(uuid) {
        if (!uuid) {
            throw new Error('Player UUID is required');
        }
        return await this.api._request('POST', `/players/${uuid}/action`, { action: 'ban' });
    }

    async unban(uuid) {
        await this.api._request('POST', `/players/${uuid}/action`, {
            action: 'unban'
        });
    }

    async op(uuid) {
        if (!uuid) {
            throw new Error('Player UUID is required');
        }
        return await this.api._request('POST', `/players/${uuid}/action`, { action: 'op' });
    }

    async deop(uuid) {
        await this.api._request('POST', `/players/${uuid}/action`, {
            action: 'deop'
        });
    }
}

class AuthModule {
    constructor(api) {
        this.api = api;
    }

    async login(username, password) {
        console.log('AuthModule.login called with username:', username);
        
        if (!username || !password) {
            throw new Error('Username and password are required');
        }
        
        try {
            console.log('Sending login request to /auth/login');
            const response = await this.api._request('POST', '/auth/login', { 
                username, 
                password 
            });
            
            console.log('Login response:', response);
            
            // Check if the login was successful
            if (response && response.success) {
                console.log('Login successful');
                return response;
            } else {
                console.error('Login failed with response:', response);
                throw new Error(response.error?.message || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    async logout() {
        return await this.api._request('POST', '/auth/logout');
    }
} 