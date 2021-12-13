# NJU Health Checkin

> NJU daily health checkin, with fake locations and tgbot info, forked from [forewing/nju-health-checkin](https://github.com/forewing/nju-health-checkin).

## Requirements

```
python3 -m pip install -r requirements.txt
```

## Run with Crontab

This script provides features of sending checkin info using telegram-bot, and manually specifying fake location. You can feel free to use all of these two features or neither of them.

*Github action is not stable and will not be used in this fork any more.*

`crontab -e` and write:

```crontab
0 21 * * * /usr/bin/env bottoken=xxx tgid=yyy bash run.sh # run at 9pm everyday
```

Note:

* Complete your own `config.ini` file. If always use the location in the last checkin, just left `location` blank.
* If you do not use telegram bot, just write `/usr/bin/env bash run.sh` in crontab.

## Contributions

- [checkin.py](checkin.py) is written by [Maxwell Lyu](https://github.com/Maxwell-Lyu).

* Modified by [Antares](https://github.com/Antares0982).

