from datetime import datetime,timedelta
from time import localtime,strftime
from django.conf import settings
import pytz



def get_epoch():
    """
    Return number of seconds since 1970-01-01- epoch
    """
    now = datetime.now()
    epoch = datetime(1970,1,1)
    diff = now - epoch
    diff = str(diff.total_seconds())
    diff_seconds = diff.split('.')
    diff_int = diff_seconds[0]
    return diff_int

def get_yesterday():
    now = datetime.now()
    one_day = timedelta(days=1)
    return now-one_day


def get_time_interval_array(interval,interval_type,start,end,tz=None):
    """
    Get an array between the provided time frame
    with slices in the given interval timedelta
    between start and end
    """

    if tz:
        timezone = pytz.timezone(tz)
    else:
        timezone = pytz.timezone(settings.TIME_ZONE)
    # TODO finish timezone implemenation
    result = []
    kwargs = {}
    kwargs[interval_type] = interval
    interval = timedelta(**kwargs)
    while start < end:
        start = start + interval
        result.append(start)

    return result

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

def epoch_to_datetime(seconds_time):
    """
    Translate seconds time to datetime object
    """
    return strftime('%Y-%m-%dT%XZ',localtime(seconds_time))


def get_last_five_days(from_date="now"):
    """
    Get last days returned to you as datetime objects in array
    @params:
        from_date: (date to return consecutive days ongoing from) (optional)
    """
    days = []
    now = datetime.now()
    if not from_date == "now":
        now = from_date

    delta = now - timedelta(5)
    for day in xrange(1,6):
        days.append(delta)
        delta = delta + timedelta(1)
    return days


def get_days_interval_delta(start, end, delta=1):

    """
    return the days inbetween the two sepcified dates
    @params:
    start: when is the interval stardate, datetime object
    end: when should the interval end , datatime object
    delta: increments in which to return dates, integer, default 1 day
    """
    delta =  timedelta(days=delta)
    curr = start
    days  = []
    while curr < end:
        days.append(curr)
        curr += delta
    return days

def get_start_end_date(days_ago, start_day):
    """
    get the delta of days ago from given start date
    """
    delta = start_day - timedelta(days=days_ago)
    return delta

