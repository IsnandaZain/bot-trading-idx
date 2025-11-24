import os


def getenv(key, default=None, func=None):
    """Get enviroment variable return None if not exists
    Args:
        key: key os environment
        default: default value if not exists
        func: apply function in env
    """
    val = os.getenv(key, default)
    if func:
        val = func(val)
    return val



# DATABASE
USER_DB = getenv("USER_DB_BOT", "root")
PASSWORD_DB = getenv("PASSWORD_DB_BOT", "")
HOST_DB = getenv("HOST_DB_BOT", "127.0.0.1")
PORT_DB = getenv("PORT_DB_BOT", 3306, int)
NAME_DB = getenv("NAME_DB_BOT", "stockanalyst")