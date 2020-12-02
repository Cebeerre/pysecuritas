# Securitas Direct API Client

Client to access Securitas Direct through the API used by the following mobile Apps:

- [Android App](https://play.google.com/store/apps/details?id=com.securitasdirect.android.mycontrol&hl=en&gl=US)
- [IOS App](https://play.google.com/store/apps/details?id=com.securitasdirect.android.mycontrol&hl=en&gl=US)

If you have a working account in the app, the client should work as well.

[API specification and known projects](https://github.com/Cebeerre/SecuritasDirectAPI)

**_NOTE:_** THIS PROJECT IS NOT IN ANY WAY ASSOCIATED WITH OR RELATED TO THE SECURITAS DIRECT-VERISURE GROUP COMPANIES. The information here and online is for educational and resource purposes only and therefore the developers do not endorse or condone any inappropriate use of it, and take no legal responsibility for the functionality or security of your alarms and devices.

# Usage

```
usage: pysecuritas.py [-h] -u USERNAME -p PASSWORD -i INSTALLATION -c COUNTRY -l
                   LANGUAGE [-s SENSOR]
                   COMMAND

Securitas Direct API Client
https://github.com/Cebeerre/pysecuritas

positional arguments:
  COMMAND               ARM: arm all sensors (inside)
                        ARMDAY: arm in day mode (inside)
                        ARMNIGHT: arm in night mode (inside)
                        PERI: arm (only) the perimeter sensors
                        DARM: disarm everything (not the annex)
                        ARMANNEX: arm the secondary alarm
                        DARMANNEX: disarm the secondary alarm
                        EST: return the panel status
                        IMG: Take a picture (requires -s)
                        ACT_V2: get the activity log
                        SRV: SIM Number and INSTIBS
                        MYINSTALLATION: Sensor IDs and other info

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Username used in the web page/mobile app.
  -p PASSWORD, --password PASSWORD
                        Password used in the web page/mobile app.
  -i INSTALLATION, --installation INSTALLATION
                        Installation/Facility number (appears on the website).
  -c COUNTRY, --country COUNTRY
                        Your country (UPPERCASE): ES, IT, FR, GB, PT ...
  -l LANGUAGE, --language LANGUAGE
                        Your language (lowercase): es, it, fr, en, pt ...
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

You can use it as well as a python class so you can use it in your integrations:

```
>>> from pysecuritas import pysecuritas
>>> my_dict = { 'username': 'michael', 'password': 'mypassword', 'language':'en', 'country':'GB', 'installation':'12345' }
>>> client=pysecuritas(**my_dict)
>>> output=client.operate_alarm('EST')
>>> output
OrderedDict([('RES', 'OK'), ('STATUS', '0'), ('MSG', 'Your Alarm is deactivated'), ('NUMINST', '12345')])
```

I'm not a developer myself, so don't be too harsh on me !
