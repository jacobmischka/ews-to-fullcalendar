#!/usr/bin/env python3

from exchangelib import DELEGATE, ServiceAccount, Account, Configuration, EWSDateTime, EWSTimeZone
from dotenv import load_dotenv, find_dotenv
import os

def get_account():
	load_dotenv(find_dotenv())

	USERNAME = os.environ.get('EWS_USERNAME')
	PASSWORD = os.environ.get('EWS_PASSWORD')
	EMAIL = os.environ.get('EWS_EMAIL')
	SERVER = os.environ.get('EWS_SERVER')

	credentials = ServiceAccount(username=USERNAME, password=PASSWORD)
	config = Configuration(server=SERVER, credentials=credentials)
	return Account(primary_smtp_address=EMAIL, config=config,
		autodiscover=False, access_type=DELEGATE)

def get_events(account):
	# FIXME
	tz = EWSTimeZone.timezone('America/Chicago')
	events = account.calendar.filter(start__range=(tz.localize(EWSDateTime(2017, 8, 1)), tz.localize(EWSDateTime(2017, 9, 1))))
	return list(events)

def get_ical_event(event):
	# Guess exchange does everything for us, that's handy
	return str(event.mime_content, 'utf-8')

def get_fullcalendar_event(event):
	# TODO

def main():
	account = get_account()
	events = get_events(account)
	print(get_ical_event(events[0]))

if __name__ == '__main__':
	main()
