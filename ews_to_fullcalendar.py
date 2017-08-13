#!/usr/bin/env python3

from fullcalendar_event import FullCalendarEvent

from exchangelib import (DELEGATE, ServiceAccount, Account, Configuration,
	CalendarItem)
from dotenv import load_dotenv, find_dotenv

from argparse import ArgumentParser
import os, json, sys

def get_account():
	try:
		load_dotenv(find_dotenv())
	except Exception:
		pass

	USERNAME = os.environ.get('EWS_USERNAME')
	PASSWORD = os.environ.get('EWS_PASSWORD')
	EMAIL = os.environ.get('EWS_EMAIL')
	SERVER = os.environ.get('EWS_SERVER')

	credentials = ServiceAccount(username=USERNAME, password=PASSWORD)
	config = Configuration(server=SERVER, credentials=credentials)
	return Account(primary_smtp_address=EMAIL, config=config,
		autodiscover=False, access_type=DELEGATE)

def get_fc_events(account):
	fc_events = []
	for event in account.calendar.all():
		if type(event) is CalendarItem:
			try:
				fc_events.append(FullCalendarEvent.from_ews_event(event))
			except Exception as e:
				print('Failed to convert EWS event to FullCalendar event: {}'.format(e), sys.stderr)

	return fc_events

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
	fc_events = get_fc_events(account)

	write_events([event.to_dict() for event in fc_events], args.outpath)


if __name__ == '__main__':
	main()
