
'''
Customized version of pyicloud.py to support iCloud3 Custom Component

Platform that supports importing data from the iCloud Location Services
and Find My Friends api routines. Modifications to pyicloud were made
by various people to include:
    - Original pyicloud - picklepete & Quantame
                        - https://github.com/picklepete

    - Updated and maintained by - Quantame
    - 2fa developed by          - Niccolo Zapponi (nzapponi)
    - Find My Friends component - Z Zeleznick

The picklepete version used imports for the services, utilities and exceptions
modules. They are now maintained by Quantame and have been modified by
Niccolo Zapponi Z Zeleznick.
These modules and updates have been incorporated into the pyicloud_ic3.py version
used by iCloud3.
'''

VERSION = '3.0.0'



from ..global_variables     import GlobalVariables as Gb
from ..const                import (AIRPODS_FNAME, CONF_PASSWORD,
                                    APPLE_SPECIAL_ICLOUD_SERVER_COUNTRY_CODE,
                                    HHMMSS_ZERO,
                                    FMF, FAMSHR, FMF_FNAME, FAMSHR_FNAME, NAME, ID,
                                    ICLOUD_HORIZONTAL_ACCURACY,
                                    LOCATION, TIMESTAMP, LOCATION_TIME, TRACKING_METHOD,
                                    ICLOUD_BATTERY_STATUS, BATTERY_STATUS_REFORMAT,
                                    )
from ..helpers.time_util    import (time_now_secs, secs_to_time, timestamp_to_time_utcsecs, )
from ..helpers.common       import (instr, obscure_field, )
from ..helpers.messaging    import (post_event, post_monitor_msg, _trace, _traceha,
                                    log_info_msg, log_error_msg, log_debug_msg, log_warning_msg, log_rawdata, log_exception)

from uuid       import uuid1
from requests   import Session, adapters
from tempfile   import gettempdir
from os         import path, mkdir
from re         import match
import inspect
import json
import http.cookiejar as cookielib
import logging
LOGGER = logging.getLogger(f"icloud3.pyicloud_ic3")

HEADER_DATA = {
    "X-Apple-ID-Account-Country": "account_country",
    "X-Apple-ID-Session-Id": "session_id",
    "X-Apple-Session-Token": "session_token",
    "X-Apple-TwoSV-Trust-Token": "trust_token",
    "scnt": "scnt",
}

DEVICE_STATUS_ERROR_500 = 500
INVALID_GLOBAL_SESSION_421 = 421
APPLE_ID_VERIFICATION_CODE_INVALID_404 = 404
AUTHENTICATION_NEEDED_421_450_500 = [421, 450, 500]
AUTHENTICATION_NEEDED_450 = 450
'''
https://developer.apple.com/library/archive/documentation/DataManagement/Conceptual/CloudKitWebServicesReference/ErrorCodes.html#//apple_ref/doc/uid/TP40015240-CH4-SW1

#Other Device Status Codes
SEND_MESSAGE_MSG_DISPLAYED = 200
REMOTE_WIPE_STARTED = 200
REMOVE_DEVICE_SUCCESS = 200
UPDATE_LOCATION_PREF_SUCCESS = 200
LOST_MODE_SUCCESS = 200
PLAY_SOUND_SUCCESS = 200
PLAY_SOUND_NEEDS_SAFETY_CONFIRM = 203
SEND_MESSAGE_MSG_SENT = 205
REMOTE_WIPE_SENT = 205
LOST_MODE_SENT = 205
LOCK_SENT = 205
PLAY_SOUND_SENT = 205
LOCK_SERVICE_FAILURE = 500
SEND_MESSAGE_FAILURE = 500
PLAY_SOUND_FAILURE = 500
REMOTE_WIPE_FAILURE = 500
UPDATE_LOCATION_PREF_FAILURE = 500
LOCK_SUCC_PASSCODE_SET = 2200
LOCK_SUCC_PASSCODE_NOT_SET_PASSCD_EXISTS = 2201
LOCK_SUCCESSFUL_2 = 2204
LOCK_FAIL_PASSCODE_NOT_SET_CONS_FAIL = 2403
LOCK_FAIL_NO_PASSCD_2 = 2406
'''

#--------------------------------------------------------------------
class PyiCloudPasswordFilter(logging.Filter):
    '''Password log hider.'''

    def __init__(self, password):
        super(PyiCloudPasswordFilter, self).__init__(password)


    def filter(self, record):
        #return True
        message = record.getMessage()
        if self.name in message:
            record.msg = message.replace(self.name, "*" * 8)
            record.args = []

        return True

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class PyiCloudSession(Session):
    '''iCloud session.'''

    def __init__(self, Service):
        self.Service = Service
        super().__init__()
        #self.FindMyiPhone = None

        # Increase the number of connections to prevent timeouts
        # authenticting the iCloud Account
        adapter = adapters.HTTPAdapter(pool_connections=20, pool_maxsize=20)

    def request(self, method, url, **kwargs):  # pylint: disable=arguments-differ

        # Charge logging to the right service endpoint
        callee = inspect.stack()[2]
        module = inspect.getmodule(callee[0])
        request_logger = logging.getLogger(module.__name__).getChild("http")

        if self.Service.password_filter not in request_logger.filters:
            request_logger.addFilter(self.Service.password_filter)


        has_retried = kwargs.get("retried", False)
        kwargs.pop("retried", False)
        retry_cnt = kwargs.get("retry_cnt", 0)
        kwargs.pop("retry_cnt", 0)

        if Gb.log_rawdata_flag:
            log_msg = (f"{secs_to_time(time_now_secs())}, {method}, {url}, {self.prefilter_rawdata(kwargs)}")
            log_rawdata("PyiCloud_ic3 iCloud Request", {'raw': log_msg})

        try:

            response = Session.request(self, method, url, **kwargs)


        except Exception as err:
            log_exception(err)
            self._raise_error(-2, "Failed to establish a new connection")

        content_type = response.headers.get("Content-Type", "").split(";")[0]
        json_mimetypes = ["application/json", "text/json"]

        try:
            data = response.json()
        except:
            data = None

        if Gb.log_rawdata_flag:
            log_msg = ( f"ResponseCode-{response.status_code} ")

            if (retry_cnt == 3 or response.status_code != 200 or response.ok is False):
                log_msg +=  (f", ResponseOK-{response.ok}, Headers-{response.headers}")
            #log_rawdata("PyiCloud_ic3 iCloud Response-Header", {'raw': log_msg})
            log_rawdata("PyiCloud_ic3 iCloud Response-Data", {'filter': self.prefilter_rawdata(data)})
            # log_rawdata("PyiCloud_ic3 iCloud Response-Data", {'raw': data})

        for header in HEADER_DATA:
            if response.headers.get(header):
                session_arg = HEADER_DATA[header]
                self.Service.session_data.update(
                    {session_arg: response.headers.get(header)})

        with open(self.Service.session_directory_filename, "w") as outfile:
            json.dump(self.Service.session_data, outfile)

        self.cookies.save(ignore_discard=True, ignore_expires=True)

        if (response.ok is False
                and (content_type not in json_mimetypes
                    or response.status_code in AUTHENTICATION_NEEDED_421_450_500)):

            try:
                # Handle re-authentication for Find My iPhone
                fmip_url = self.Service._get_webservice_url("findme")
                if retry_cnt == 0 and response.status_code in AUTHENTICATION_NEEDED_421_450_500 and fmip_url in url:
                    log_debug_msg("Re-authenticating Find My iPhone service")

                    try:
                        # If 450, authentication requires a sign in to the account
                        service = None if response.status_code == 450 else 'find'
                        self.Service.authenticate(True, service)

                    except PyiCloudAPIResponseException:
                        log_debug_msg("Re-authentication failed")

                    kwargs["retried"] = True
                    retry_cnt += 1
                    kwargs['retry_cnt'] = retry_cnt
                    return self.request(method, url, **kwargs)

            except Exception:
                pass

            if retry_cnt == 0 and response.status_code in AUTHENTICATION_NEEDED_421_450_500:
                self._log_debug_msg("AUTHENTICTION NEEDED, Status Code", response.status_code)

                kwargs["retried"] = True
                retry_cnt += 1
                kwargs['retry_cnt'] = retry_cnt

                return self.request(method, url, **kwargs)

            error_code, error_reason = self._resolve_error_code_reason(data)

            self._raise_error(response.status_code, error_reason)

        if content_type not in json_mimetypes:
            return response

        try:
            data = response.json()

        except:
            if not response.ok:
                msg = (f"Error handling data returned from iCloud, {response}")
                request_logger.warning(msg)
            return response

        error_code, error_reason = self._resolve_error_code_reason(data)

        if error_reason:
            self._raise_error(error_code, error_reason)

        return response

