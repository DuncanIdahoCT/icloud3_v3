

from ..global_variables import GlobalVariables as Gb
from ..const            import (
                                EVLOG_CARD_WWW_DIRECTORY, EVLOG_CARD_WWW_JS_PROG,
                                IPHONE, IPAD,
                                WATCH,  AIRPODS,
                                DEVICE_TYPES,
                                NO_IOSAPP,
                                NAME,
                                NAME, BADGE,
                                TRIGGER, INACTIVE_DEVICE,
                                ZONE, ZONE_DATETIME, LAST_ZONE,
                                INTERVAL,
                                BATTERY, BATTERY_STATUS,
                                ZONE_DISTANCE, CALC_DISTANCE, WAZE_DISTANCE,
                                TRAVEL_TIME, TRAVEL_TIME_MIN, DIR_OF_TRAVEL, MOVED_DISTANCE,
                                LAST_UPDATE,
                                NEXT_UPDATE,
                                LAST_LOCATED,
                                INFO, GPS_ACCURACY, POLL_COUNT, VERTICAL_ACCURACY, ALTITUDE,
                                ZONE_NAME, ZONE_FNAME, LAST_ZONE_NAME, LAST_ZONE_FNAME,
                                CONFIG_IC3,
                                CONF_CONFIG_IC3_FILE_NAME,
                                CONF_VERSION, CONF_EVLOG_CARD_DIRECTORY, CONF_EVLOG_CARD_PROGRAM,
                                CONF_USERNAME, CONF_PASSWORD, CONF_DEVICES, CONF_TRACKING_METHOD,
                                CONF_DEVICENAME, CONF_TRACK_FROM_ZONES, CONF_TRACKING_MODE,
                                CONF_IOSAPP_SUFFIX, CONF_IOSAPP_ENTITY, CONF_NO_IOSAPP, CONF_IOSAPP_INSTALLED,
                                CONF_PICTURE, CONF_EMAIL, CONF_DEVICE_TYPE, CONF_INZONE_INTERVALS,
                                CONF_UNIT_OF_MEASUREMENT, CONF_TIME_FORMAT, CONF_MAX_INTERVAL, CONF_OFFLINE_INTERVAL,
                                CONF_GPS_ACCURACY_THRESHOLD, CONF_OLD_LOCATION_THRESHOLD,
                                CONF_TRAVEL_TIME_FACTOR,
                                CONF_LOG_LEVEL,
                                CONF_DISPLAY_ZONE_FORMAT, CONF_CENTER_IN_ZONE, CONF_DISCARD_POOR_GPS_INZONE,
                                CONF_WAZE_USED, CONF_WAZE_REGION, CONF_WAZE_MAX_DISTANCE, CONF_WAZE_MIN_DISTANCE,
                                CONF_WAZE_REALTIME,
                                CONF_STAT_ZONE_STILL_TIME, CONF_STAT_ZONE_INZONE_INTERVAL,
                                CONF_STAT_ZONE_BASE_LATITUDE,
                                CONF_STAT_ZONE_BASE_LONGITUDE, CONF_DISPLAY_TEXT_AS,
                                CONF_IC3_DEVICENAME, CONF_FNAME, CONF_FAMSHR_DEVICENAME,
                                CONF_IOSAPP_DEVICE, CONF_PICTURE, CONF_FMF_EMAIL,
                                CONF_TRACK_FROM_ZONES, CONF_DEVICE_TYPE, CONF_INZONE_INTERVAL,
                                CONF_NAME,
                                NAME, BADGE, BATTERY, BATTERY_STATUS, INFO,
                                CF_DEFAULT_IC3_CONF_FILE,
                                DEFAULT_PROFILE_CONF, DEFAULT_TRACKING_CONF, DEFAULT_DEVICE_CONF, DEFAULT_GENERAL_CONF,
                                DEFAULT_SENSORS_CONF,
                                WAZE_SERVERS_BY_COUNTRY_CODE,
                                )

CONF_DEVICENAME       = 'device_name'
CONF_NO_IOSAPP        = 'no_iosapp'
CONF_IOSAPP_INSTALLED = 'iosapp_installed'
CONF_IOSAPP_SUFFIX    = 'iosapp_suffix'
CONF_IOSAPP_ENTITY    = 'iosapp_entity'
CONF_EMAIL            = 'email'
CONF_CONFIG           = 'config'
CONF_SOURCE           = 'source'

