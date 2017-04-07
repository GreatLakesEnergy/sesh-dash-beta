"""
The module contains functions related to data aggretion
"""

# Python libs
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Django libs
from django.db.models import Avg

# Seshdash
from seshdash.models import Daily_Data_Point, Sesh_Site, Sesh_Alert
from seshdash.utils.time_utils import get_date_dashed
from seshdash.utils.reporting import get_measurement_unit

def get_avg_field_year(site, field):
    """ Returns the average of a field for a year range in Daily Data Point"""
    now = datetime.now()
    year_before = now - relativedelta(years=1)
    avg_field_yield = Daily_Data_Point.objects.filter(date__range=[
                                                                  get_date_dashed(year_before),
                                                                  get_date_dashed(now)],site=site)\
                                                                  .aggregate(Avg(field)).values()[0]
    return avg_field_yield


def get_alerts_for_year(site):
    """ Returns the alerts for a site in a year range """

    # NOTE: When using datetime object date_range does not include the last date
    now = datetime.now()
    year_before = now - relativedelta(years=1)

    return get_alerts_for_range(site, year_before, now)


def get_alerts_for_range(site, start_date=None, end_date=None):
    """ Returns the number of alerts for a given date range default day """
    if start_date is None and end_date is None:
        start_date = datetime.now()
        end_date = start_date - relativedelta(days=1)

    alerts_for_year = Sesh_Alert.objects.filter(date__range=[
                                                             get_date_dashed(start_date),
                                                             get_date_dashed(end_date)], site=site)
    return alerts_for_year


def get_historical_dict(column='daily_pv_yield'):
    """ Packages a ditionary containing data information of a column in Daily_Data_Point for the whole year """
    unit = get_measurement_unit(column)
    sites = Sesh_Site.objects.all();
    historical_points = Daily_Data_Point.objects.all()

    historical_data = [];


    # For each site get Points
    for site in sites:
       historical_points = Daily_Data_Point.objects.filter(site=site.id)
       site_historical_data = []

        # For point get neccessary Data
       for point in historical_points:
           site_historical_data.append({
               "date": get_date_dashed(point.date),
               "count": getattr(point, column),
               "point_id":point.id,
           })

       historical_data.append({
                               "site_id":site.id,
                               "site_name":site.site_name,
                               "site_historical_data": site_historical_data,
                               "data_unit": unit,
                               "number_of_alerts": get_alerts_for_year(site).count(),
                               "average_pv_yield": get_avg_field_year(site, 'daily_pv_yield'),
                               "average_power_consumption_total": get_avg_field_year(site, 'daily_power_consumption_total')
                    })
    return historical_data

