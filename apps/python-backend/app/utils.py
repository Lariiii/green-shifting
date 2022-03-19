from datetime import datetime


def unix_timestamp_to_datetime_str(unix_timestamp: int) -> str:
    return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')
