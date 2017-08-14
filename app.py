# pylint: skip-file
# FIXME: Reenable pylint when updated to 2.0
# Flask(__name__) breaks pylint 1.6 on python 3.6

from flask import Flask, request

from ews_to_fullcalendar import (get_cache, get_all_cached_fc_events,
	get_cached_fc_events_between, get_ical_events)
from fullcalendar_event import FullCalendarEvent

from exchangelib import EWSDateTime, EWSTimeZone

import json

app = Flask(__name__)

tz = EWSTimeZone.timezone('America/Chicago')

@app.route('/fullcalendar')
def fullcalendar():
	start = request.args.get('start', None)
	end = request.args.get('end', None)

	with get_cache() as cache:
		if start and end:
			events = get_cached_fc_events_between(cache, start, end)
		else:
			events = get_all_cached_fc_events(cache)

	return (
		json.dumps([event.to_dict() for event in events], indent='\t'),
		{
			'Content-Type': 'application/json',
			'Access-Control-Allow-Origin': '*'
		}
	)

@app.route('/ical.ics')
def ical():
	account = get_account()
	ics_events = get_ical_events(account.calendar.all())

	return (
		'\n'.join(ics_events),
		{
			'Content-Type': 'text/calendar',
			'Access-Control-Allow-Origin': '*'
		}
	)


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True, port=80)
