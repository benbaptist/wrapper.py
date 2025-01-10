from curses import wrapper as curses_wrapper
import curses
import sys
import atexit
from queue import Queue
from threading import Lock

from ..exceptions import ConsoleError
from .command_handler import CommandHandler

class ConsoleUI:
    def __init__(self, wrapper):
        self.wrapper = wrapper
        self.log = wrapper.log_manager.get_logger("console")
        self.message_queue = Queue()
        self.screen_lock = Lock()
        self.input_buffer = ""
        self.cursor_pos = 0
        self.command_handler = CommandHandler(wrapper)
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
                    self.handle_output(f"> {self.input_buffer}\n")
                    self.command_handler.handle_command(self.input_buffer)
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