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
        if (!this.eventHandlers[event]) return;
        this.eventHandlers[event].forEach(handler => handler(data));
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
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`/v1${endpoint}`, options);
        const json = await response.json();

        if (!json.success) {
            throw new Error(json.error.message);
        }

        return json.payload;
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
        await this.api._request('POST', '/server', { action: 'start' });
    }

    async stop() {
        await this.api._request('POST', '/server', { action: 'stop' });
    }

    async restart() {
        await this.api._request('POST', '/server', { action: 'restart' });
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
}

class PlayersModule {
    constructor(api) {
        this.api = api;
    }

    async getAll() {
        return await this.api._request('GET', '/server/players');
    }

    async get(uuid) {
        return await this.api._request('GET', `/players/${uuid}`);
    }

    async getStats(uuid) {
        return await this.api._request('GET', `/players/${uuid}/stats`);
    }

    async kick(uuid, reason = 'Kicked by admin') {
        await this.api._request('POST', `/players/${uuid}/action`, {
            action: 'kick',
            reason
        });
    }

    async ban(uuid) {
        await this.api._request('POST', `/players/${uuid}/action`, {
            action: 'ban'
        });
    }

    async unban(uuid) {
        await this.api._request('POST', `/players/${uuid}/action`, {
            action: 'unban'
        });
    }

    async op(uuid) {
        await this.api._request('POST', `/players/${uuid}/action`, {
            action: 'op'
        });
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
        await this.api._request('POST', '/auth/login', { username, password });
    }

    async logout() {
        await this.api._request('POST', '/auth/logout');
    }
} 