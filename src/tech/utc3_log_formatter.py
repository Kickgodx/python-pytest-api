from datetime import datetime, timedelta, timezone
import logging

class UTC3Formatter(logging.Formatter):
    UTC_PLUS_3 = timezone(timedelta(hours=3))

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=self.UTC_PLUS_3)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.isoformat()
        return s
