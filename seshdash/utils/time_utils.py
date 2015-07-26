from datetime import datetime,timedelta
from time import localtime,strftime
"""
Return number of seconds since 1970-01-01- epoch
"""
def get_epoch():
    now = datetime.now()
    epoch = datetime(1970,1,1)
    diff = now - epoch

    return diff.total_seconds()

"""
Return number of seconds since 1970-01-01- epoch
from given date
@params: month,day,year,hours,minutes
"""
def get_epoch_from_date(year,month,day,hours,minutes):
    date = datetime(year,month,day,hours,minutes)

    epoch = datetime(1970,1,1)
    diff = date - epoch
    return diff.total_seconds()

"""
Translate seconds time to datetime object
"""
def epoch_to_date(seconds_time):
    return strftime('%Y-%m-%d',localtime(seconds_time))

"""
Get last days returned to you as datetime objects in array
@params:
    from_date: (date to return consecutive days ongoing from) (optional)
"""
def get_last_five_days(from_date="now"):
    days = []
    now = datetime.now()
    if not from_date == "now":
        now = from_date

    delta = now - timedelta(5)
    for day in xrange(1,6):
        days.append(delta)
        delta = delta + timedelta(1)
    return days



