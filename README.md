![](https://img.shields.io/pypi/v/pysecuritas) ![](https://img.shields.io/pypi/pyversions/pysecuritas.svg) ![](https://pypi.org/project/pysecuritas/) ![](https://img.shields.io/pypi/dm/pysecuritas) ![](https://img.shields.io/github/license/Cebeerre/pysecuritas)

# Securitas Direct API Client

Client to access Securitas Direct through the API used by the following mobile Apps:

- [Android App](https://play.google.com/store/apps/details?id=com.securitasdirect.android.mycontrol&hl=en&gl=US)
- [IOS App](https://apps.apple.com/es/app/my-verisure-securitas-direct/id385076046)

If you have a working account in the app, the client should work as well.

[API specification and known projects](https://github.com/Cebeerre/SecuritasDirectAPI)

**_NOTE:_** THIS PROJECT IS NOT IN ANY WAY ASSOCIATED WITH OR RELATED TO THE SECURITAS DIRECT-VERISURE GROUP COMPANIES. The information here and online is for educational and resource purposes only and therefore the developers do not endorse or condone any inappropriate use of it, and take no legal responsibility for the functionality or security of your alarms and devices.

# Installing and Supported Versions
pysecuritas is available on PyPI and officially supports Python 2.7 & 3.5+:

`$ python -m pip install pysecuritas`

# Usage
## Command line
```
usage: pysecuritas [options]

Python library to retrieve and interact with securitas devices.

positional arguments:
  command               ARM: arm all sensors (inside)
                        ARMDAY: arm in day mode (inside)
                        ARMNIGHT: arm in night mode (inside)
                        PERI: arm (only) the perimeter sensors
                        DARM: disarm everything (not the annex)
                        ARMANNEX: arm the secondary alarm
                        DARMANNEX: disarm the secondary alarm
                        EST: return the panel status
                        ACT_V2: get the activity log
                        SRV: SIM Number and INSTIBS
                        MYINSTALLATION: Sensor IDs and other info
                        IMG: Take a picture (requires -s)

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Username used in the web page/mobile app.
  -p PASSWORD, --password PASSWORD
                        Password used in the web page/mobile app.
  -i INSTALLATION, --installation INSTALLATION
                        Installation/Facility number (appears on the website).
  -c COUNTRY, --country COUNTRY
                        Your country: ES, IT, FR, GB, PT ...
  -l LANGUAGE, --language LANGUAGE
                        Your language: es, it, fr, en, pt ...
  -s SENSOR, --sensor SENSOR
                        The sensor ID (to take a picture using IMG)
```

Example:

`$ ./pysecuritas.py -u michael -p mypassword -i 12345 -c GB -l en EST`

You'll get a json with the API output:

```
{
  "RES": "OK",
  "STATUS": "0",
  "MSG": "Your Alarm is deactivated",
  "NUMINST": "12345"
}
```

## API
You can use it as well as a python class so you can use it in your integrations:
There three main api endpoints:
- **alarm**: provides access to alarm actions such as arm and disarm
- **camera**: takes snapshots from camera sensors
- **installation**: retrieves basic information about the installation

Example getting alarm status: 
```
>>> from pysecuritas.core.session import Session
>>> from pysecuritas.api.alarm import Alarm
>>> session = Session(username, password, installation, country, language, sensor)
>>> session.connect()
>>> output = Alarm(session).get_status()
>>> output
OrderedDict([('RES', 'OK'), ('STATUS', '0'), ('MSG', 'Your Alarm is deactivated'), ('NUMINST', '12345')])
```