#------------------------------------------------------------------
    @staticmethod
    def _resolve_error_code_reason(data):
        '''
        Determine if there is an error message in the data returned.

        Return:
            error code - Error Code
            error reason - Text reason for the error
        '''

        code = reason = None
        if isinstance(data, dict):
            reason = data.get("error")
            reason = reason or data.get("errorMessage")
            reason = reason or data.get("reason")
            reason = reason or data.get("errorReason")

            code = data.get("errorCode")
            code = code or data.get("serverErrorCode")

            if (reason in [1, '1', '2fa Already Processed']
                    or code == 1):
                return None, None

        return code, reason

#------------------------------------------------------------------
    @staticmethod
    def _raise_error(code, reason):

        api_error = None
        if code is None and reason is None:
            return

        if reason in ("ZONE_NOT_FOUND", "AUTHENTICATION_FAILED"):
            reason = ("Please log into https://icloud.com/ to manually "
                    "finish setting up your iCloud service")
            api_error = PyiCloudServiceNotActivatedException(reason, code)

        elif code in AUTHENTICATION_NEEDED_421_450_500: #[204, 421, 450, 500]:
            log_info_msg(f"iCloud Account Authentication is needed ({code})")
            return

        elif reason ==  'Missing X-APPLE-WEBAUTH-TOKEN cookie':
            log_info_msg(f"iCloud Account Authentication is needed, No WebAuth Token")
            api_error = PyiCloud2FARequiredException()

        # 2fa needed that has already been requested and processed
        elif reason == '2fa Already Processed':
            return

        elif code in [400, 404]:
            reason = f"Apple ID Validation Code Invalid ({code})"

        elif reason == "ACCESS_DENIED":
            reason = (reason + ".  Please wait a few minutes then try again."
                                "The remote servers might be trying to throttle requests.")

        if api_error is None:
            api_error = PyiCloudAPIResponseException(reason, code)

        # log_error_msg(f"{api_error}")
        raise api_error

#------------------------------------------------------------------
    @staticmethod
    def _log_debug_msg(title, display_data):
        ''' Display debug data fields '''
        try:
            log_debug_msg(f"{title} -- {display_data}")
        except:
            log_debug_msg(f"{title} -- None")

#------------------------------------------------------------------
    @staticmethod
    def prefilter_rawdata(kwargs_json):
        '''
        Obscure account name and password in rawdata
        '''

        if kwargs_json is None:
            return None

        try:
            # if 'data' not in kwargs_json:
            #     return kwargs_json

            kwargs_dict = json.loads(kwargs_json['data'])
            if 'password' in kwargs_dict:       kwargs_dict['password']       = obscure_field(kwargs_dict['password'])
            if 'accountName' in kwargs_dict:    kwargs_dict['accountName']    = obscure_field(kwargs_dict['accountName'])
            if 'trustTokens' in kwargs_dict:    kwargs_dict['trustTokens']    = '... ...'
            if 'trustToken' in kwargs_dict:     kwargs_dict['trustToken']     = '... ...'
            if 'dsWebAuthToken' in kwargs_dict: kwargs_dict['dsWebAuthToken'] = '... ...'
            kwargs_json = json.dumps(kwargs_dict)

        except Exception as err:
            #log_exception(err)
            pass

        return kwargs_json

#------------------------------------------------------------------
    async def _async_session_request(self, method, url, **kwargs):
        return await Gb.hass.async_add_executor_job(
                                Session.request,
                                self,
                                method,
                                url,
                                **kwargs)


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   PyiCloud_RawData Object - Store all of the data related to the device. It is created
#   and updated in the FindMyPhoneSvcMgr.refresh_client module and is based on the
#   device_id. The Global Variable PyiCloud.RawData_by_device_id contains the object
#   pointer for each device_id.
#
#       - content = all of the data for this device_id
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class PyiCloudService():
    '''
    A base authentication class for the iCloud service. Handles the
    authentication required to access iCloud services.

    Usage:
        from pyicloud import PyiCloudService
        pyicloud = PyiCloudService('username@apple.com', 'password')
        pyicloud.iphone.location()
    '''

    # See if a country code suffix is needed to access iCloud servers in specific countries
    # Gb.country_code = 'cn'
    url_suffix = f".{Gb.country_code}" if Gb.country_code in APPLE_SPECIAL_ICLOUD_SERVER_COUNTRY_CODE else ''

    HOME_ENDPOINT = f"https://www.icloud.com{url_suffix}"
    SETUP_ENDPOINT = f"https://setup.icloud.com{url_suffix}/setup/ws/1"
    AUTH_ENDPOINT = "https://idmsa.apple.com/appleauth/auth"

    def __init__(   self, apple_id, password=None,
                    cookie_directory=None, session_directory=None,
                    verify=True, client_id=None, with_family=True,
                    called_from='notset'):

        if not apple_id:
            msg = "The Apple iCloud account username is not specified"
            raise PyiCloudFailedLoginException(msg)
        if not password:
            msg = "The Apple iCloud account password is not specified"
            raise PyiCloudFailedLoginException(msg)

        self.user        = {"accountName": apple_id, "password": password}
        self.apple_id    = apple_id
        self.called_from = called_from

        try:
            if self.init_stage['complete']:
                return self
        except:
            self._initialize_variables()


        if self.init_stage['setup_session'] is False:
            self._setup_password_filter(password)
            self._setup_cookie_files(cookie_directory)
            self._setup_PyiCloudSession(session_directory)
            self.init_stage['setup_session'] = True

            if called_from == 'config_flow':
                Gb.PyiCloudConfigFlow = self
            elif called_from == 'init':
                Gb.PyiCloudInit = self
            else:
                Gb.PyiCloud = self

        if self.init_stage['authenticate'] is False:
            post_monitor_msg(f"AUTHENTICATING PyiCloud, -{obscure_field(apple_id)} ({called_from})")
            self.authenticate()
            self.init_stage['authenticate'] = True

        if self.init_stage['setup_famshr'] is False:
            post_monitor_msg(f"CREATING PyiCloud FamShr, {obscure_field(apple_id)} ({called_from})")
            self.create_FamilySharing_object()
            self.init_stage['setup_famshr'] = True

        if self.init_stage['setup_fmf'] is False:
            post_monitor_msg(f"CREATING PyiCloud FmF, {obscure_field(apple_id)} ({called_from})")
            self.create_FindMyFriends_object()
            self.init_stage['setup_fmf'] = True

        self.init_stage['complete'] = True

