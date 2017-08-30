#!/usr/bin/env python3

from fullcalendar_event import FullCalendarEvent

from exchangelib import (DELEGATE, ServiceAccount, Account, Configuration,
	CalendarItem)
from dotenv import load_dotenv, find_dotenv
from appdirs import user_cache_dir

from argparse import ArgumentParser
import os, json, sys, sqlite3, pickle, tzlocal

PRODID = '-//Jacob Mischka//EWS to FullCalendar//EN'

APP_NAME = 'ews-to-fullcalendar'
AUTHOR_NAME = 'jacobmischka'

CACHE_DIR = user_cache_dir(APP_NAME, AUTHOR_NAME)
CACHE_FILENAME = 'ews-event-cache.db'
ICAL_CACHE_FILENAME = 'ical.ics'

try:
	load_dotenv(find_dotenv())
except Exception:
	pass

USERNAME = os.environ.get('EWS_USERNAME')
PASSWORD = os.environ.get('EWS_PASSWORD')
EMAIL = os.environ.get('EWS_EMAIL')
SERVER = os.environ.get('EWS_SERVER')

CALNAME = os.environ.get('EWS_CALNAME', 'Calendar')
CALDESC = os.environ.get('EWS_CALDESC', '')
TIMEZONE = os.environ.get('EWS_TIMEZONE', tzlocal.get_localzone().zone)

EVENT_CACHE_PATH = os.environ.get('EWS_CACHE', os.path.join(CACHE_DIR, CACHE_FILENAME))
ICAL_CACHE_PATH = os.environ.get('EWS_ICAL_CACHE', os.path.join(CACHE_DIR, ICAL_CACHE_FILENAME))

def get_account():
	credentials = ServiceAccount(username=USERNAME, password=PASSWORD)
	config = Configuration(server=SERVER, credentials=credentials)
	return Account(primary_smtp_address=EMAIL, config=config,
		autodiscover=False, access_type=DELEGATE)

def get_cache():
	os.makedirs(os.path.dirname(EVENT_CACHE_PATH), exist_ok=True)
	conn = sqlite3.connect(EVENT_CACHE_PATH)
	conn.execute('''
		CREATE TABLE IF NOT EXISTS events (
			id text PRIMARY KEY,
			title text,
			start text,
			end text,
			event blob
		)
	''')
	conn.commit()
	return conn

def upsert_event(cache, event):
	cache.execute('''
		INSERT OR REPLACE INTO events(id, title, start, end, event)
		VALUES (?, ?, ?, ?, ?)
	''', (event.id, event.title, event.start, event.end, pickle.dumps(event)))

def sync_events(account):
	events = [event for event in account.calendar.all() if type(event) is CalendarItem]

	with get_cache() as cache:
		save_events_to_cache(events, cache)

	save_ical(events)

def save_events_to_cache(events, cache):
	for fc_event in get_fc_events(events):
		upsert_event(cache, fc_event)

	cache.commit()

def save_ical(events):
	ics_events = [clean_mime_content(event.mime_content) for event in events]

	ical = '''\
BEGIN:VCALENDAR
VERSION:2.0
PRODID:{}
X-WR-CALNAME:{}
X-WR-CALDESC:{}
X-WR-TIMEZONE:{}
{}
END:VCALENDAR'''.format(
		PRODID,
		CALNAME,
		CALDESC,
		TIMEZONE,
		'\n'.join(ics_events)
	)

	with open(ICAL_CACHE_PATH, 'w') as ical_file:
		ical_file.write(ical)

def get_all_cached_fc_events():
	with get_cache() as cache:
		return [pickle.loads(event[0]) for event in cache.execute('SELECT event FROM events')]

def get_cached_fc_events_between(start, end):
	with get_cache() as cache:
		return [pickle.loads(event[0]) for event in cache.execute(
			'SELECT event FROM events WHERE start <= ? AND end >= ?', (end, start))]

def get_all_fc_events(account):
	return get_fc_events(account.calendar.all())

def get_fc_events_between(account, start, end):
	return get_fc_events(account.calendar.view(
		start=start,
		end=end
	))

def get_fc_events(events):
	fc_events = []
	for event in events:
		fc_event = get_fc_event(event)
		if fc_event:
			fc_events.append(fc_event)

	return fc_events

def get_fc_event(event):
	if type(event) is CalendarItem:
		try:
			return FullCalendarEvent.from_ews_event(event)
		except Exception as e:
			print('Failed to convert EWS event to FullCalendar event: {}'.format(e), file=sys.stderr)
	else:
		print('Event is not EWS CalendarItem, skipping', file=sys.stderr)

def get_saved_ical():
	with open(ICAL_CACHE_PATH, 'r') as ical_file:
		return ical_file.read()

def clean_mime_content(mime):
	content = mime.decode('utf-8').replace('\r', '')
	BEGIN = 'BEGIN:VEVENT'
	END = 'END:VEVENT'

	start = content.find(BEGIN)
	end = content.find(END) + len(END)

	return content[start:end].strip()

def write_events(events, outpath=None):
	if outpath:
		with open(outpath, 'w') as outfile:
			json.dump(events, outfile, indent='\t')
	else:
		json.dump(events, sys.stdout, indent='\t')

def main():
	parser = ArgumentParser(description='Outputs all calendar events as FullCalendar events')
	parser.add_argument('-o', help='Output file path (default stdout)', dest='outpath', required=False, default=None)
	parser.add_argument('-i', '--ical', '--ics', action='store_true', help='Get .ics instead', dest='ics')
	parser.add_argument('-s', '--sync', action='store_true', help='Save calendar events to local cache', dest='sync')
	parser.add_argument('-q', '--quiet', action='store_true', help="Don't output events (to be used with --sync)", dest='quiet')
	args = parser.parse_args()

	if args.sync:
		sync_events(get_account())

	if not args.quiet:
		if args.ics:
			if args.outpath:
				with open(args.outpath, 'w') as outfile:
					outfile.write(get_saved_ical())
			else:
				sys.stdout.write(get_saved_ical())
		else:
			fc_events = get_all_cached_fc_events()
			write_events([event.to_dict() for event in fc_events], args.outpath)


if __name__ == '__main__':
	main()
