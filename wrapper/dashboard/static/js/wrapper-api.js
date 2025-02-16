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
        
        // Initialize Socket.IO
        this.socket = io();
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

            const response = await fetch(endpoint, options);
            if (!response.ok) {
                throw new Error(response.statusText);
            }

            return await response.json();
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
        return await this.api._request('GET', '/v2/server/status');
    }

    async getChat() {
        return await this.api._request('GET', '/v2/server/chat');
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
        return await this.api._request('POST', '/v2/server/action', { action: 'start' });
    }

    async stop() {
        return await this.api._request('POST', '/v2/server/action', { action: 'stop' });
    }

    async restart() {
        return await this.api._request('POST', '/v2/server/action', { action: 'restart' });
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
        const props = await this.api._request('GET', '/v2/server/properties');
        this.api.cache.properties = props;
        return props;
    }

    async updateProperties(changes) {
        await this.api._request('PATCH', '/v2/server/properties', changes);
        // Refresh cache
        await this.getProperties();
    }

    async sendChat(message) {
        return await this.api._request('POST', '/v2/server/chat', { message });
    }

    async sendCommand(command) {
        return await this.api._request('POST', '/v2/server/command', { command });
    }
}

class PlayersModule {
    constructor(api) {
        this.api = api;
    }

    async getAll() {
        return await this.api._request('GET', '/v2/players');
    }

    async get(uuid) {
        return await this.api._request('GET', `/v2/players/${uuid}`);
    }

    async getStats(uuid) {
        return await this.api._request('GET', `/v2/players/${uuid}/stats`);
    }

    async kick(uuid) {
        if (!uuid) {
            throw new Error('Player UUID is required');
        }
        return await this.api._request('POST', `/v2/players/${uuid}/action`, { action: 'kick' });
    }

    async ban(uuid) {
        if (!uuid) {
            throw new Error('Player UUID is required');
        }
        return await this.api._request('POST', `/v2/players/${uuid}/action`, { action: 'ban' });
    }

    async unban(uuid) {
        await this.api._request('POST', `/v2/players/${uuid}/action`, {
            action: 'unban'
        });
    }

    async op(uuid) {
        if (!uuid) {
            throw new Error('Player UUID is required');
        }
        return await this.api._request('POST', `/v2/players/${uuid}/action`, { action: 'op' });
    }

    async deop(uuid) {
        await this.api._request('POST', `/v2/players/${uuid}/action`, {
            action: 'deop'
        });
    }
}

class AuthModule {
    constructor(api) {
        this.api = api;
    }

    async login(username, password) {
        await this.api._request('POST', '/v2/auth/login', { username, password });
    }

    async logout() {
        await this.api._request('POST', '/v2/auth/logout');
    }
} 