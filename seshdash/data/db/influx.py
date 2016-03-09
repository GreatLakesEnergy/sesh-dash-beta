from __future__ import absolute_import
import logging
from datetime import datetime

from django.conf import settings
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError,InfluxDBServerError


class Influx:

    def __init__(self):
        self._influx_client = InfluxDBClient (settings.INFLUX_HOST,
                                              settings.INFLUX_PORT,
                                              settings.INFLUX_USERNAME,
                                              settings.INFLUX_PASSWORD,
                                              settings.INFLUX_DB
                                              )
        self.db = settings.INFLUX_DB
        #TODO draw this from settings
        self._influx_tag = 'sesh_dash'


    def get_measurement_bucket(self,measurement,bucket_size,clause,clause_val,time_delta,start="now",operator="mean") :
        """
        return the requsted measurement values in given bucket size
        """
        start_time = "now()"
        query_string = "SELECT {operator}(\"value\") FROM \"{measurement}\" WHERE \"{clause}\" = '{clause_value}' AND  time  >  now() - {time_delta} GROUP BY time({bucket_size}) fill(0)"


        if not start == "now":
            start_time = start

        query_string_formatted = query_string.format(
                                                    measurement = measurement,
                                                    bucket_size = bucket_size,
                                                    clause = clause,
                                                    clause_value = clause_val,
                                                    time_delta = time_delta,
                                                    operator = operator
                                                    )


        try:
            result_set = self._influx_client.query(query_string_formatted,database = self.db)
            #get values
            result_set_gen = result_set.get_points(measurement=measurement)
            return list(result_set_gen)
        except InfluxDBServerError,e:
            logging.error("Error running query on server %s"% str(e))
        except InfluxDBClientError,e:
            logging.error("Error running  query"%str(e))
        except Exception,e:
            logging.error("influxdb unkown error %s" %str(e))
        return []

    def send_object_measurements(self,measurement_dict, timestamp=None, tags={}):
        """
        returns True if objects are submitted False otherwise
        send Django object as seperate measurements to influx
        @param Timestamps is assumed now if not provided
        @param Tags will be applied to all measurments
        """
        tags['source'] = self._influx_tag
        data_point_list = []
        logging.debug("recieved data point %s"%measurement_dict)
        # Create our timestamp if one was not provided.
        if not timestamp:
            timestamp = datetime.now()
        if not isinstance(timestamp,str):
            timestamp = timestamp.isoformat()

        for key in measurement_dict.keys():
                # Incoming data is likely to have datetime object. We need to ignore this
                data_point = {}
                data_point["measurement"] = key
                data_point["tags"] = tags
                # Datetime needs to be converted to epoch
                data_point["time"] = timestamp
                #Cast everything not string to Float
                if isinstance(measurement_dict[key], str) or isinstance(measurement_dict[key],unicode):
                    data_point["fields"] = {"value" : measurement_dict[key]}
                else:
                    data_point["fields"] = {"value" : float(measurement_dict[key])}

                logging.debug("prepping data point %s"%(data_point))
                # Get the data point array ready.
                data_point_list.append(data_point)
        try:
            #Send the data blob to influx
            logging.debug("sending %s"%data_point_list)
            self._influx_client.write_points(data_point_list)
        except InfluxDBServerError,e:
            logging.error("Error running query on server %s"%e)
        except InfluxDBClientError,e:
            logging.error("Error running  query %s "%e)
        except Exception,e:
            logging.error("influxdb unkown error %s"%e)
        else:
            return False

        return True




