from datetime import datetime


def get_current_time_in_str():
    """
    This should be the standard way the Linea captures time in its tables
    """
    return str(datetime.now().timestamp())