#----------------------------------------------------------------------------
    def _initialize_variables(self):
        '''
        Initialize the PyiCloud variables
        '''

        log_info_msg(f"Initialize PyiCloud Service, establish iCloud Location Services connection")

        self.data      = {}
        # self.client_id = client_id or f"auth-{str(uuid1()).lower()}"
        self.client_id = f"auth-{str(uuid1()).lower()}"
        self.params    = { "clientBuildNumber": "2021Project52",
                        "clientMasteringNumber": "2021B29",
                        "ckjsBuildVersion": "17DProjectDev77",
                        "clientId": self.client_id[5:],  }

        self.with_family = True
        self.new_2fa_code_already_requested_flag = False

        # PyiCloud tracking method and raw data control objects
        self.FamilySharing               = None # PyiCloud_ic3 object for FamilySharig used to refresh the device's location
        self.FindMyFriends               = None # PyiCloud_ic3 object for FindMyFriends used to refresh the device's location
        self.RawData_by_device_id        = {}   # Device data for tracked devices, updated in Pyicloud famshr.refresh_client
        self.RawData_by_device_id_famshr = {}
        self.RawData_by_device_id_fmf    = {}

        self.init_stage   = {}
        self.init_stage['init_variables'] = True
        self.init_stage['authenticate']   = False
        self.init_stage['setup_session']  = False
        self.init_stage['setup_famshr']   = False
        self.init_stage['setup_fmf']      = False
        self.init_stage['complete']       = False

        # Gb.PyiCloud = self

#----------------------------------------------------------------------------
    def authenticate(self, refresh_session=False, service=None):
        '''
        Handles authentication, and persists cookies so that
        subsequent logins will not cause additional e-mails from Apple.
        '''

        login_successful = False
        self.authenticate_method = ""

        # Validate token - Consider authenticated if token is valid (POST=validate)
        if (refresh_session is False
                and self.session_data.get("session_token")
                and 'dsid' in self.params):
            log_info_msg("Checking session token validity")

            try:
                self.data = self._validate_token()
                login_successful = True
                self.authenticate_method += ", ValidateToken"

            except PyiCloudAPIResponseException:
                msg = "Invalid authentication token, will log in from scratch."

        # Authenticate with Service
        if login_successful is False and service != None:
            app = self.data["apps"][service]

            if "canLaunchWithOneFactor" in app and app["canLaunchWithOneFactor"] == True:
                log_debug_msg("Authenticating as %s for %s" % (self.user["accountName"], service))
                try:
                    self._authenticate_with_credentials_service(service)

                    login_successful = True
                    self.authenticate_method += (f", TrustToken/ServiceLogin")

                except:
                    log_debug_msg("Could not log into service. Attempting brand new login.")

        # Authenticate - Sign into icloud account (POST=/signin)
        if login_successful is False:
            log_info_msg(f"Authenticating account {obscure_field(self.user['accountName'])}, Using Account/PasswordSignin")

            data = dict(self.user)
            data["rememberMe"] = True
            data["trustTokens"] = []

            if self.session_data.get("trust_token"):
                data["trustTokens"] = [self.session_data.get("trust_token")]

            headers = self._get_auth_headers()

            if self.session_data.get("scnt"):
                headers["scnt"] = self.session_data.get("scnt")

            if self.session_data.get("session_id"):
                headers["X-Apple-ID-Session-Id"] = self.session_data.get("session_id")

            try:
                req = self.Session.post(
                    f"{self.AUTH_ENDPOINT}/signin",
                    params={"isRememberMeEnabled": "true"},
                    data=json.dumps(data),
                    headers=headers,)
                self.authenticate_method += ", Account/PasswordSignin"

            except PyiCloudAPIResponseException as error:
                msg = "Invalid email/password combination."
                raise PyiCloudFailedLoginException(msg, error)

            self._authenticate_with_token()

        self._webservices = self.data["webservices"]

        self.authenticate_method = self.authenticate_method[2:]
        log_info_msg(f"Authentication completed successfully, method-{self.authenticate_method}")

#----------------------------------------------------------------------------
    def _authenticate_with_token(self):
        '''Authenticate using session token. Return True if successful.'''
        data = {"accountCountryCode": self.session_data.get("account_country"),
                "dsWebAuthToken": self.session_data.get("session_token"),
                "extended_login": True,
                "trustToken": self.session_data.get("trust_token", ""),
                }

        try:
            req = self.Session.post(f"{self.SETUP_ENDPOINT}/accountLogin"
                                        f"?clientBuildNumber=2021Project52&clientMasteringNumber=2021B29"
                                        f"&clientId={self.client_id[5:]}",
                                        data=json.dumps(data))
            data = req.json()

        except PyiCloudAPIResponseException as error:
            msg = "Invalid authentication token."
            raise PyiCloudFailedLoginException(msg, error)

        self.data = req.json()
        self._update_dsid(self.data)

        return True

#----------------------------------------------------------------------------
    def _authenticate_with_credentials_service(self, service):
        '''Authenticate to a specific service using credentials.'''
        data = {"appName": service,
                "apple_id": self.user["accountName"],
                "password": self.user["password"],
                "accountCountryCode": self.session_data.get("account_country"),
                "dsWebAuthToken": self.session_data.get("session_token"),
                "extended_login": True,
                "trustToken": self.session_data.get("trust_token", ""),
                }

        try:
            log_debug_msg("Authenticate with credentials requested")
            self.Session.post(f"{self.SETUP_ENDPOINT}/accountLogin"
                        f"?clientBuildNumber=2021Project52&clientMasteringNumber=2021B29"
                        f"&clientId={self.client_id[5:]}",
                        data=json.dumps(data))

            self.data = self._validate_token()

        except Exception as err:
            log_exception(err)

        except PyiCloudAPIResponseException as error:
            log_exception(error)
            msg = "Invalid username/password combination."
            raise PyiCloudFailedLoginException(msg, error)

#----------------------------------------------------------------------------
    def _validate_token(self):
        '''Checks if the current access token is still valid.'''
        log_debug_msg("Checking session token validity")
        try:
            req = self.Session.post("%s/validate" % self.SETUP_ENDPOINT, data="null")
            log_debug_msg("Session token is still valid")
            return req.json()

        except PyiCloudAPIResponseException as err:
            log_debug_msg("Invalid authentication token")
            raise err

#----------------------------------------------------------------------------
    def _update_dsid(self, data):
        try:
            # check self.data returned and contains dsid
            if 'dsInfo' in data:
                if 'dsid' in data['dsInfo']:
                    self.params["dsid"]= str(data["dsInfo"]["dsid"])
            else:
                # if no dsid given delete it from self.params - until returned.  Otherwise is passing default incorrect dsid
                if 'dsid' in self.params:
                    self.params.pop("dsid")

        except:
            log_debug_msg(u"Error setting dsid field.")
            # if error, self.data None/empty delete
            if 'dsid' in self.params:
                self.params.pop("dsid")

        return

