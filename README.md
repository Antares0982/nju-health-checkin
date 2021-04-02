# NJU Health Checkin

## Usage

```
python -m pip install -r requirements.txt
NJU_USER=xxx NJU_PASS=xxx python checkin.py
```

## Github Actions

1. Set `NJU_USER`, `NJU_USER` in settings/secrets.

2. (Optional) Set `TELEGRAM_TOKEN`, `TELEGRAM_TO` secrets. [(appleboy/telegram-action)](https://github.com/appleboy/telegram-action#secrets)

- The job will be automatically executed at 9:00 am UTC+8 (may delay up to 1 hour due to GitHub's issue with cron actions).

- You can also trigger the job and set `NJU_USER`, `NJU_USER` manually by using `workflow_dispatch`.

## Credits

- [checkin.py](checkin.py) is written by [Maxwell Lyu](https://github.com/Maxwell-Lyu).