import logging
from datetime import datetime, timedelta, timezone


class UtcFormatter(logging.Formatter):

    def __init__(self, fmt=None, datefmt=None, style='%', validate=True, tz_hours_gap: int = 3):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style, validate=validate)
        self.tz = timezone(timedelta(hours=tz_hours_gap))

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=self.tz)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.isoformat()
        return s