VALID_CONF_DEVICES_ITEMS = [CONF_DEVICENAME, CONF_EMAIL, CONF_PICTURE, CONF_NAME,
                            CONF_INZONE_INTERVAL, 'track_from_zone', CONF_IOSAPP_SUFFIX,
                            CONF_IOSAPP_ENTITY, CONF_IOSAPP_INSTALLED,
                            CONF_NO_IOSAPP, CONF_TRACKING_METHOD, ]

TIME_PARAMETER_ITEMS = [    CONF_MAX_INTERVAL, CONF_OLD_LOCATION_THRESHOLD,
                            CONF_STAT_ZONE_STILL_TIME, CONF_STAT_ZONE_INZONE_INTERVAL,
                            CONF_INZONE_INTERVAL, ]

V2_EVLOG_CARD_WWW_DIRECTORY = 'www/custom_cards'
SENSOR_ID_NAME_LIST = {
        'zon': ZONE,
        'lzon': LAST_ZONE,
        'zonn': ZONE_NAME,
        'zont': ZONE_NAME,
        'zonfn': ZONE_FNAME,
        'lzonn': LAST_ZONE_NAME,
        'lzont': LAST_ZONE_NAME,
        'lzonfn': LAST_ZONE_FNAME,
        'zonts': ZONE_DATETIME,
        'zdis': ZONE_DISTANCE,
        'cdis': CALC_DISTANCE,
        'wdis': WAZE_DISTANCE,
        'tdis': MOVED_DISTANCE,
        'ttim': TRAVEL_TIME,
        'mtim': TRAVEL_TIME_MIN,
        'dir': DIR_OF_TRAVEL,
        'intvl':  INTERVAL,
        'lloc': LAST_LOCATED,
        'lupdt': LAST_UPDATE,
        'nupdt': NEXT_UPDATE,
        'cnt': POLL_COUNT,
        'info': INFO,
        'trig': TRIGGER,
        'bat': BATTERY,
        'batstat': BATTERY_STATUS,
        'alt': ALTITUDE,
        'gpsacc': GPS_ACCURACY,
        'vacc': VERTICAL_ACCURACY,
        'badge': BADGE,
        'name': NAME,
        }

CONF_SENSORS_DEVICE_LIST            = ['name', 'badge', 'battery', 'battery_status', 'info',]
CONF_SENSORS_TRACKING_UPDATE_LIST   = ['interval', 'last_update', 'next_update', 'last_located']
CONF_SENSORS_TRACKING_TIME_LIST     = ['travel_time', 'travel_time_min']
CONF_SENSORS_TRACKING_DISTANCE_LIST = ['zone_distance', 'home_distance', 'dir_of_travel', 'moved_distance']
CONF_SENSORS_TRACKING_BY_ZONES_LIST = []
CONF_SENSORS_TRACKING_OTHER_LIST    = ['trigger', 'waze_distance', 'calc_distance', 'pll_count']
CONF_SENSORS_ZONE_LIST              = ['zone', 'zone_fname', 'zone_name', 'zone_timestamp', 'last_zone']
CONF_SENSORS_OTHER_LIST             = ['gps_accuracy', 'vertical_accuracy', 'altitude']

from ..helpers.common       import (instr, )
from ..helpers.messaging    import (_traceha, log_info_msg, log_warning_msg, log_exception, )
from ..helpers.time_util    import (time_str_to_secs, secs_to_hhmmss, datetime_now, )
from ..support              import waze
from .                      import config_file

import os
import json
from   homeassistant.util    import slugify
import homeassistant.util.yaml.loader as yaml_loader
import logging
_LOGGER = logging.getLogger(__name__)

