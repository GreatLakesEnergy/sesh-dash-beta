import datetime
import hashlib
import random


def generate_rmc_api_key(seed=''):
    """
    simple function to unique api key
    """
    if not seed:
        seed = random.random()
    now = datetime.datetime.now()
    m = hashlib.md5()
    # Create seed +  datatimenow digest
    key = str(seed) + str(now)
    m.update(key)
    return m.hexdigest()


