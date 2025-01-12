from flask import Flask
from flask_restful import Api
from flask_socketio import SocketIO
from flask_login import LoginManager
import threading

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'  # TODO: Make this configurable

# Initialize extensions
api = Api(app)
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager()
login_manager.init_app(app)

# Import routes after app initialization to avoid circular imports
from .api import routes
from .io import events
from .auth import migrate_passwords

def init_app(wrapper):
    """Initialize the dashboard with the wrapper instance."""
    app.wrapper = wrapper
    
    # Initialize event hooks
    events.init_events(wrapper)
    
    # Migrate passwords to sha256_crypt if needed
    migrate_passwords()
    
    # Start dashboard server if enabled
    if wrapper.config["dashboard"]["enable"]:
        bind_ip = wrapper.config["dashboard"]["bind"]["ip"]
        bind_port = wrapper.config["dashboard"]["bind"]["port"]
        
        # Start in a separate thread to not block the main wrapper
        def run_server():
            socketio.run(app, host=bind_ip, port=bind_port)
        
        dashboard_thread = threading.Thread(target=run_server)
        dashboard_thread.daemon = True  # Thread will be killed when main process exits
        dashboard_thread.start()
        
        wrapper.log.info(f"Dashboard started on http://{bind_ip}:{bind_port}")
    
    return app, socketio 