#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
class iCloud3_v2v3ConfigMigration(object):

    def __init__(self):
        self.config_track_devices_fields = []
        self.config_ic3_track_devices_fields = []
        self.devicename_list = []

        # self.config_parm          = DEFAULT_CONFIG_VALUES.copy()
        self.config_parm_general  = DEFAULT_GENERAL_CONF.copy()
        self.config_parm_tracking = DEFAULT_TRACKING_CONF.copy()
        self.config_parm_sensors  = {}

        Gb.conf_profile   = DEFAULT_PROFILE_CONF.copy()
        Gb.conf_tracking  = DEFAULT_TRACKING_CONF.copy()
        Gb.conf_devices   = []
        Gb.conf_general   = DEFAULT_GENERAL_CONF.copy()
        Gb.conf_sensors   = DEFAULT_SENSORS_CONF.copy()
        Gb.conf_file_data = CF_DEFAULT_IC3_CONF_FILE.copy()

        try:
            self.log_filename_name  = Gb.hass.config.path("icloud3-migration.log")
            self.migration_log_file = open(self.log_filename_name, 'w', encoding='utf8')
        except Exception as err:
            log_exception(err)

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #
    #   EXTRACT ICLOUD3 PARAMETERS FROM THE CONFIG_IC3.YAML PARAMETER FILE.
    #
    #   The ic3 parameters are specified in the HA configuration.yaml file and
    #   processed when HA starts. The 'config_ic3.yaml' file lets you specify
    #   parameters at HA startup time or when iCloud3 is restarted using the
    #   Restart-iC3 command on the Event Log screen. When iC3 is restarted,
    #   the parameters will override those specified at HA startup time.
    #
    #   1. You can, for example, add new tracked devices without restarting HA.
    #   2. You can specify the username, password and tracking method in this
    #      file but these items are onlyu processed when iC3 initially loads.
    #      A restart will discard these items
    #
    #   Default file is config/custom_components/icloud3/config-ic3.yaml
    #   if no '/' on the config_ic3_filename parameter:
    #       check the default directory
    #       if not found, check the /config directory
    #
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def convert_v2_config_files_to_v3(self):
        self.write_migration_log_msg(f"\nMigration Started, {datetime_now()}\n")
        log_warning_msg('iCloud3 - Migrating Configuration Parameters')
        self._extract_config_parameters(Gb.ha_config_yaml_icloud3_platform)

        config_ic3_records = self._get_config_ic3_records()
        self._extract_config_parameters(config_ic3_records)
        self._set_data_fields_from_config_parameter_dictionary()

        try:
            self.write_migration_log_msg("\nMigration Complete, Writing Configuration File")
            self.write_migration_config_items('Profile', Gb.conf_profile)
            self.write_migration_config_items('Tracking', Gb.conf_tracking)
            self.write_migration_config_items('General', Gb.conf_general)
            self.write_migration_config_items('Sensors', Gb.conf_sensors)


            # self.write_migration_log_msg("\nMigration Complete, Writing Configuration File")
            # self.write_migration_log_msg(f"  -- Profile: {Gb.conf_profile}")
            # temp_tracking_recds = Gb.conf_tracking.copy()
            # temp_tracking_recds[CONF_PASSWORD] = '********'
            # self.write_migration_log_msg(f"  -- Tracking: {temp_tracking_recds}")
            # self.write_migration_log_msg(f"  -- General: {Gb.conf_general}")
            # self.write_migration_log_msg(f"  -- Sensors: {Gb.conf_sensors}")

        except Exception as err:
            self.log_exception(err)

        log_warning_msg('iCloud3 - Migration Complete')

        # event_msg = (   f"iCloud3 parameters were converted from v2 to v3. Log file "
        #                 f"{self.log_filename_name} was created")

        config_file.write_storage_icloud3_configuration_file()
        self.migration_log_file.close()

    #-------------------------------------------------------------------------
    def _extract_config_parameters(self, config_yaml_recds):
        '''
        OrderedDict([('devices', [OrderedDict([('device_name', 'Gary-iPhone'),
        ('name', 'Gary'), ('email', 'gcobb321@gmail.com'),
        ('picture', 'gary.png'), ('track_from_zone', 'warehouse')]), OrderedDict([('device_name', 'lillian_iphone'),
        ('name', 'Lillian'), ('picture', 'lillian.png'), ('email', 'lilliancobb321@gmail.com')])]),
        ('display_text_as', ['gcobb321@gmail.com > gary_2fa@email.com', 'lilliancobb321@gmail.com > lillian_2fa@email.com',
        'twitter:@lillianhc > twitter:@lillian_twitter_handle', 'gary-real-email@gmail.com > gary_secret@email.com',
        'lillian-real-email@gmail.com > lillian_secret@email.com']),
        ('inzone_interval', '30 min'),
        ('display_zone_format', FNAME)])
        '''

        if config_yaml_recds == {}:
            return

        if CONF_DISPLAY_TEXT_AS in config_yaml_recds:
            display_text_as = DEFAULT_GENERAL_CONF[CONF_DISPLAY_TEXT_AS].copy()
            cdta_idx = 0
            for dta_text in config_yaml_recds[CONF_DISPLAY_TEXT_AS]:
                if dta_text.strip():
                    display_text_as[cdta_idx] = dta_text
                    cdta_idx += 1

            config_yaml_recds[CONF_DISPLAY_TEXT_AS] = display_text_as

        self.write_migration_log_msg(f"\nExtracting parameters")
        # temp_config_yaml_recds = config_yaml_recds.copy()
        # temp_config_yaml_recds[CONF_PASSWORD] = '********'
        #self.write_migration_log_msg(f"-- {temp_config_yaml_recds}")

        for pname, pvalue in config_yaml_recds.items():
            if pname == CONF_PASSWORD:
                self.write_migration_log_msg(f"-- {pname}: ********")
            else:
                self.write_migration_log_msg(f"-- {pname}: {pvalue}")

            if pname == CONF_DEVICES:
                pvalue = json.loads(json.dumps(pvalue))
                self.config_ic3_track_devices_fields.extend(\
                        self._get_devices_list_from_config_devices_parm(pvalue, CONFIG_IC3))

            else:
                self._set_non_device_parm_in_config_parameter_dictionary(pname, pvalue)

        return

    #-------------------------------------------------------------------------
    def _get_config_ic3_records(self):
        try:
            config_yaml_recds = {}

            # Get config_ic3.yaml file name from parameters, then reformat since adding to the '/config/ variable
            config_ic3_filename = Gb.ha_config_yaml_icloud3_platform.get(CONF_CONFIG_IC3_FILE_NAME, CONFIG_IC3)
            config_ic3_filename = config_ic3_filename.replace("config/", "")
            if config_ic3_filename.startswith('/'):
                config_ic3_filename = config_ic3_filename[1:]
            if config_ic3_filename.endswith('.yaml') is False:
                config_ic3_filename = f"{config_ic3_filename}.yaml"

            if instr(config_ic3_filename, "/"):
                pass

            elif os.path.exists(f"{Gb.ha_config_directory}{config_ic3_filename}"):
                config_ic3_filename = (f"{Gb.ha_config_directory}{config_ic3_filename}")

            elif os.path.exists(f"{Gb.icloud3_directory}/{config_ic3_filename}"):
                config_ic3_filename = (f"{Gb.icloud3_directory}/{config_ic3_filename}")

            config_ic3_filename = config_ic3_filename.replace("//", "/")

            self.write_migration_log_msg(f"Converting parameters, Source: {config_ic3_filename}")
            if os.path.exists(config_ic3_filename) is False:
                self.write_migration_log_msg(f" -- Skipped, {config_ic3_filename} not used")
                return {}

            Gb.config_ic3_yaml_filename = config_ic3_filename
            config_yaml_recds = yaml_loader.load_yaml(config_ic3_filename)

            # self.write_migration_log_msg(f"-- {config_yaml_recds}")

        except Exception as err:
            self.log_exception(err)

        return config_yaml_recds

    #-------------------------------------------------------------------------
    def _get_devices_list_from_config_devices_parm(self, conf_devices_parameter, source_file):
        '''
        Process the CONF_DEVICES parameter. This is the general routine for parsing
        the parameter and creating a dictionary (devices_list) containing values
        associated with each device_name.

        Input:      The CONF_DEVICES parameter
        Returns:    The dictionary with the fields associated with all of the devices
        '''
        devices_list = []
        for device in conf_devices_parameter:
            devicename = slugify(device[CONF_DEVICENAME])
            if devicename in self.devicename_list:
                continue
            self.devicename_list.append(devicename)
            conf_device = DEFAULT_DEVICE_CONF.copy()
            conf_device[CONF_IOSAPP_DEVICE] = f"Search: {devicename}"
            conf_device[CONF_TRACKING_MODE]= INACTIVE_DEVICE

            self.write_migration_log_msg(f"Extracted device: {devicename}")
            for pname, pvalue in device.items():
                self.write_migration_log_msg(f"    -- {pname}: {pvalue}")
                if pname in VALID_CONF_DEVICES_ITEMS:
                    if pname == CONF_DEVICENAME:
                        devicename = slugify(pvalue)

                        fname, device_type = self._extract_name_device_type(pvalue)
                        conf_device[CONF_IC3_DEVICENAME]    = devicename
                        conf_device[CONF_FNAME]             = fname
                        conf_device[CONF_FAMSHR_DEVICENAME] = devicename
                        conf_device[CONF_DEVICE_TYPE]       = device_type

                    #You can track from multiple zones, cycle through zones and check each one
                    #The value can be zone name or zone friendly name. Change to zone name.
                    elif pname == 'track_from_zone':
                            if instr(pvalue, 'home') is False:
                                pvalue += ',home'
                            pvalue = pvalue.replace(', ', ',').lower()
                            tfz_list = pvalue.split(',')
                            conf_device[CONF_TRACK_FROM_ZONES] = tfz_list

                    elif pname == CONF_EMAIL:
                        conf_device[CONF_FMF_EMAIL] = pvalue

                    elif pname == CONF_NAME:
                        conf_device[CONF_FNAME] = pvalue

                    elif pname == CONF_IOSAPP_SUFFIX:
                        if pvalue.startswith('_') is False:
                            pvalue = f"_{pvalue}"
                        conf_device[CONF_IOSAPP_DEVICE] = f"{devicename}{pvalue}"

                    elif pname == CONF_IOSAPP_ENTITY:
                            conf_device[CONF_IOSAPP_DEVICE] = pvalue

                    elif pname == CONF_NO_IOSAPP and pvalue:
                        conf_device[CONF_IOSAPP_DEVICE] = 'None'

                    elif pname == CONF_IOSAPP_INSTALLED and pvalue is False:
                        conf_device[CONF_IOSAPP_DEVICE] = 'None'

                    elif pname == CONF_TRACKING_METHOD:
                        if pvalue == 'fmf':
                            conf_device[CONF_FAMSHR_DEVICENAME] = 'None'
                        elif pvalue == 'iosapp':
                            conf_device[CONF_FAMSHR_DEVICENAME] = 'None'
                            conf_device[CONF_FMF_EMAIL] = 'None'


                    elif pname == CONF_PICTURE:
                        if instr(pvalue, 'www') is False:
                            pvalue = f"www/{pvalue}"
                        # pvalue = pvalue.replace('local', '').replace('www', '').replace('/', '')
                        conf_device[CONF_PICTURE] = pvalue

                    elif pname == CONF_INZONE_INTERVAL:
                        conf_device[CONF_INZONE_INTERVAL] = secs_to_hhmmss(time_str_to_secs(pvalue))
                    else:
                        conf_device[pname] = pvalue

            if "cancel_update" in conf_device:
                conf_device.pop("cancel_update")
            devices_list.append(conf_device)

        return devices_list

    #-------------------------------------------------------------------------
    def _set_non_device_parm_in_config_parameter_dictionary(self, pname, pvalue):
        '''
        Set the config_parameters[key] master parameter dictionary from the
        config_ic3 parameter file

        Input:      parameter name & value
        Output:     Valid parameters are added to the config_parameter[pname] dictionary
        '''
        try:
            if pname == "":
                return

            if pname == 'stationary_still_time':      pname = CONF_STAT_ZONE_STILL_TIME
            if pname == 'stationary_inzone_interval': pname = CONF_STAT_ZONE_INZONE_INTERVAL

            if pname in self.config_parm_general:
                self.config_parm_general[pname] = pvalue

            elif pname in self.config_parm_tracking:
                self.config_parm_tracking[pname] = pvalue

            elif pname in ['exclude_sensors', 'create_sensors']:
                self._set_sensors(pname, pvalue)

            elif pname == CONF_INZONE_INTERVALS:
                iztype_iztime = {}
                for iztype_iztimes in pvalue:
                    for iztype, iztime in iztype_iztimes.items():
                        iztype_iztime[iztype] = iztime

                inzone_intervals = {}
                inzone_intervals['default'] = iztype_iztime.get('inzone_interval', '02:00:00')
                inzone_intervals[IPHONE]    = iztype_iztime.get(IPHONE, '02:00:00')
                inzone_intervals[IPAD]      = iztype_iztime.get(IPAD, '02:00:00')
                inzone_intervals[WATCH]     = iztype_iztime.get(WATCH, '00:15:00')
                inzone_intervals[AIRPODS]   = iztype_iztime.get(AIRPODS, '00:15:00')
                inzone_intervals[NO_IOSAPP] = iztype_iztime.get(NO_IOSAPP, '00:15:00')
                self.config_parm_general[CONF_INZONE_INTERVALS] = inzone_intervals.copy()

            elif pname == 'stationary_zone_offset':
                sz_offset = pvalue.split(',')
                self.config_parm_general[CONF_STAT_ZONE_BASE_LATITUDE]  = float(sz_offset[0])
                self.config_parm_general[CONF_STAT_ZONE_BASE_LONGITUDE] = float(sz_offset[1])


        except Exception as err:
            self.log_exception(err)
            pass

        return

    #--------------------------------------------------------------------
    def _set_sensors(self, pname, pvalue):
        device_list            = []
        tracking_update        = []
        tracking_time_list     = []
        tracking_distance_list = []
        tracking_other_list    = []
        zone_list              = []
        other_list             = []

        sensor_list = []
        pvalue = f",{pvalue.replace(' ', '')},"
        if pname == 'exclude_sensors':
            for sensor_abbrev, sensor in SENSOR_ID_NAME_LIST.items():
                if instr(pvalue, f",{sensor_abbrev},") is False:
                    sensor_list.append(sensor)

        elif pname == 'create_sensors':
            for sensor_abbrev, sensor in SENSOR_ID_NAME_LIST.items():
                if instr(pvalue, f",{sensor_abbrev},"):
                    sensor_list.append(sensor)

        for sname in sensor_list:
            if sname in ['name', 'badge', 'battery', 'info',]:
                device_list.append(sname)
            if sname in ['interval', 'last_update', 'next_update', 'last_located']:
                tracking_update.append(sname)
            if sname in ['travel_time', 'travel_time_min']:
                tracking_time_list.append(sname)
            if sname in ['zone_distance', 'home_distance', 'dir_of_travel', 'moved_distance']:
                tracking_distance_list.append(sname)
            if sname in ['trigger', 'waze_distance', 'calc_distance', 'pll_count']:
                tracking_other_list.append(sname)
            if sname in ['zone', 'zone_fname', 'zone_name', 'zone_title', 'zone_timestamp']:
                if sname not in zone_list:
                    zone_list.append(sname)
            if sname in ['last_zone', 'last_zone_fname', 'last_zone_name', 'last_zone_title']:
                if 'last_zone' not in zone_list:
                    zone_list.append('last_zone')
            if sname in ['gps_accuracy', 'vertical_accuracy',   'altitude']:
                other_list.append(sname)

        Gb.conf_sensors['device']            = device_list
        Gb.conf_sensors['tracking_update']   = tracking_update
        Gb.conf_sensors['tracking_time']     = tracking_time_list
        Gb.conf_sensors['tracking_distance'] = tracking_distance_list
        Gb.conf_sensors['tracking_other']    = tracking_other_list
        Gb.conf_sensors['zone']              = zone_list
        Gb.conf_sensors['other']             = other_list

        return

    #--------------------------------------------------------------------
    def write_migration_log_msg(self, msg):
        '''
        Write a status message to the icloud3_migration.log file
        '''
        self.migration_log_file.write(f"{msg}\n")

    #--------------------------------------------------------------------
    def write_migration_config_items(self, dict_title, dict_items):
        '''
        Cycle through the dictionary. Write each item to the migration log
        '''
        self.write_migration_log_msg(f"{dict_title}")

        for pname, pvalue in dict_items.items():
            if type(pvalue) is list:
                self.write_migration_config_list_items(pname, pvalue)
                continue

            if pvalue == '':
                continue

            if pname == CONF_PASSWORD:
                self.write_migration_log_msg(f"  -- {pname}: ********")
            else:
                self.write_migration_log_msg(f"  -- {pname}: {pvalue}")

    #--------------------------------------------------------------------
    def write_migration_config_list_items(self, pname, pvalues):
        '''
        Cycle through the dictionary. Write each item to the migration log
        '''
        if pvalues == []:
            self.write_migration_log_msg(f"  -- {pname}: {pvalues}")

        elif type(pvalues[0]) is dict:
            for pvalue in pvalues:
                self.write_migration_config_items(pname.title(), pvalue)
        else:
            self.write_migration_log_msg(f"  -- {pname}: {pvalues}")

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #
    #   INITIALIZE THE GLOBAL VARIABLES WITH THE CONFIGURATION FILE PARAMETER
    #   VALUES
    #
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def _set_data_fields_from_config_parameter_dictionary(self):
        '''
        Set the iCloud3 variables from the configuration parameters
        '''

        # Convert operational parameters
        Gb.conf_profile[CONF_VERSION]                    = 0
        Gb.conf_profile[CONF_EVLOG_CARD_DIRECTORY]       = self.config_parm_general.get(CONF_EVLOG_CARD_DIRECTORY, V2_EVLOG_CARD_WWW_DIRECTORY)
        if instr(Gb.conf_profile[CONF_EVLOG_CARD_DIRECTORY], 'www') is False:
            Gb.conf_profile[CONF_EVLOG_CARD_DIRECTORY]   = f"www/{Gb.conf_profile[CONF_EVLOG_CARD_DIRECTORY]}"
        Gb.conf_profile[CONF_EVLOG_CARD_PROGRAM]         = self.config_parm_general.get(CONF_EVLOG_CARD_PROGRAM, EVLOG_CARD_WWW_JS_PROG)

        # Convert iCloud Account Parameters
        Gb.conf_tracking[CONF_USERNAME]                  = self.config_parm_tracking[CONF_USERNAME]
        Gb.conf_tracking[CONF_PASSWORD]                  = self.config_parm_tracking[CONF_PASSWORD]
        Gb.conf_tracking[CONF_DEVICES]                   = self.config_ic3_track_devices_fields

        # Convert General parameters
        Gb.conf_general[CONF_LOG_LEVEL]                  = self.config_parm_general[CONF_LOG_LEVEL]
        Gb.conf_general[CONF_UNIT_OF_MEASUREMENT]        = self.config_parm_general[CONF_UNIT_OF_MEASUREMENT].lower()
        #12/17/2022 (beta 1) - The time format was being converted to 12_hour_hour instead of 12_hour
        Gb.conf_general[CONF_TIME_FORMAT]                = (f"{self.config_parm_general[CONF_TIME_FORMAT]}-hour").replace('-hour-hour', '-hour')
        Gb.conf_general[CONF_TRAVEL_TIME_FACTOR]         = self.config_parm_general[CONF_TRAVEL_TIME_FACTOR]
        Gb.conf_general[CONF_MAX_INTERVAL]               = secs_to_hhmmss(time_str_to_secs(self.config_parm_general[CONF_MAX_INTERVAL]))
        Gb.conf_general[CONF_GPS_ACCURACY_THRESHOLD]     = self.config_parm_general[CONF_GPS_ACCURACY_THRESHOLD]
        Gb.conf_general[CONF_OLD_LOCATION_THRESHOLD]     = secs_to_hhmmss(time_str_to_secs(self.config_parm_general[CONF_OLD_LOCATION_THRESHOLD]))
        Gb.conf_general[CONF_DISPLAY_ZONE_FORMAT]        = self.config_parm_general[CONF_DISPLAY_ZONE_FORMAT].lower()
        Gb.conf_general[CONF_CENTER_IN_ZONE]             = self.config_parm_general[CONF_CENTER_IN_ZONE]
        Gb.conf_general[CONF_DISCARD_POOR_GPS_INZONE]    = self.config_parm_general.get(CONF_DISCARD_POOR_GPS_INZONE, False)
        Gb.conf_general[CONF_DISPLAY_TEXT_AS]           = self.config_parm_general[CONF_DISPLAY_TEXT_AS]

        # Convert Waze Parameters
        if CONF_WAZE_USED in self.config_parm_general:
            Gb.conf_general[CONF_WAZE_USED]              = self.config_parm_general[CONF_WAZE_USED]
        elif 'distance_method' in self.config_parm_general:
            Gb.conf_general[CONF_WAZE_USED]              = self.config_parm_general['distance_method'].lower() == 'waze'
        # Gb.conf_general[CONF_WAZE_REGION]                = self.config_parm_general[CONF_WAZE_REGION].lower()
        Gb.conf_general[CONF_WAZE_REGION]                = WAZE_SERVERS_BY_COUNTRY_CODE.get(Gb.country_code, 'row')
        Gb.conf_general[CONF_WAZE_MIN_DISTANCE]          = self.config_parm_general[CONF_WAZE_MIN_DISTANCE]
        Gb.conf_general[CONF_WAZE_MAX_DISTANCE]          = self.config_parm_general[CONF_WAZE_MAX_DISTANCE]
        Gb.conf_general[CONF_WAZE_REALTIME]              = self.config_parm_general[CONF_WAZE_REALTIME]

        # if Gb.conf_general[CONF_WAZE_USED]:
        #     waze_region_code = waze.waze_region_by_country_code()
            # if waze_region_code != Gb.conf_general[CONF_WAZE_REGION]:
            #     log_msg =  (f""
            #                 f"The current Waze Region ({Gb.conf_general[CONF_WAZE_REGION].upper()}) "
            #                 f"does not match the region ({waze_region_code}) "
            #                 f"for the HA Country Code ({Gb.location_info['country_code']}). "
            #                 f"The Region in the iCloud3 configuration was changed\n")
            #     self.write_migration_log_msg(log_msg)
            #     log_warning_msg(log_msg)

                # Gb.conf_general[CONF_WAZE_REGION] = waze_region_code.lower()
                # Gb.conf_general[CONF_WAZE_USED]   = (waze_region_code != '??')

        # Convert Stationary Zone Parameters
        if instr(self.config_parm_general[CONF_STAT_ZONE_STILL_TIME], ':'):
            Gb.conf_general[CONF_STAT_ZONE_STILL_TIME]   = self.config_parm_general[CONF_STAT_ZONE_STILL_TIME]
        else:
            Gb.conf_general[CONF_STAT_ZONE_STILL_TIME]   = secs_to_hhmmss(time_str_to_secs(self.config_parm_general[CONF_STAT_ZONE_STILL_TIME]))
        if instr(self.config_parm_general[CONF_STAT_ZONE_INZONE_INTERVAL], ':'):
            Gb.conf_general[CONF_STAT_ZONE_INZONE_INTERVAL] = self.config_parm_general[CONF_STAT_ZONE_INZONE_INTERVAL]
        else:
            Gb.conf_general[CONF_STAT_ZONE_INZONE_INTERVAL] = secs_to_hhmmss(time_str_to_secs(self.config_parm_general[CONF_STAT_ZONE_INZONE_INTERVAL]))
        Gb.conf_general[CONF_STAT_ZONE_BASE_LATITUDE]   = self.config_parm_general[CONF_STAT_ZONE_BASE_LATITUDE]
        Gb.conf_general[CONF_STAT_ZONE_BASE_LONGITUDE]  = self.config_parm_general[CONF_STAT_ZONE_BASE_LONGITUDE]

        self.write_migration_log_msg(f"\nCreated iCloud3 configuration file: {Gb.icloud3_config_filename}")

    #--------------------------------------------------------------------
    def _extract_name_device_type(self, devicename):
        '''Extract the name and device type from the devicename'''

        try:
            devicename = fname = devicename.lower()
            device_type = ""
            for ic3dev_type in DEVICE_TYPES:
                if devicename == ic3dev_type:
                    return (devicename, devicename)

                elif instr(devicename, ic3dev_type):
                    fnamew = devicename.replace(ic3dev_type, "")
                    fname  = fnamew.replace("_", "").replace("-", "").title().strip()
                    device_type = ic3dev_type
                    break

            if device_type == "":
                device_type = 'other'
                fname  = fname.replace("_", "").replace("-", "").title().strip()

        except Exception as err:
            # log_exception(err)
            pass

        return (fname, device_type)

    #--------------------------------------------------------------------
    def log_exception(self, err):
        _LOGGER.exception(err)
