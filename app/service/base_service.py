import pytz
from datetime import datetime

def get_moscow_time():
    moscow_tz = pytz.timezone('Europe/Moscow')
    moscow_time = datetime.now(moscow_tz).replace(tzinfo=None)
    return moscow_time