#----------------------------------------------------------------------------
    def _get_auth_headers(self, overrides=None):
        headers = { "Accept": "*/*",
                    "Content-Type": "application/json",
                    "X-Apple-OAuth-Client-Id": "d39ba9916b7251055b22c7f910e2ea796ee65e98b2ddecea8f5dde8d9d1a815d",
                    "X-Apple-OAuth-Client-Type": "firstPartyAuth",
                    "X-Apple-OAuth-Redirect-URI": "https://www.icloud.com",
                    "X-Apple-OAuth-Require-Grant-Code": "true",
                    "X-Apple-OAuth-Response-Mode": "web_message",
                    "X-Apple-OAuth-Response-Type": "code",
                    "X-Apple-OAuth-State": self.client_id,
                    "X-Apple-Widget-Key": "d39ba9916b7251055b22c7f910e2ea796ee65e98b2ddecea8f5dde8d9d1a815d",
                    }
            #"X-Apple-OAuth-State": "auth-" + self.client_id,

        if overrides:
            headers.update(overrides)
        return headers

#----------------------------------------------------------------------------
    def _setup_password_filter(self, password):
        '''
        Set up the password_filter, cookies and session files
        '''

        self.password_filter = PyiCloudPasswordFilter(password)
        LOGGER.addFilter(self.password_filter)
        Gb.HALogger.addFilter(self.password_filter)

#----------------------------------------------------------------------------
    def _setup_cookie_files(self, cookie_directory):
        '''
        Set up the password_filter, cookies and session files
        '''

        self.cookie_directory  = path.expanduser(path.normpath(cookie_directory))

        if not path.exists(self.cookie_directory):
            mkdir(self.cookie_directory)

#----------------------------------------------------------------------------
    def _setup_PyiCloudSession(self, session_directory):
        '''
        Set up the password_filter, cookies and session files
        '''

        self.cookie_directory  = path.expanduser(path.normpath(self.cookie_directory))
        self.session_directory = session_directory

        if not path.exists(self.cookie_directory):
            mkdir(self.cookie_directory)

        if not path.exists(self.session_directory):
            mkdir(self.session_directory)

        try:
            self.session_data = {}
            with open(self.session_directory_filename) as session_f:
                self.session_data = json.load(session_f)
        except:
            log_info_msg("Session file does not exist")

        if self.session_data.get("client_id"):
            self.client_id = self.session_data.get("client_id")
        else:
            self.session_data.update({"client_id": self.client_id})


        self.Session = PyiCloudSession(self)


        self.Session.verify = True
        self.Session.headers.update({"Origin": self.HOME_ENDPOINT, "Referer": self.HOME_ENDPOINT,})

        self.Session.cookies = cookielib.LWPCookieJar(filename=self.cookie_directory_filename)
        if path.exists(self.cookie_directory_filename):
            try:
                self.Session.cookies.load(ignore_discard=True, ignore_expires=True)
                log_debug_msg(f"Read Cookies from {self.cookie_directory_filename}")

            except:
                log_warning_msg(f"Failed to read cookie file {self.cookie_directory_filename}")

#----------------------------------------------------------------------------
    @property
    def cookie_directory_filename(self):
        '''Get path for cookiejar file.'''
        return path.join(
            self.cookie_directory,
            "".join([c for c in self.user.get("accountName") if match(r"\w", c)]),)

    @property
    def session_directory_filename(self):
        '''Get path for session data file.'''
        return path.join(self.session_directory,
                            "".join([c for c in self.user.get("accountName") if match(r"\w", c)]),)

    @property
    def authentication_method(self):
        '''
        Returns the type of authentication method performed
            - None = No authentication done
            - TrustToken = Authentication using trust token (/accountLogin)
            - ValidateToken = Trust token was validated (/validate)
            - AccountSignin = Signed into the account (/signin)
        '''
        authenticate_method = self.authenticate_method
        self.authenticate_method = ""
        return authenticate_method

    @property
    def requires_2sa(self):
        '''Returns True if two-step authentication is required.'''
        needs_2sa_flag = (self.data.get("dsInfo", {}).get("hsaVersion", 0) >= 1
                                and (self.data.get("hsaChallengeRequired", False))
                            or not self.is_trusted_session)

        return needs_2sa_flag

    @property
    def requires_2fa(self):
        '''Returns True if two-factor authentication is required.'''
        try:
            needs_2fa_flag = (self.data.get("dsInfo", {}).get("hsaVersion", 0) == 2
                                    and (self.data.get("hsaChallengeRequired", False)
                                or not self.is_trusted_session))

        except KeyError:
            needs_2fa_flag = True
        except Exception as err:
            log_exception(err)
            return False

        if needs_2fa_flag:
            log_debug_msg(f"NEEDS-2FA, is_trusted_session-{self.is_trusted_session}")

        return needs_2fa_flag

    @property
    def is_trusted_session(self):
        '''Returns True if the session is trusted.'''
        return self.data.get("hsaTrustedBrowser", False)

    @property
    def trusted_devices(self):
        '''Returns devices trusted for two-step authentication.'''
        url = f"{self.SETUP_ENDPOINT}/listDevices"
        request = self.Session.get(url, params=self.params)
        return request.json().get("devices")

    def new_log_in_needed(self, username):
        return username != self.apple_id

#----------------------------------------------------------------------------
    def send_verification_code(self, device):
        '''Requests that a verification code is sent to the given device.'''
        data = json.dumps(device)
        request = self.Session.post("%s/sendVerificationCode" % self.SETUP_ENDPOINT,
                                    params=self.params,
                                    data=data,)

        return request.json().get("success", False)

#----------------------------------------------------------------------------
    def validate_verification_code(self, device, code):
        '''Verifies a verification code received on a trusted device.'''
        device.update({"verificationCode": code, "trustBrowser": True})
        data = json.dumps(device)

        try:
            self.Session.post("%s/validateVerificationCode" % self.SETUP_ENDPOINT,
                                params=self.params,
                                data=data,)

        except PyiCloudAPIResponseException as error:
            if error.code == -21669:
                # Wrong verification code
                return False
            raise

        # Re-authenticate, which will both update the HSA data, and
        # ensure that we save the X-APPLE-WEBAUTH-HSA-TRUST cookie.
        self.authenticate()

        return not self.requires_2sa

#----------------------------------------------------------------------------
    def validate_2fa_code(self, code):
        '''Verifies a verification code received via Apple's 2FA system (HSA2).'''
        data = {"securityCode": {"code": code}}

        headers = self._get_auth_headers({"Accept": "application/json"})

        if self.session_data.get("scnt"):
            headers["scnt"] = self.session_data.get("scnt")

        if self.session_data.get("session_id"):
            headers["X-Apple-ID-Session-Id"] = self.session_data.get("session_id")

        try:
            self.Session.post(f"{self.AUTH_ENDPOINT}/verify/trusteddevice/securitycode",
                                    data=json.dumps(data),
                                    headers=headers,)

        except PyiCloudAPIResponseException as error:
            # Wrong verification code
            if error.code == -21669:
                log_error_msg("Code verification failed")
                return False
            raise

        log_debug_msg("Code verification successful")

        self.trust_session()
        return not self.requires_2sa

