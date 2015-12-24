from __future__ import absolute_import

from django.conf import settings
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError,InfluxDBServerError
from datetime import datetime

import logging

class Influx:

    def __init__(self):
        self._influx_client = InfluxDBClient (settings.INFLUX_HOST,
                                              settings.INFLUX_PORT,
                                              settings.INFLUX_USERNAME,
                                              settings.INFLUX_PASSWORD,
                                              settings.INFLUX_DB
                                                )
        self.db = settings.INFLUX_DB


    def get_measurement_bucket(self,measurement,bucket_size,clause,clause_val,time_delta,start="now",operator="mean") :
        """
        return the requsted measurement values in given bucket size
        """
        start_time = "now()"
        query_string = "SELECT {operator}(\"value\") FROM \"{measurement}\" WHERE \"{clause}\" = '{clause_value}' AND  time  >  now() - {time_delta} GROUP BY time({bucket_size})"


        if not start == "now":
            start_time = start

        query_string_formatted = query_string.format(
                                                    measurement = measurement,
                                                    bucket_size = bucket_size,
                                                    clause = clause,
                                                    clause_value = clause_val,
                                                    time_delta = time_delta
                                                    )


        try:
            result_set = self._influx_client.query(query_string_formatted,database = self.db)

            return result_set
        except InfluxDBServerError,e:
            logging.error("Error running query on server %s"%e)
        except InfluxDBClientError,e:
            logging.error("Error running  query"%e)
        except Exception,e:
            logging.error("influxdb unkown error %s"%e)


