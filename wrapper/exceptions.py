class ServerError(Exception): pass
class ServerStarting(ServerError): pass
class ServerStopping(ServerError): pass
class ServerStopped(ServerError): pass

class AuthError(Exception): pass
class PlayerNotFound(Exception): pass

class CommandError(Exception): pass
class CommandNotFound(CommandError): pass
class CommandSyntaxError(CommandError): pass
class CommandExecutionError(CommandError): pass
class CommandPermissionError(CommandError): pass
class CommandUsageError(CommandError): pass

class ConsoleError(Exception): pass
class UnsupportedFormat(Exception): pass