#----------------------------------------------------------------------------
    def trust_session(self):
        '''Request session trust to avoid user log in going forward.'''
        headers = self._get_auth_headers()

        if self.session_data.get("scnt"):
            headers["scnt"] = self.session_data.get("scnt")

        if self.session_data.get("session_id"):
            headers["X-Apple-ID-Session-Id"] = self.session_data.get("session_id")

        try:
            self.Session.get(f"{self.AUTH_ENDPOINT}/2sv/trust", headers=headers,)

            self._authenticate_with_token()
            return True

        except PyiCloudAPIResponseException:
            log_error_msg("Session trust failed")
            return False

#----------------------------------------------------------------------------
    def _get_webservice_url(self, ws_key):
        '''Get webservice URL, raise an exception if not exists.'''
        if self._webservices.get(ws_key) is None:
            raise PyiCloudServiceNotActivatedException("Webservice not available", ws_key)

        return self._webservices[ws_key]["url"]

#----------------------------------------------------------------------------
    @property
    def famshr_devices(self):
        '''
        Initializes the FindMyiPhone class, refresh the iCloud device data for all
        devices and create the PyiCloud_RawData object containing the data for all locatible devices.
        '''
        self.create_FamilySharing_object()

        # service_root = self._get_webservice_url("findme")
        # Gb.PyiCloud_FamilySharing = PyiCloud_FamilySharing(service_root, self.Session, self.params, self.with_family)

        # return Gb.PyiCloud_FamilySharing.response

#----------------------------------------------------------------------------
    def create_FamilySharing_object(self):
        '''
        Initializes the Family Sharing object, refresh the iCloud device data for all
        devices and create the PyiCloud_RawData object containing the data for all locatible devices.
        '''
        try:
            if self.FamilySharing is not None:
                return

            service_root       = self._get_webservice_url("findme")
            self.FamilySharing = PyiCloud_FamilySharing(self, service_root, self.Session, self.params, self.with_family)

        except Exception as err:
            log_exception(err)

#----------------------------------------------------------------------------
    @property
    def refresh_famshr_data(self):
        '''
        Refresh the iCloud device data for all devices and update the PyiCloud_RawData object
        for all locatible devices that are being tracked by iCloud3.
        '''
        self.FamilySharing.refresh_client()
        # return

#----------------------------------------------------------------------------

    def create_FindMyFriends_object(self):
        try:
            service_root = self._get_webservice_url("findme")  #fmf
            self.FindMyFriends = PyiCloud_FindMyFriends(self, service_root, self.Session, self.params)

        except Exception as err:
            log_exception(err)

#----------------------------------------------------------------------------
    def play_sound(self, device_id, subject="Find My iPhone Alert"):
        '''
        Send a request to the device to play a sound.
        It's possible to pass a custom message by changing the `subject`.
        '''

        service_root = self._get_webservice_url("findme")
        data = self.FamilySharing(service_root, self.Session, self.params, self.with_family,
                    task="PlaySound", device_id=device_id, subject=subject)
        return data


#----------------------------------------------------------------------------
    def __repr__(self):
        try:
            return (f"<PyiCloudService: {self.apple_id} ({self.called_from})>")
        except:
            return (f"<PyiCloudService: Undefined>")


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   Find my iPhone service
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class PyiCloud_FamilySharing():
    '''
    The 'Find my iPhone' iCloud service

    This connects to iCloud and return phone data including the near-realtime
    latitude and longitude.
    '''

    def __init__(self, PyiCloud, service_root, Session,
                params, with_family=False, task="RefreshData",
                device_id=None, subject=None, message=None,
                sounds=False, number="", newpasscode=""):

        self.Session     = Session
        self.PyiCloud    = PyiCloud
        self.params      = params
        self.with_family = with_family
        self.task        = task
        self.device_id   = device_id
        self.devices_without_location_data = []

        fmip_endpoint          = f"{service_root}/fmipservice/client/web"
        self._fmip_refresh_url = f"{fmip_endpoint}/refreshClient"
        self._fmip_sound_url   = f"{fmip_endpoint}/playSound"
        self._fmip_message_url = f"{fmip_endpoint}/sendMessage"
        self._fmip_lost_url    = f"{fmip_endpoint}/lostDevice"

        fmiDict =   {"clientContext":
                        { "appName": "Home Assistant", "appVersion": "0.118",
                        "inactiveTime": 1, "apiVersion": "2.2.2" }
                    }

        if task == "PlaySound":
            if device_id:
                self.play_sound(device_id, subject)
            return

        elif task == "Message":
            if device_id:
                self.display_message(device_id, subject, message)
            return

        elif task == "LostDevice":
            if device_id:
                self.lost_device(device_id, number, message, newpasscode="")
            return

        # FamShr Device information - These is used verify the device, display on the EvLog and in the Config Flow
        # device selection list on the iCloud3 Devices screen
        self.dup_device_fname_cnt        = {}       # Used to create a suffix for duplicate devicenames
        self.device_id_by_device_fname   = {}       # Example: {'Gary-iPhone': 'n6ofM9CX4j...'}
        self.device_fname_by_device_id   = {}       # Example: {'n6ofM9CX4j...': 'Gary-iPhone14'}
        self.device_info_by_device_fname = {}       # Example: {'Gary-iPhone': 'Gary-iPhone (iPhone 14 Pro (iPhone15,2)'}
        self.device_model_info_by_fname  = {}       # {'Gary-iPhone': [raw_model,model,model_display_name]}
                                                    # {'Gary-iPhone': ['iPhone15,2', 'iPhone', 'iPhone 14 Pro']}

        # Refresh the data
        self.refresh_client(device_id)


#----------------------------------------------------------------------------
    @property
    def timestamp_field(self):
        return 'timeStamp'

    @property
    def tracking_method(self):
        return FAMSHR_FNAME

#----------------------------------------------------------------------------
    def refresh_client(self, requested_by_devicename= None, _device_id=None,
                            _with_family=None, refreshing_poor_loc_flag=False):
        '''
        Refreshes the FindMyiPhoneService endpoint,
        This ensures that the location data is up-to-date.
        '''
        selected_device = _device_id   if _device_id else "all"
        fmly_param      = _with_family if _with_family is not None else self.with_family

        response = self.Session.post(self._fmip_refresh_url,
                                params=self.params,
                                data=json.dumps({"clientContext":
                                                    {   "fmly": fmly_param,
                                                        "shouldLocate": True,
                                                        "selectedDevice": selected_device,
                                                        "deviceListVersion": 1, }}),)

        try:
            self.response = response.json()

        except Exception as err:
            self.response = {}
            log_debug_msg("No data returned from fmi refresh request")

        if requested_by_devicename:
            post_monitor_msg(f"FamShr iCloudData Update RequestedBy-{requested_by_devicename}")

        self.update_device_location_data(requested_by_devicename, self.response.get("content", {}))

