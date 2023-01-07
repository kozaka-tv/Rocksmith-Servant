from datetime import datetime

DATE_TIME = "%Y-%m-%d %H:%M:%S"


def now():
    return datetime.now().strftime(DATE_TIME)
