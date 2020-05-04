# VerisureAPIClient
Client to access Verisure / Securitas Direct Mobile API

API specification and known projects: [https://github.com/Cebeerre/VerisureEUAPI](https://github.com/Cebeerre/VerisureEUAPI)

**_NOTE:_** THIS PROJECT IS NOT IN ANY WAY ASSOCIATED WITH OR RELATED TO THE SECURITAS DIRECT-VERISURE GROUP COMPANIES. The information here and online is for educational and resource purposes only and therefore the developers do not endorse or condone any inappropriate use of it, and take no legal responsibility for the functionality or security of your alarms and devices.

# Usage

```
usage: verisure.py [-h] -u USERNAME -p PASSWORD -i INSTALLATION -c COUNTRY -l
                   LANGUAGE
                   COMMAND

Verisure/SecuritasDirect API Client
https://github.com/Cebeerre/VerisureAPIClient

positional arguments:
  COMMAND               Your request/command

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
```

Available commands are:

- `ARM`: arm the main alarm
- `ARMNIGHT`: arm in night mode
- `ARMDAY`: arm in day mode
- `PERI`: arm the perimeter sensors
- `DARM`: disarms everything
- `ACT`: output the activity log
- `EST`: get the current alarm status

Example:

`$ ./verisure.py -u michael -p mypassword -i 12345 -c GB -l en EST`

You'll get a json with the API output:

```
{
  "PET": {
    "RES": "OK",
    "STATUS": "0",
    "MSG": "Your Alarm is deactivated",
    "NUMINST": "12345",
    "BLOQ": {
      "@remotereqactive": "1",
      "#text": "Estamos mejorando nuestros servicios. Por favor intentelo de nuevo mas tarde. Gracias por confiar en Securitas Direct"
    }
  }
}
```

I'm not a developer myself, so don't be too harsh on me !