#----------------------------------------------------------------------------
    def update_device_location_data(self, requested_by_devicename=None, device_data=None):
        # content contains the device data and the location data
        # for device_info in self.response.get("content", {}):
        if device_data is None:
            return

        for device_info in device_data:
            device_id   = device_info[ID]
            device_name = device_info[NAME]
            monitor_msg = ''

            device_name       = device_name.replace(u'\xa0', ' ')
            device_name       = device_name.replace(u'\2019', "'")
            device_info[NAME] = device_name

            # Do not add device is no location data

            if (device_name in Gb.conf_famshr_devicenames
                    and Gb.start_icloud3_inprocess_flag):
                pass

            elif (LOCATION not in device_info
                    or device_info[LOCATION] == {}
                    or device_info[LOCATION] is None):
                if device_id not in self.devices_without_location_data:
                    self.devices_without_location_data.append(device_id)
                    monitor_msg = ( f"NO LOCATION FamShr PyiCloudData-"
                                    f"{device_name}/{device_id[:8]}, "
                                    f"{device_info['modelDisplayName']} "
                                    f"({device_info['rawDeviceModel']})")
                    if Gb.EvLog:
                        post_monitor_msg(monitor_msg)
                    else:
                        log_debug_msg(monitor_msg)

                log_rawdata(f"FamShr PyiCloud Device - No Location Data - <{device_name}>", device_info)

                if device_name not in Gb.conf_famshr_devicenames:
                    continue

            monitor_msg = ''
            if device_id not in self.PyiCloud.RawData_by_device_id:
                self._create_RawData_object(device_id, device_name, device_info)

            else:
                _RawData = self.PyiCloud.RawData_by_device_id[device_id]

                _RawData.save_new_device_data(device_info)
                requested_by_flag = ' *' if requested_by_devicename == _RawData.devicename else ''

                log_rawdata(f"FamShr PyiCloud Device Data - "
                            f"<{device_name}/{_RawData.devicename}>", _RawData.device_data)

                monitor_msg = ( f"UPDATED FamShr PyiCloudData-"
                                f"{_RawData.devicename}, "
                                f"{_RawData.location_time}/"
                                f"{_RawData.gps_accuracy}m"
                                f"{requested_by_flag}")
                if Gb.EvLog:
                    post_monitor_msg(monitor_msg)
                else:
                    log_debug_msg(monitor_msg)

        # if not self.PyiCloud.RawData_by_device_id:
        #     raise PyiCloudNoDevicesException()

#----------------------------------------------------------------------------
    def _create_RawData_object(self, device_id, device_name, device_info):

        _RawData = PyiCloud_RawData(device_id, device_info, self.Session, self.params,
                                    'FamShr', 'timeStamp',
                                    self,
                                    device_name,
                                    sound_url=self._fmip_sound_url,
                                    lost_url=self._fmip_lost_url,
                                    message_url=self._fmip_message_url,)

        self.PyiCloud.RawData_by_device_id[device_id]        = _RawData
        self.PyiCloud.RawData_by_device_id_famshr[device_id] = _RawData

        fname = _RawData.famshr_device_fname
        self.device_id_by_device_fname[fname]     = device_id
        self.device_fname_by_device_id[device_id] = fname
        self.device_info_by_device_fname[fname]   = _RawData.famshr_device_info
        self.device_model_info_by_fname[fname]    = _RawData.famshr_device_model_info

        log_rawdata(f"FamShr PyiCloud Device Data - <{device_name}>", _RawData.device_data)

        monitor_msg = (f"ADDED FamShr PyiCloudDevice-{device_name}/{device_id[:8]}")

        if Gb.EvLog:
            post_monitor_msg(monitor_msg)
        else:
            log_debug_msg(monitor_msg)

#----------------------------------------------------------------------------
    def play_sound(self, device_id, subject):
        '''
        Send a request to the device to play a sound.
        It's possible to pass a custom message by changing the `subject`.
        '''
        if not subject:
            subject = "Find My iPhone Alert"

        data = json.dumps(
            {"device": device_id, "subject": subject, "clientContext": {"fmly": True}, }
        )
        self.Session.post(self._fmip_sound_url, params=self.params, data=data)
        return

#----------------------------------------------------------------------------
    def display_message(self, device_id, subject="Find My iPhone Alert",
                message="This is a note", sounds=False):
        '''
        Send a request to the device to display a message.
        It's possible to pass a custom message by changing the `subject`.
        '''
        data = json.dumps(
            {"device": device_id, "subject": subject, "sound": sounds,
                "userText": True, "text": message, }
        )
        self.Session.post(self._fmip_message_url, params=self.params, data=data)
        return

#----------------------------------------------------------------------------
    def lost_device(self, device_id, number, message="This iPhone has been lost. Please call me.",
                newpasscode=""):
        '''
        Send a request to the device to trigger 'lost mode'.

        The device will show the message in `text`, and if a number has
        been passed, then the person holding the device can call
        the number without entering the passcode.
        '''
        data = json.dumps(
            {"text": message, "userText": True, "ownerNbr": number, "lostModeEnabled": True,
                "trackingEnabled": True, "device": device_id, "passcode": newpasscode, }
        )
        self.Session.post(self._fmip_lost_url, params=self.params, data=data)
        return

#----------------------------------------------------------------------------
    def __repr__(self):
        try:
            return (f"<PyiCloud.FamilySharing: {self.PyiCloud.apple_id}>")
        except:
            return (f"<PyiCloud.FamilySharing: NotSetUp>")


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   Find my Friends service
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class PyiCloud_FindMyFriends():
    '''
    The 'Find My' (aka 'Find My Friends') iCloud service

    This connects to iCloud and returns friend's data including
    latitude and longitude.
    '''

    def __init__(self, PyiCloud, service_root, Session, params):

        self.Session          = Session
        self.PyiCloud         = PyiCloud
        self.params           = params
        self._service_root    = service_root
        self._friend_endpoint = f"{self._service_root}/fmipservice/client/fmfWeb/initClient"
        self.refresh_always   = False
        self.response         = {}
        self.devices_without_location_data = []

        # FmF Device information - These is used verify the device, display on the EvLog and in the Config Flow
        # device selection list on the iCloud3 Devices screen
        self.device_id_by_fmf_email      = {}
        self.fmf_email_by_device_id      = {}
        self.device_info_by_fmf_email    = {}
        self.device_form_icloud_fmf_list = []

        self.refresh_client()

        self._update_fmf_email_tables()

    @property
    def timestamp_field(self):
        return 'timestamp'

    @property
    def tracking_method(self):
        return FMF_FNAME

#----------------------------------------------------------------------------
    def refresh_client(self, requested_by_devicename=None, refreshing_poor_loc_flag=False):
        '''
        Refreshes all data from 'Find My' endpoint,
        '''
        params = dict(self.params)

        # This is a request payload we mock to fetch the data
        mock_payload = json.dumps(
            {
                "clientContext": {
                    "appVersion": "1.0",
                    "contextApp": "com.icloud.web.fmf",
                    "mapkitAvailable": True,
                    "productType": "fmfWeb",
                    "tileServer": "Apple",
                    "userInactivityTimeInMS": 537,
                    "windowInFocus": False,
                    "windowVisible": True,
                },
                "dataContext": None,
                "serverContext": None,
            }
        )
        try:
            response = self.Session.post(self._friend_endpoint, data=mock_payload, params=params)
        except:
            self.response = {}
            log_debug_msg("No data returned on friends refresh request")

        try:
            self.response = response.json()
        except:
            self.response = {}
            log_debug_msg("No data returned on friends refresh request")

        if requested_by_devicename:
            post_monitor_msg(f"FmF iCloudData Update RequestedBy-{requested_by_devicename}")

        try:
            device_name = ''
            for device_info in self.response.get('locations', {}):
                device_id   = device_info[ID]
                monitor_msg = ''

                # Device was already set up or rejected
                if device_id in self.devices_without_location_data:
                    continue

                # Update PyiCloud_RawData with data just received for tracked devices
                monitor_msg = ''
                if device_id in self.PyiCloud.RawData_by_device_id:
                    if device_id in Gb.Devices_by_icloud_device_id:
                        _RawData = self.PyiCloud.RawData_by_device_id[device_id]

                        _RawData.save_new_device_data(device_info)
                        requested_by_flag = ' *' if requested_by_devicename == _RawData.devicename else ''

                        log_rawdata(f"FmF PyiCloud Device Data - <{_RawData.devicename}>", _RawData.device_data)

                        monitor_msg = (f"UPDATED FmF PyiCloudData > "
                                        f"{_RawData.devicename}, "
                                        f"{_RawData.location_time}/"
                                        f"{_RawData.gps_accuracy}m"
                                        f"{requested_by_flag}")
                        if Gb.EvLog:
                            post_monitor_msg(monitor_msg)
                        else:
                            log_debug_msg(monitor_msg)

                else:
                    self._create_RawData_object(device_id, device_name, device_info)

            return self.response

        except Exception as err:
            log_exception(err)
            return None

