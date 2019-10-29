# VerisureAPIClient
Client to access Verisure / Securitas Direct Mobile API

Tested with a Spanish account, might work in other countries.

Right now is pretty simple. TODO:
* Error Control
* Clean-up & Documentation

I managed to create a webservice with this and Flask and integrate everything together with IFTT using WebHooks.

THIS PROJECT IS NOT IN ANY WAY ASSOCIATED WITH OR RELATED TO THE SECURITAS DIRECT-VERISURE GROUP COMPANIES.

# Usage

You can either call it as a module:

```
$ python3
Python 3.7.3 (v3.7.3:ef4ec6ed12, Mar 25 2019, 16:52:21) 
[Clang 6.0 (clang-600.0.57)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from verisure import VerisureAPIClient
>>> client = VerisureAPIClient('username','password','0000000','SDVFAST','ES','es',1)
>>> client.get_panel_status()
{'result': 'OK', 'status': '0', 'message': 'Tu Alarma está desconectada'}
```

* client.get_panel_status()
* client.arm_outside()
* client.arm_total_inside()
* client.arm_nigh()
* client.disarm_all()
* client.log()

or from the command line:

```
$ ./verisure.py username password 0000000 SDVFAST ES es 1 EST
{'result': 'OK', 'status': '0', 'message': 'Tu Alarma está desconectada'}
```

Parameters (strict order)
* Username (the same than used in the Mobile App/Web)
* Password (the same than used in the Mobile App/Web)
* Installation/Facility Number
* Alarm Model (nowadays, almost everybody uses the SDVFAST)
* Country (uppercase)
* Language (lowercase)
* ACTION:
  * EST -> STATUS
  * PERI -> PERIMETER/OUTDOOR
  * ARM -> ARMED/INDOOR
  * ARMNIGHT -> ARMED/NIGHT MODE
  * DARM -> SWITCH OFF EVERYTHING
  * ACT -> LOG ACTIVITY

I'm not a developer myself, so don't be too harsh on me !
