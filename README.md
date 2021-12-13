# NJU Health Checkin

## Usage

```
python3 -m pip install -r requirements.txt
NJU_USER=xxx NJU_PASS=xxx python3 checkin.py
```

## Crontab

```crontab
0 21 * * * NJU_USER=xxx NJU_PASS=xxx /usr/bin/python3 checkin.py
```

Github action is not stable and not used in this fork any more.

## Credits

- [checkin.py](checkin.py) is written by [Maxwell Lyu](https://github.com/Maxwell-Lyu).

