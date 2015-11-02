from datetime import datetime,timedelta
from time import localtime,strftime
"""
Return number of seconds since 1970-01-01- epoch
"""
def get_epoch():
    now = datetime.now()
    epoch = datetime(1970,1,1)
    diff = now - epoch
    diff = str(diff.total_seconds())
    diff_seconds = diff.split('.')
    diff_int = diff_seconds[0]
    return diff_int

def get_epoch_from_datetime(date):
    """
    Return number of seconds since 1970-01-01- epoch
    from given date
    @params: dateobject
    """
    epoch =  datetime(1970,1,1)
    if date.tzinfo:
        epoch = datetime(1970,1,1,tzinfo=date.tzinfo)
    diff = date - epoch
    seconds_only = str(diff.total_seconds())
    seconds_only_str = seconds_only.split('.')
    seconds_only = seconds_only_str[0]
    return seconds_only

def get_epoch_from_date(year,month,day,hours,minutes):
    """
    Return number of seconds since 1970-01-01- epoch
    from given date
    @params: month,day,year,hours,minutes
    """
    date = datetime(year,month,day,hours,minutes)

    epoch = datetime(1970,1,1)
    diff = date - epoch
    return diff.total_seconds()

def epoch_to_date(seconds_time):
    """
    Translate seconds time to date
    """
    return strftime('%Y-%m-%d',localtime(seconds_time))

"""
Translate seconds time to datetime object
"""
def epoch_to_datetime(seconds_time):
    return strftime('%Y-%m-%dT%XZ',localtime(seconds_time))


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



"""
return the days inbetween the two sepcified dates
@params:
start: when is the interval stardate, datetime object
end: when should the interval end , datatime object
delta: increments in which to return dates, integer, default 1 day
"""
def get_days_interval_delta(start, end, delta=1):
    delta =  timedelta(days=delta)
    curr = start
    days  = []
    while curr < end:
        days.append(curr)
        curr += delta
    return days

"""
get the delta of days ago from given start date
"""
def get_start_end_date(days_ago, start_day):
    delta = start_day - timedelta(days=days_ago)
    return delta

