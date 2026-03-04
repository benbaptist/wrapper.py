# Dashboard

The dashboard is a web interface for managing wrapper.py and the server. It is built using Flask-SocketIO, Vue.js, and Tailwind CSS.

## API

The API is a RESTful API that allows for the management of wrapper.py and the server. It is built using Flask-RESTful. See api.md for more information.

## Frontend

The frontend is a single-page application that allows for the management of wrapper.py and the server. It is built using Vue.js and Tailwind CSS.

- Code should be as minimal as possible while achieving the goals
- Trust the server's responses; no overzealous response cleansing & handling
- SOLID DRY KISS, baby!

## Structure

- `api/`: The API is built using Flask-RESTful. See api.md for more information.
- `io/`: The SocketIO methods will be stored here.
- `frontend/`: The frontend is built using Vue.js and Tailwind CSS.
- `__init__.py`: imports dashboard
- `dashboard.py`: The main Flask initialization file
