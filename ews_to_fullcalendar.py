#!/usr/bin/env python3

from exchangelib import (DELEGATE, ServiceAccount, Account, Configuration,
	EWSDateTime, EWSTimeZone, Message, ExtendedProperty)
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

def get_request(account):
	return account.inbox.filter(subject='')[0]

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
	pass

def main():
	account = get_account()
	Message.register('content_class', PidNameContentClass)
	Message.register('provider_guid', PidLidSharingProviderGuid)
	r = get_request(account)
	print(r.content_class)
	print(r.provider_guid)


class PidNameContentClass(ExtendedProperty):
	property_set_id = '00020386-0000-0000-c000-000000000046'
	property_name = 'Content-class'
	property_type = 'String'

class PidLidSharingProviderGuid(ExtendedProperty):
	property_set_id = '00062040-0000-0000-C000-000000000046'
	property_name = '0x8A01'
	property_type = 'Binary'

# class PidLidSharingProviderName(ExtendedProperty):
# 	property_set_id = ''
# 	property_name = '0x00008A02'

if __name__ == '__main__':
	main()
