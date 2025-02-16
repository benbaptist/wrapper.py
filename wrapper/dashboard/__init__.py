from flask import Flask, render_template, redirect, url_for, Blueprint
from flask_restful import Api
from flask_socketio import SocketIO
from flask_login import LoginManager, current_user
import threading

# Create Blueprint
dashboard = Blueprint('dashboard', __name__, 
                     template_folder='templates',
                     static_folder='static',
                     static_url_path='/static')

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'  # TODO: Make this configurable
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize extensions
api = Api(app)
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'dashboard.login'

# Import routes after app initialization to avoid circular imports
from .api import routes
from .io import events
from .auth import migrate_passwords, require_auth

@dashboard.route('/')
@require_auth
def index():
    """Render the main dashboard."""
    return render_template('dashboard.html')

@dashboard.route('/login')
def login():
    """Render the login page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('login.html')

@dashboard.route('/test')
def test_page():
    """Render the API test page."""
    return render_template('api_test.html')

def init_app(wrapper):
    """Initialize the dashboard with the wrapper instance."""
    app.wrapper = wrapper
    
    # Register blueprint
    app.register_blueprint(dashboard)
    
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