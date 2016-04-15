from random import random
from random import uniform
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from seshdash.utils.time_utils import get_time_interval_array

def get_random_int():
    val =  random() * 100
    return val

def get_random_binary():
    val = get_random_int()
    if val > 50:
        return 1
    return 0

def get_random_interval(cieling,floor):
    return uniform(cieling,floor)

def generate_date_array(start=None,naive=False):
    now = timezone.now()
    if naive:
        now = datetime.now()
    
    if not start:
        start = now - timedelta(hours=24)

    time_arr = get_time_interval_array(5,"minutes",start,now)
    return time_arr