#----------------------------------------------------------------------------
    def _create_RawData_object(self, device_id, device_name, device_info):
        _RawData = PyiCloud_RawData(device_id, device_info, self.Session, self.params,
                                    'FmF', 'timestamp',
                                    self,
                                    device_name,
                                    sound_url=None, lost_url=None, message_url=None,)

        self.PyiCloud.RawData_by_device_id[device_id]     = _RawData
        self.PyiCloud.RawData_by_device_id_fmf[device_id] = _RawData

        log_rawdata(f"FmF PyiCloud Device Data - <{_RawData.devicename}>", _RawData.device_data)

        monitor_msg = (f"ADDED FmF PyiCloudDevice-{device_name}/{device_id[:8]}")

        if (LOCATION not in device_info
                or device_info[LOCATION] == {}
                or device_info[LOCATION] is None):
            monitor_msg += " (No Location Data)"

        if Gb.EvLog:
            post_monitor_msg(monitor_msg)
        else:
            log_debug_msg(monitor_msg)

#----------------------------------------------------------------------------
    def _update_fmf_email_tables(self):

        fmf_friends_data = {'emails': self.contact_details,
                            'invitationFromHandles': self.followers,
                            'invitationAcceptedHandles': self.following}

        for fmf_email_field, Pyicloud_FmF_data in fmf_friends_data.items():
            if Pyicloud_FmF_data is None:
                continue

            for friend in Pyicloud_FmF_data:
                friend_emails = friend.get(fmf_email_field)
                full_name     = (f"{friend.get('firstName', '')} {friend.get('lastName', '')}")
                full_name     = full_name.strip()
                device_id     = friend.get('id')

                # extracted_fmf_devices.append((device_id, friend_emails))
                for friend_email in friend_emails:
                    self.device_id_by_fmf_email[friend_email] = device_id
                    self.fmf_email_by_device_id[device_id]    = friend_email
                    friend_email_full_name = f"{friend_email} ({full_name})" if full_name else friend_email
                    if (friend_email not in self.device_info_by_fmf_email or full_name):
                        self.device_info_by_fmf_email[friend_email] = f"{friend_email_full_name}"

#----------------------------------------------------------------------------
    def contact_id_for(self, identifier, default=None):
        '''
        Returns the contact id of your friend with a given identifier
        '''
        lookup_key = "phones"
        if "@" in identifier:
            lookup_key = "emails"

        def matcher(item):
            '''Returns True iff the identifier matches'''
            hit = item.get(lookup_key)
            if not isinstance(hit, list):
                return hit == identifier
            return any([el for el in hit if el == identifier])

        candidates = [
            item.get(ID, default)
            for item in self.contact_details
            if matcher(item)]
        if not candidates:
            return default
        return candidates[0]

#----------------------------------------------------------------------------
    def location_of(self, contact_id, default=None):
        '''
        Returns the location of your friend with a given contact_id
        '''
        candidates = [
            item.get("location", default)
            for item in self.locations
            if item.get(ID) == contact_id]
        if not candidates:
            return default
        return candidates[0]

#----------------------------------------------------------------------------
    @property
    def data(self):
        '''
        Convenience property to return data from the 'Find My' endpoint.
        Call `refresh_client()` before property access for latest data.
        '''
        if not self.response:
            self.refresh_client()
        return self.response

    @property
    def locations(self):
        '''Returns a list of your friends' locations'''
        return self.response.get("locations", [])

    @property
    def followers(self):
        '''Returns a list of friends who follow you'''
        return self.response.get("followers")

    @property
    def following(self):
        '''Returns a list of friends who you follow'''
        return self.response.get("following")

    @property
    def contact_details(self):
        '''Returns a list of your friends contact details'''
        return self.response.get("contactDetails")

    @property
    def my_prefs(self):
        '''Returns a list of your own preferences details'''
        return self.response.get("myPrefs")

    @property
    def device_identifier(self):
        return  (f"{self.response.get('firstName', '')} {self.response.get('lastName', '')}").strip()

    def __repr__(self):
        try:
            return (f"<PyiCloud.FindMyFriends: {self.PyiCloud.apple_id}>")
        except:
            return (f"<PyiCloud.FindMyFriends: NotSetUp>")



#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   PyiCloud_RawData Object - Store all of the data related to the device. It is created
#   and updated in the FindMyPhoneSvcMgr.refresh_client module and is based on the
#   device_id. The Global Variable PyiCloud.RawData_by_device_id contains the object
#   pointer for each device_id.
#
#       - content = all of the data for this device_id
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class PyiCloud_RawData():
    '''
    PyiCloud_Device stores all the device data for Family Sharing and Find-my-Friends
    tracking methods. FamShr device_data contains the device info and the location
    FmF contains the location
    '''

    def __init__(self, device_id, device_data, Session, params,
                        tracking_method, timestamp_field,
                        FamShr_FmF, device_name,
                        sound_url=None, lost_url=None, message_url=None, ):

        self.device_id       = device_id
        self.device_data     = device_data
        self.Session         = Session
        self.params          = params
        self.tracking_method = tracking_method
        self.timestamp_field = timestamp_field
        self.FamShr_FmF      = FamShr_FmF
        self.name            = device_name

        self.Device          = Gb.Devices_by_icloud_device_id.get(device_id)
        self.devicename      = self.Device.devicename if self.Device else device_id[:8]
        self.update_secs     = time_now_secs()
        self.location_secs   = 0
        self.location_time   = HHMMSS_ZERO
        self.last_used_location_secs = 0
        self.last_used_location_time = HHMMSS_ZERO

        self.sound_url   = sound_url
        self.lost_url    = lost_url
        self.message_url = message_url

        self.set_located_time()
        self.device_data[TRACKING_METHOD] = self.tracking_method

#----------------------------------------------------------------------
    @property
    def device_id8(self):
        return self.device_id[:8]

