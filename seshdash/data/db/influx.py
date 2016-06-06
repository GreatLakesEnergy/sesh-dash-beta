from __future__ import absolute_import
import logging
from django.utils import timezone
from datetime import datetime, timedelta,date

from django.conf import settings
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError,InfluxDBServerError

# Instantiating the logger
logger = logging.getLogger(__name__)

class Influx:

    def __init__(self,database=None):

        self.db = settings.INFLUX_DB
        if database:
           self.db = database

        self._influx_client = InfluxDBClient (settings.INFLUX_HOST,
                                              settings.INFLUX_PORT,
                                              settings.INFLUX_USERNAME,
                                              settings.INFLUX_PASSWORD,
                                              self.db
                                              )
  #TODO draw this from settings
#	try:
#		self.dbs = self._influx_client.get_list_database()
#	except:
#		self.dbs = []
#		pass

        self._influx_tag = 'sesh_dash'

    def _generate_date_clause(self,start,end=None):
        """
        Helper function to generate time constraint on influx query
        to handle if using epoch time or datetime
        """
        query_str =  "time  >=  {start}s"
        if end:
            query_str = query_str + " AND time <= {end}s"

        try:
            start = int(start)
        except:
            start = start
            pass
        if isinstance(start,datetime):
            start = timezone.make_naive(start)
            if end:
                end = timezone.make_naive(end)

        if isinstance(start,date) or isinstance(start,datetime):
            query_str =  query_str.replace("{start}s","\'{start}\'")
            if end:
                query_str = query_str.replace("{end}s","\'{end}\'")



        query_str_formatted =  query_str.format(start=start, end=end)
        return query_str_formatted

    def get_measurement_bucket(self,
                                measurement,
                                bucket_size,
                                clause,
                                clause_val,
                                time_delta={'hours':24},
                                start="now",
                                operator="mean",
                                database=None):
        """
        return the requsted measurement values in given bucket size
        """
        db =  self.db
        if database:
           db = database

        start_time = timezone.now() - timedelta(**time_delta)

        end_time = start_time + timedelta(**time_delta)

       #print "start is %s end is %s" % (start_time, end_time)
        query_string = "SELECT {operator}(\"value\") FROM \"{measurement}\" WHERE \"{clause}\" = '{clause_value}' AND  {time_constraint}  GROUP BY time({bucket_size}) fill(0)"
        result_set_gen = []
        if not start == "now":
            start_time = start
            end_time = start_time + timedelta(**time_delta)

        time_constraint = self._generate_date_clause(start_time, end=end_time)
        query_string_formatted = query_string.format(
                                                    measurement = measurement,
                                                    bucket_size = bucket_size,
                                                    clause = clause,
                                                    clause_value = clause_val,
                                                    operator = operator,
                                                    time_constraint = time_constraint,
                                                    )
       # print query_string_formatted
        try:
            result_set = self._influx_client.query(query_string_formatted,database = db)
            logger.debug("Influx query %s"% query_string_formatted)
            #get values
            result_set_gen = result_set.get_points(measurement=measurement)
            return list(result_set_gen)
        except InfluxDBServerError,e:
            logger.error("Error running query on server %s"% str(e))
            logger.debug("error on server %s" % str(e))
            raise Exception
        except InfluxDBClientError,e:
            logger.error("Error running  query %s"%str(e))
            logger.debug("error %s"% str(e))
            raise Exception
        except Exception,e:
            logger.error("influxdb unkown error %s" %str(e))
            logger.debug("unkown error %s"% str(e))
            raise Exception
        return result_set_gen

    def send_object_measurements(self,measurement_dict, timestamp=None, tags={}, database=None):
        """
        returns True if objects are submitted False otherwise
        send Django object as seperate measurements to influx
        @param Timestamps is assumed now if not provided
        @param Tags will be applied to all measurments
        """
        tags['source'] = self._influx_tag
        data_point_list = []

        #Use Defaul database if None
        db =  self.db
        if database:
           db = database

        logger.debug("recieved data point %s"%measurement_dict)
        # Create our timestamp if one was not provided.
        if not timestamp:
            timestamp = datetime.now()
        if not isinstance(timestamp,str):
            timestamp = timestamp.isoformat()
        #print "sending data to influx %s"%measurement_dict
        for key in measurement_dict.keys():
               # Incoming data is likely to have datetime object. We need to ignore this
               data_point = {}

               try:
                    data_point["measurement"] = key
                    data_point["tags"] = tags
                    # Datetime needs to be converted to epoch
                    data_point["time"] = timestamp
                    # Cast everything not string to Float
                    data_point["fields"] = {"value" : float(measurement_dict[key])}
                    logger.debug("INFLUX prepping data point %s"%(data_point))
                    # Get the data point array ready.
                    data_point_list.append(data_point)
               except Exception,e:
                    logger.debug("INFLUX: unable to cast to float skipping: %s key: %s"%(e,key))

        try:
                # Send the data list
                logger.debug("INFLUX sending %s"%data_point_list)
                result = self._influx_client.write_points(data_point_list)
                logger.debug("Result %s"%result)
        except InfluxDBServerError,e:
            logger.warning("INFLUX Error running query on server %s %s"%(e,data_point_list))
            logger.debug(e)
        except InfluxDBClientError,e:
            logger.warning("INFLUX Error running  query %s %s"%(e,data_point_list))
            logger.debug(e)
        except Exception,e:
            logger.warning("INFLUX unkown error %s %s"%(e,data_point))
            logger.debug(e)

        return True

    def query(self,measurement_name,database=None):
        db =  self.db
        if database:
           db = database
        query = "SELECT value FROM %s"%measurement_name
        return list(self._influx_client.query(query,database=db).get_points())


    def create_database(self,name):
        self._influx_client.create_database(name)

    def delete_database(self,name):
        self._influx_client.drop_database(name)


    def insert_point(self, site, measurement_name, value, time=None, tags=None):
        """ Write points to the database """


        json_body = [
                    {
                    "measurement": measurement_name,
                    "tags": {
                        "site_name": site.site_name,
                        "site_id": site.id,
                        "source": 'sesh_dash'
                    },
                    "fields":{
                        "value": value
                    }
                }
            ]
        # override default tags
        if tags:
            json_body[0]['tags'] = tags

        if time:
            json_body[0]['time'] = time.isoformat()

        value_returned = self._influx_client.write_points(json_body)
        logger.debug("inserting point into DB %s %s %s"%(self.db,json_body, value_returned))

        return value_returned

    def get_point(self, measurement_name, point_id, database=None):
        db = self.db
        if database:
            db = database

        query = "SELECT * FROM %s WHERE time='%s'" %(measurement_name, point_id)
        return list(self._influx_client.query(query, database=db).get_points())


    def get_measurements(self,database=None):
        db = self.db
        if database:
           db = database
        query = "SHOW measurements"
        try:
            return list(self._influx_client.query(query,database=db).get_points())
        except Exception, e:
            logger.debug("INFLUX error %s" %e)
       

    def get_latest_measurement_point_site(self, site, measurement_name, site_id=None, database=None):
         """ Returns the latest point of a site for a measurement """
         db = self.db
         if database:
             db = database
         # TODO make this work with Site_id for API
         query = "SELECT * FROM %s WHERE site_name='%s' ORDER BY time DESC LIMIT 1" % (measurement_name, site.site_name)
         logger.debug("Querying DB %s"%db)
         logger.debug(query)
         result = list(self._influx_client.query(query,database=db).get_points())
         logger.debug("got result %s"%result)
         return result

    # Helper classes to the interface
    def get_measurements_latest_point(self, site, measurement_list, database=None):
        """
        Returns a list of elements containing the latest points of provided measurements
        """

        # Handling the db to be used
        db = self.db
        if database:
           db = database
    

        measurement_dict = {}
        for measurement in measurement_list:
            try:
                measurement_dict[measurement] = self.get_latest_measurement_point_site(site, measurement)[0]
            except IndexError, e:
                logger.debug('No points for %s ' % measurement)
                pass

        return measurement_dict


# Helper classes to the interface
def get_latest_point_site(site, measurement_name, db=None):
    """ Static method for that returns  latest point for a measurement for a specific siite """
    i = Influx()
    if db is not None:
        i = Influx(database=db)

    point = i.get_latest_measurement_point_site(site, measurement_name, db)

    if len(point) > 0:
        point = point[0]
    else:
        logger.error('No influx data points for the site')
        return None

    return point


def get_point(measurement_name, point_id, db=None):
    """ Queryies for a specific point and returns it """
    i = Influx()
    if db is not None:
        i = Influx(database=db)

    point = i.get_point(measurement_name, point_id, db)

    if point:
        return point[0]

    return point


def insert_point(site, measurement_name, value, db=None, time=None, tags=None):
    """ Inserts a point into the db provided the name and the site """
    i = Influx()
    if db is not None:
        i = Influx(database=db)

    value = i.insert_point(site, measurement_name, float(value), time=time, tags=tags)



def get_measurements_latest_point(site, measurements_list, db=None):
    """ Returns a list of latest measurement points for a given site """
    i = Influx()
    if db is not None:
        i = Influx(database=db)


    return i.get_measurements_latest_point(site, measurements_list)
