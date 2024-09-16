from datetime import datetime


def format_datetime(time: datetime) -> str:
    return time.replace(microsecond=0).isoformat() + "Z00:00"
