from curses import wrapper as curses_wrapper
import curses
import sys
import atexit
from queue import Queue
from threading import Lock

from ..exceptions import *
from ..commons import *

class Console:
    def __init__(self, wrapper):
        self.wrapper = wrapper
        self.server = wrapper.server
        self.log = wrapper.log_manager.get_logger("console")
        self.message_queue = Queue()
        self.screen_lock = Lock()
        self.input_buffer = ""
        self.cursor_pos = 0
        atexit.register(self.cleanup)
        
    def cleanup(self):
        """Restore terminal settings on exit"""
        try:
            curses.echo()
            curses.nocbreak()
            curses.endwin()
        except:
            pass

    def run(self):
        try:
            # Initialize curses
            curses_wrapper(self.curses_main)
        except KeyboardInterrupt:
            self.cleanup()
        except:
            self.log.traceback("Console input error")
            self.cleanup()
            raise ConsoleError()

    def handle_output(self, text):
        # Queue output messages to be displayed
        if text and text.strip():  # Only queue non-empty messages
            self.message_queue.put(text)
            if hasattr(self, 'screen'):
                self.refresh_screen()

    def curses_main(self, screen):
        self.screen = screen
        curses.start_color()
        curses.use_default_colors()
        curses.curs_set(1)  # Show cursor
        screen.nodelay(1)   # Non-blocking input
        
        # Setup main window and input window
        height, width = screen.getmaxyx()
        self.main_win = curses.newwin(height-2, width, 0, 0)
        self.input_win = curses.newwin(1, width, height-1, 0)
        
        self.main_win.scrollok(True)
        self.messages = []

        # Redirect stdout/stderr to our custom handler
        sys.stdout.write = self.handle_output
        sys.stderr.write = self.handle_output
        
        while not self.wrapper.abort:
            try:
                self.refresh_screen()
                self.handle_input()
                curses.napms(50)  # Small delay to prevent high CPU usage
            except KeyboardInterrupt:
                break

    def refresh_screen(self):
        with self.screen_lock:
            # Process any queued messages
            while not self.message_queue.empty():
                msg = self.message_queue.get()
                if isinstance(msg, bytes):
                    msg = msg.decode('utf-8', errors='replace')
                # Split multi-line messages
                for line in str(msg).splitlines():
                    if line.strip():
                        self.messages.append(line.rstrip())
                
            # Update main window with messages
            height, width = self.main_win.getmaxyx()
            self.main_win.clear()
            display_messages = self.messages[-(height-1):]  # Leave room for input
            for i, msg in enumerate(display_messages):
                try:
                    self.main_win.addstr(i, 0, msg[:width-1])
                except curses.error:
                    pass
            
            # Update input window
            self.input_win.clear()
            prompt = "> " + self.input_buffer
            try:
                self.input_win.addstr(0, 0, prompt[:width-1])
                self.input_win.move(0, 2 + self.cursor_pos)
            except curses.error:
                pass
            
            # Refresh windows
            self.main_win.refresh()
            self.input_win.refresh()

    def handle_input(self):
        try:
            key = self.screen.getch()
            if key == -1:  # No input
                return
            elif key == ord('\n'):
                # Process command
                if self.input_buffer.strip():
                    self.process_command(self.input_buffer)
                self.input_buffer = ""
                self.cursor_pos = 0
            elif key in (curses.KEY_BACKSPACE, 127, 8):  # Handle different backspace keys
                if self.cursor_pos > 0:
                    self.input_buffer = (self.input_buffer[:self.cursor_pos-1] + 
                                       self.input_buffer[self.cursor_pos:])
                    self.cursor_pos -= 1
            elif key == curses.KEY_LEFT and self.cursor_pos > 0:
                self.cursor_pos -= 1
            elif key == curses.KEY_RIGHT and self.cursor_pos < len(self.input_buffer):
                self.cursor_pos += 1
            elif 32 <= key <= 126:  # Printable characters
                self.input_buffer = (self.input_buffer[:self.cursor_pos] + 
                                   chr(key) + 
                                   self.input_buffer[self.cursor_pos:])
                self.cursor_pos += 1
        except curses.error:
            pass

    def process_command(self, data):
        # Add command to message history
        self.handle_output(f"> {data}\n")

        def args(i):
            try:
                return data.split(" ")[i]
            except:
                return None

        def args_after(i):
            try:
                return " ".join(data.split(" ")[i:])
            except:
                return None

        if len(data) > 0:
            command = args(0)

            # Remove preceeding slash before processing
            if command and command[0] == "/":
                command = command[1:]

            # Commands
            if command == "start":
                self.server.start()
                return

            if command == "restart":
                self.log.info("Restart initiated from console")
                self.server.restart()
                return

            if command == "broadcast":
                message = args_after(1)
                if message:
                    self.server.broadcast(message)
                else:
                    self.log.error("Usage: /broadcast <message>")
                return

            if command == "plugins":
                subcommand = args(1)

                if subcommand == "list":
                    plugins = []
                    for plugin in self.wrapper.plugins.plugins:
                        plugins.append(plugin.name)
                    self.log.info("Plugins: %s" % ", ".join(plugins))
                elif subcommand == "reload":
                    self.log.info("Reloading plugins")
                    self.wrapper.plugins.reload_plugins()
                else:
                    self.log.info("Usage: /plugins <list/reload>")
                return

            if command == "stop":
                self.wrapper.server.stop()
                return

            if command == "wrapper":
                subcommand = args(1)
                if subcommand in ("halt", "stop"):
                    self.log.info("Wrapper.py shutdown initiated from console")
                    self.wrapper.shutdown()
                elif subcommand == "about":
                    self.log.info("Wrapper.py")
                else:
                    self.log.info("Usage: /wrapper <stop/about>")
                return

        # If no built-in command matched, try to send to server
        try:
            self.server.run(data)
        except ServerStopped:
            self.log.error("Failed to run command: server is currently stopped")
