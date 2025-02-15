from typing import List, Tuple

from ..exceptions import ServerStopped

from wrapper import __version__

from wrapper.dashboard.auth import reset_password

class CommandHandler:
    def __init__(self, wrapper):
        self.wrapper = wrapper
        self.server = wrapper.server
        self.log = wrapper.log_manager.get_logger("console")

    def parse_args(self, command: str) -> Tuple[str, List[str]]:
        """Parse a command string into command name and arguments."""
        parts = command.strip().split()
        if not parts:
            return "", []
        
        cmd = parts[0]
        # Remove leading slash if present
        if cmd.startswith('/'):
            cmd = cmd[1:]
        return cmd, parts[1:]

    def handle_command(self, command: str) -> None:
        """Process a command and execute the appropriate action."""
        if not command.strip():
            return

        cmd, args = self.parse_args(command)
        
        # Command handlers
        handlers = {
            'start': self._handle_start,
            'restart': self._handle_restart,
            'broadcast': self._handle_broadcast,
            'plugins': self._handle_plugins,
            'stop': self._handle_stop,
            'wrapper': self._handle_wrapper
        }

        handler = handlers.get(cmd)
        if handler:
            handler(args)
        else:
            # If no built-in command matched, try to send to server
            try:
                self.server.instance.run(command)
            except ServerStopped:
                self.log.error("Failed to run command: server is currently stopped")

    def _handle_start(self, args: List[str]) -> None:
        self.server.start()

    def _handle_restart(self, args: List[str]) -> None:
        self.log.info("Restart initiated from console")
        self.server.restart()

    def _handle_broadcast(self, args: List[str]) -> None:
        if args:
            message = ' '.join(args)
            self.server.broadcast(message)
        else:
            self.log.error("Usage: /broadcast <message>")

    def _handle_plugins(self, args: List[str]) -> None:
        if not args:
            self.log.info("Usage: /plugins <list/reload>")
            return

        subcommand = args[0]
        if subcommand == "list":
            plugins = [plugin.name for plugin in self.wrapper.plugins.plugins]
            self.log.info("Plugins: %s" % ", ".join(plugins))
        elif subcommand == "reload":
            self.log.info("Reloading plugins")
            self.wrapper.plugins.reload_plugins()
        else:
            self.log.info("Usage: /plugins <list/reload>")

    def _handle_stop(self, args: List[str]) -> None:
        self.wrapper.server.stop()

    def _handle_wrapper(self, args: List[str]) -> None:
        if not args:
            self.log.info("Usage: /wrapper <stop/about>")
            return

        subcommand = args[0]
        if subcommand in ("halt", "stop"):
            self.log.info("Wrapper.py shutdown initiated from console")
            self.wrapper.shutdown()
        elif subcommand == "reset":
            if len(args) < 2:
                self.log.error("Usage: /wrapper reset <password>")
                return

            password = args[1]
            
            try:
                reset_password(password)
                self.log.info("Dashboard password has been reset.")
            except AttributeError:
                self.log.error("Dashboard is not enabled or initialized")
        elif subcommand == "about":
            self.log.info(f"Wrapper.py {__version__}")
        else:
            self.log.info("Usage: /wrapper <stop/about>") 