#----------------------------------------------------------------------
    @property
    def device_identifier(self):
        '''
        Format device name:
            - iPhone 14,2 (iPhone15,2)
            - Gary-iPhone
        '''
        if self.tracking_method_FAMSHR:
            display_name = self.device_data['deviceDisplayName'].split(' (')[0]
            display_name = display_name.replace('Series ', '')
            if self.device_data.get('rawDeviceModel').startswith(AIRPODS_FNAME):
                device_class = AIRPODS_FNAME
            else:
                device_class = self.device_data.get('deviceClass', '')
            raw_model = self.device_data.get('rawDeviceModel', device_class).replace('_', '')

            return (f"{display_name} ({raw_model}").replace("’", "'")

        elif self.tracking_method_FMF:
            full_name = (f"{self.device_data.get('firstName', '')} {self.device_data.get('lastName', '')}").strip()
            return full_name.replace("’", "'")

        else:
            return self.name.replace("’", "'")

#----------------------------------------------------------------------
    @property
    def famshr_device_fname(self):
        if self.tracking_method_FAMSHR:
            _FamShr = self.FamShr_FmF
            # Remove non-breakable space and right quote mark
            fname = self.name.replace("\xa0", " ").replace("’", "'")

            if fname not in _FamShr.dup_device_fname_cnt:
                _FamShr.dup_device_fname_cnt[fname] = 1

            if fname in _FamShr.device_id_by_device_fname:
                dup_fname = f"{fname}{'*'*_FamShr.dup_device_fname_cnt[fname]}"
                _FamShr.device_id_by_device_fname[dup_fname]      = _FamShr.device_id_by_device_fname[fname]
                _FamShr.device_fname_by_device_id[self.device_id] = dup_fname
                _FamShr.device_info_by_device_fname[dup_fname]    = _FamShr.device_info_by_device_fname[fname]
                _FamShr.dup_device_fname_cnt[fname] += 1

            self.fname = fname
            return fname

        elif self.tracking_method_FMF:
            _FmF = self.FamShr_FmF
            pass

#----------------------------------------------------------------------
    @property
    def famshr_device_info(self):
        info = f"{self.fname} ({self.device_identifier})"

        return info

#----------------------------------------------------------------------
    @property
    def famshr_device_display_name(self):
        display_name = self.device_data['deviceDisplayName'].split(' (')[0]
        display_name = display_name.replace('Series ', '')

        return display_name

#----------------------------------------------------------------------
    @property
    def famshr_device_model_info(self):
        model_info = [  self.device_data['rawDeviceModel'].replace("_", ""),        # iPhone15,2
                        self.device_data['modelDisplayName'],      # iPhone
                        self.famshr_device_display_name]     # iPhone 14 Pro

        return model_info

#----------------------------------------------------------------------
    @property
    def tracking_method_FMF(self):
        return (self.tracking_method in [FMF, FMF_FNAME])

    @property
    def tracking_method_FAMSHR(self):
        return (self.tracking_method in [FAMSHR, FAMSHR_FNAME])

    #** Added 5/3/2022
    @property
    def gps_accuracy(self):
        """ Get location gps accuracy or -1 if not available """

        try:
            return round(self.location[ICLOUD_HORIZONTAL_ACCURACY])
        except:
            return 9999

    @property
    def is_gps_poor(self):
        return (self.gps_accuracy > Gb.gps_accuracy_threshold
                    or self.gps_accuracy == 9999)

    @property
    def is_gps_good(self):
        return not self.is_gps_poor

    @property
    def gps_accuracy_msg(self):
        """ GPS Accuracy text if available or unknown """
        if self.gps_accuracy == 9999:
            return  'Unknown'
        return round(self.gps_accuracy)

    def save_new_device_data(self, device_data):
        '''Update the device data.'''
        self.device_data.clear()
        self.device_data.update(device_data)
        self.set_located_time()
        self.device_data[TRACKING_METHOD] = self.tracking_method
        return

#----------------------------------------------------------------------------
    def status(self, additional_fields=[]):  # pylint: disable=dangerous-default-value
        '''
        Returns status information for device.
        This returns only a subset of possible properties.
        '''
        self.FamShr_FmF.refresh_client(self.device_id, with_family=True)

        fields = ["batteryLevel", "deviceDisplayName", "deviceStatus", "name"]
        fields += additional_fields

        properties = {}
        for field in fields:
            properties[field] = self.location.get(field)

        return properties

#----------------------------------------------------------------------------
    @property
    def is_location_data_available(self):

        return not (LOCATION not in self.device_data
                    or self.device_data[LOCATION] == {}
                    or self.device_data[LOCATION] is None)
#----------------------------------------------------------------------------
    def set_located_time(self):

        try:
            if self.is_location_data_available is False:
                self.device_data[LOCATION] = {self.timestamp_field: 1000}

            self.device_data[LOCATION][TIMESTAMP]     = int(self.device_data[LOCATION][self.timestamp_field] / 1000)
            self.device_data[LOCATION][LOCATION_TIME] = secs_to_time(self.device_data[LOCATION][TIMESTAMP])
            self.location_secs = self.device_data[LOCATION][TIMESTAMP]
            self.location_time = self.device_data[LOCATION][LOCATION_TIME]

        except TypeError:
            # This will happen if there is no location data in device_data
            self.device_data[LOCATION] = {TIMESTAMP: 0, LOCATION_TIME: HHMMSS_ZERO}
            self.location_secs = 0
            self.location_time = HHMMSS_ZERO

        except Exception as err:
            log_exception(err)
            self.device_data[LOCATION] = {TIMESTAMP: 0, LOCATION_TIME: HHMMSS_ZERO}
            self.location_secs = 0
            self.location_time = HHMMSS_ZERO


        self.update_secs = time_now_secs()

        # Reformat and convert batteryStatus
        try:
            battery_status = self.device_data[ICLOUD_BATTERY_STATUS].lower()
            self.device_data[ICLOUD_BATTERY_STATUS] = BATTERY_STATUS_REFORMAT.get(battery_status, battery_status)
        except:
            pass

#----------------------------------------------------------------------------
    @property
    def data(self):
        '''Returns all of the device's data'''
        return self.device_data

    @property
    def location(self):
        '''Return the device's location data'''
        return self.device_data["location"]

    def __repr__(self):
        try:
            return f"<PyiCloud_RawData: {self.name}-{self.tracking_method}-{self.device_id[:8]}"
        except:
            return f"<PyiCloud_RawData: Undefined>"



#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
#   Exceptions (exceptions.py)
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
'''Library exceptions.'''


class PyiCloudException(Exception):
    '''Generic iCloud exception.'''
    pass

#----------------------------------------------------------------------------
class PyiCloudAPIResponseException(PyiCloudException):
    '''iCloud response exception.'''
    def __init__(self, reason, code=None, retry=False):

        self.reason = reason
        self.code = code
        message = reason or ""
        if code:
            message += (f" (Status Code {code})")
        if retry:
            message += ". Retrying ..."

        super(PyiCloudAPIResponseException, self).__init__(message)

#----------------------------------------------------------------------------
class PyiCloudServiceNotActivatedException(PyiCloudAPIResponseException):
    '''iCloud service not activated exception.'''
    pass

#----------------------------------------------------------------------------
class PyiCloudFailedLoginException(PyiCloudException):
    '''iCloud failed login exception.'''
    pass

#----------------------------------------------------------------------------
class PyiCloud2FARequiredException(PyiCloudException):
    '''iCloud 2SA required exception.'''
    pass

#----------------------------------------------------------------------------
class PyiCloudNoStoredPasswordAvailableException(PyiCloudException):
    '''iCloud no stored password exception.'''
    pass

#----------------------------------------------------------------------------
class PyiCloudNoDevicesException(PyiCloudException):
    '''iCloud no device exception.'''
    pass
