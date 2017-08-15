# ews-to-fullcalendar

Small wrapper library and associated CLI and web interface to convert Exchange Web Services calendar events to a [FullCalendar][fullcalendar] event JSON or iCalendar feed.

## Configuration

Uses the following env vars, which can be loaded from a `.env` file:

- `EWS_USERNAME`
- `EWS_PASSWORD`
- `EWS_EMAIL`
- `EWS_SERVER`
- `EWS_CALNAME`
- `EWS_CALDESC`
- `EWS_TIMEZONE`
- `EWS_ALLOWED_ORIGIN`

## Usage

### CLI

```
$ ./ews_to_fullcalendar.py -h
usage: ews_to_fullcalendar.py [-h] [-o OUTPATH] [-i] [-s] [-q]

Outputs all calendar events as FullCalendar events

optional arguments:
  -h, --help         show this help message and exit
  -o OUTPATH         Output file path (default stdout)
  -i, --ical, --ics  Get .ics instead
  -s, --sync         Save calendar events to local cache
  -q, --quiet        Don't output events (to be used with --sync)
```

### Web

Intended to be used for [ics-merger][ics-merger] but should work for any FullCalendar or iCalendar consumer.

Serves events from local cache, which is updated every 3 hours by default (see `crontabs/root`).

### Library

```python
from ews_to_fullcalendar import get_account, sync_events, get_all_cached_fc_events

account = get_account()
sync_events(account)
events = get_all_cached_fc_events()
```

[fullcalendar]: https://fullcalendar.io/
[ics-merger]: https://github.com/jacobmischka/ics-merger
