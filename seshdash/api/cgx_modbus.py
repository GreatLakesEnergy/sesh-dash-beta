# bin python
from pymodbus.client.sync import ModbusTcpClient
import csv,logging
from pprint import pprint
class Victron_Modbus():

    CGX_IP = '192.168.0.3'
    #this valuse ie defined in the victron mapping files
    MDODBUS_UNIT = 246
    MAPPING_FILE = ''
    MAPPING_MODBUS_REGISTER_DICT = {}
    IS_ENABLED = False
    _CLIENT  = ''

    def __init__(self,CGX_IP,mapping_file_path="victron_modbus_mapping"):
        self.CGX_IP = CGX_IP
        self.MAPPING_FILE = mapping_file_path

        self._parse_mapping_file(mapping_file_path)
        if len(self.MAPPING_MODBUS_REGISTER_DICT.keys()):
            self.IS_ENABLED = True

        self._CLIENT = ModbusTcpClient(CGX_IP)
        if self._CLIENT.connect() and self.IS_ENABLED:
            self.IS_ENABLED = True
        else:
            self.IS_ENABLED = False

    #get all fields that are availible to query
    def get_availible_modbus_register_names (self):
        if self.IS_ENABLED:
            pprint (self.MAPPING_MODBUS_REGISTER_DICT.keys())
        else:
            pprint("Register mapping was not found or system is not enabled")

    #Wrapper function to get register data
    #will return an array
    def get_register_value_raw(self,register_name):
        return self._make_modbus_request(register_name,parsed=False)


    #Wrapper function to get register data
    #parsed and with units as a string in an array
    def get_register_value_parsed(self,register_name):
        return self._make_modbus_request(register_name)


    #Make the call to CGX
    #returns an array of register values
    def _make_modbus_request(self,register_name,count=1,parsed=True):
        if self.IS_ENABLED:
            if self.MAPPING_MODBUS_REGISTER_DICT.has_key(register_name):
                address = int(self.MAPPING_MODBUS_REGISTER_DICT[register_name]['Address'])
                scale_factor = self.MAPPING_MODBUS_REGISTER_DICT[register_name]['Scalefactor']
                unit = self.MAPPING_MODBUS_REGISTER_DICT[register_name]['dbus-unit']

                result = self._CLIENT.read_holding_registers(address=address,unit=self.MDODBUS_UNIT,count=count)
                results_values = result.registers
                parsed_values = []
                for val in results_values:
                    if parsed:
                        parsed_values.append(self._parse_unit(val,scale_factor,unit))
                    else:
                        parsed_values.append(val)
                return parsed_values
            print "key not found "



    #make the returned values nice and readable
    def _parse_unit(self,value,scale_factor,unit):
            value = int(value)/int(scale_factor)

            value_str = "%s %s"%(value,unit)

            return value_str


    #we need this file to know which registers contain which type of data
    def _parse_mapping_file(self,mapping_file_path):
        with open(mapping_file_path,'rb') as csv_mapping:
            mapping_reader = csv.reader(csv_mapping)
            for row in mapping_reader:
                #Assume that first column of each row is the dbu name which should contain somethin like com.victronenergy.vebus
                #['dbus-service-name', 'description', 'Address', 'Type', 'Scalefactor', 'Range', 'dbus-obj-path', 'dbus-unit']
                #  this mmapping file is availible from victron email mvader@victronenergy.com for support
                if  len(row)  and row[0].__contains__("victronenergy"):
                    self.MAPPING_MODBUS_REGISTER_DICT[row[1]] = {
                                                            'dbus-service-name' : row[0],
                                                            'description' : row[1],
                                                            'Address': row[2],
                                                            'Type' :row[3],
                                                            'Scalefactor' :row[4],
                                                            'Range': row[5],
                                                            'dbus-obj-path': row[6],
                                                            'dbus-unit': row[7]
                                                            }






