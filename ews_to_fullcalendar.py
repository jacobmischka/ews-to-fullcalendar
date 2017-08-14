#!/usr/bin/env python3

from fullcalendar_event import FullCalendarEvent

from exchangelib import (DELEGATE, ServiceAccount, Account, Configuration,
	CalendarItem)
from dotenv import load_dotenv, find_dotenv
from appdirs import user_cache_dir

from argparse import ArgumentParser
import os, json, sys, sqlite3, pickle

APP_NAME = 'ews-to-fullcalendar'
AUTHOR_NAME = 'jacobmischka'

CACHE_DIR = user_cache_dir(APP_NAME, AUTHOR_NAME)
CACHE_FILENAME = 'ews-event-cache.db'

try:
	load_dotenv(find_dotenv())
except Exception:
	pass

USERNAME = os.environ.get('EWS_USERNAME')
PASSWORD = os.environ.get('EWS_PASSWORD')
EMAIL = os.environ.get('EWS_EMAIL')
SERVER = os.environ.get('EWS_SERVER')
EVENT_CACHE_PATH = os.environ.get('EWS_CACHE', os.path.join(CACHE_DIR, CACHE_FILENAME))

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

def save_events_to_cache(account, cache):
	for fc_event in get_all_fc_events(account):
		upsert_event(cache, fc_event)

def get_all_cached_fc_events(cache):
	return [pickle.loads(event[0]) for event in cache.execute('SELECT event FROM events')]

def get_cached_fc_events_between(cache, start, end):
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
		if type(event) is CalendarItem:
			try:
				fc_events.append(FullCalendarEvent.from_ews_event(event))
			except Exception as e:
				print('Failed to convert EWS event to FullCalendar event: {}'.format(e), file=sys.stderr)
		else:
			print('Event is not EWS CalendarItem, skipping', file=sys.stderr)

	return fc_events

def get_ical_events(qs):
	ical_events = []
	for event in qs:
		if type(event) is CalendarItem:
			try:
				ical_events.append(strip_windows_newlines(event.mime_content.decode('utf-8')))
			except Exception as e:
				print('Failed to get MIME content from event: {}'.format(e), file=sys.stderr)
		else:
			print('Event is not EWS CalendarItem, skipping', file=sys.stderr)

	return ical_events

def strip_windows_newlines(s):
	return s.replace('\r', '')

def write_events(events, outpath=None):
	if outpath:
		with open(outpath, 'w') as outfile:
			json.dump(events, outfile, indent='\t')
	else:
		json.dump(events, sys.stdout, indent='\t')

def main():
	parser = ArgumentParser(description='Outputs all calendar events as FullCalendar events')
	parser.add_argument('-o', help='Output file path (default stdout)', dest='outpath', required=False, default=None)
	args = parser.parse_args()

	account = get_account()
	with get_cache() as cache:
		save_events_to_cache(account, cache)
		fc_events = get_all_cached_fc_events(cache)

	write_events([event.to_dict() for event in fc_events], args.outpath)


if __name__ == '__main__':
	main()
