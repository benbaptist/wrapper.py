from flask import jsonify, request
from flask_restful import Resource
from flask_login import login_user, logout_user
from ..auth import require_auth, User, hash_password, verify_user
from .. import api, app

def success_response(payload=None):
    """Standard success response format."""
    return jsonify({
        "success": True,
        "payload": payload
    })

def error_response(message, code=-1, status_code=400):
    """Standard error response format."""
    response = jsonify({
        "success": False,
        "error": {
            "message": message,
            "code": code
        }
    })
    response.status_code = status_code
    return response

class ServerResource(Resource):
    method_decorators = [require_auth]

    def get(self):
        """Get server status and information."""
        instance = app.wrapper.server.instance
        if not instance:
            return success_response({
                "status": "stopped",
                "version": None,
                "cpu_usage": 0,
                "memory_usage": 0,
                "players": []
            })

        return success_response({
            "status": instance.state,
            "version": instance.server_version,
            "cpu_usage": instance.cpu_usage if hasattr(instance, 'cpu_usage') else 0,
            "memory_usage": instance.ram_usage if hasattr(instance, 'ram_usage') else 0,
            "players": [player.__serialize__() for player in instance.players]
        })

    def post(self):
        """Start/stop/restart server."""
        action = request.json.get('action')
        if action not in ['start', 'stop', 'restart']:
            return error_response("Invalid action", code=1)

        server = app.wrapper.server
        try:
            if action == 'start':
                server.start()
            elif action == 'stop':
                server.stop()
            else:  # restart
                server.restart()
            return success_response()
        except Exception as e:
            return error_response(str(e), code=2)

class ServerPropertiesResource(Resource):
    method_decorators = [require_auth]

    def get(self):
        """Get server.properties."""
        instance = app.wrapper.server.instance
        if not instance:
            return error_response("Server not running", code=3)
        
        return success_response(instance.properties._properties)

    def patch(self):
        """Update server.properties."""
        instance = app.wrapper.server.instance
        if not instance:
            return error_response("Server not running", code=3)

        try:
            for key, value in request.json.items():
                instance.properties._properties[key] = value
            instance.properties.save()
            return success_response()
        except Exception as e:
            return error_response(str(e), code=4)

class PlayersResource(Resource):
    method_decorators = [require_auth]

    def get(self):
        """Get all players (online and offline)."""
        instance = app.wrapper.server.instance
        if not instance:
            return error_response("Server not running", code=3)

        return success_response([
            player.__serialize__() for player in instance.list_players(everyone=True)
        ])

class PlayerResource(Resource):
    method_decorators = [require_auth]

    def get(self, uuid):
        """Get specific player information."""
        instance = app.wrapper.server.instance
        if not instance:
            return error_response("Server not running", code=3)

        try:
            player = instance.get_player_(uuid)
            if not player:
                return error_response("Player not found", code=5, status_code=404)
            
            return success_response(player.__serialize__())
        except Exception as e:
            return error_response(str(e), code=6)

class PlayerStatsResource(Resource):
    method_decorators = [require_auth]

    def get(self, uuid):
        """Get player statistics."""
        instance = app.wrapper.server.instance
        if not instance:
            return error_response("Server not running", code=3)

        try:
            player = instance.get_player_(uuid)
            if not player:
                return error_response("Player not found", code=5, status_code=404)
            
            return success_response(player.stats)
        except Exception as e:
            return error_response(str(e), code=6)

class PlayerActionResource(Resource):
    method_decorators = [require_auth]

    def post(self, uuid):
        """Perform action on player (kick, ban, etc)."""
        action = request.json.get('action')
        if action not in ['kick', 'ban', 'unban', 'op', 'deop']:
            return error_response("Invalid action", code=1)

        instance = app.wrapper.server.instance
        if not instance:
            return error_response("Server not running", code=3)

        try:
            player = instance.get_player_(uuid)
            if not player:
                return error_response("Player not found", code=5, status_code=404)

            if action == 'kick':
                reason = request.json.get('reason', 'Kicked by admin')
                instance.api.kick(player.username, reason)
            # TODO: Implement other actions
            
            return success_response()
        except Exception as e:
            return error_response(str(e), code=6)

class LoginResource(Resource):
    def post(self):
        """Handle user login."""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return error_response("Missing username or password", code=7)
            
        if not verify_user(username, password):
            return error_response("Invalid credentials", code=8, status_code=401)
            
        # Login successful
        user = User(username, username)
        login_user(user)
        
        return success_response({
            "username": username
        })

class LogoutResource(Resource):
    @require_auth
    def post(self):
        """Handle user logout."""
        logout_user()
        return success_response()

# Register routes
api.add_resource(ServerResource, '/v1/server')
api.add_resource(ServerPropertiesResource, '/v1/server/properties')
api.add_resource(PlayersResource, '/v1/server/players')
api.add_resource(PlayerResource, '/v1/players/<string:uuid>')
api.add_resource(PlayerStatsResource, '/v1/players/<string:uuid>/stats')
api.add_resource(PlayerActionResource, '/v1/players/<string:uuid>/action')
api.add_resource(LoginResource, '/v1/auth/login')
api.add_resource(LogoutResource, '/v1/auth/logout') 