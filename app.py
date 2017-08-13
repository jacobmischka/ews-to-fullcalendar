# pylint: skip-file
# FIXME: Reenable pylint when updated to 2.0
# Flask(__name__) breaks pylint 1.6 on python 3.6

from flask import Flask, request

from ews_to_fullcalendar import get_account, get_fc_events_between, get_all_fc_events
from fullcalendar_event import FullCalendarEvent

from exchangelib import EWSDateTime, EWSTimeZone

import json

app = Flask(__name__)

tz = EWSTimeZone.timezone('America/Chicago')

@app.route('/fullcalendar')
def index():
	start = request.args.get('start', None)
	end = request.args.get('end', None)

	account = get_account()

	if start and end:
		ews_start = tz.localize(EWSDateTime.strptime(start, '%Y-%m-%d'))
		ews_end = tz.localize(EWSDateTime.strptime(end, '%Y-%m-%d'))

		events = get_fc_events_between(account, ews_start, ews_end)
	else:
		events = get_all_fc_events(account)

	return (
		json.dumps([event.to_dict() for event in events], indent='\t'),
		{
			'Content-Type': 'application/json'
		}
	)

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True, port=80)
