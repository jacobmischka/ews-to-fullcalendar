class FullCalendarEvent(object):
	optional_props = [
		'id',
		'all_day',
		'end',
		'url',
		'location',
		'description'
	]

	dict_keys = {
		'all_day': 'allDay'
	}

	def __init__(self, title, start, **kwargs):
		for k in kwargs.keys():
			self.title = title
			self.start = start
			if k in self.optional_props:
				self.__setattr__(k, kwargs[k])

	@classmethod
	def from_ews_event(cls, event):
		description = None
		if event.text_body and event.text_body.strip():
			description = event.text_body.strip()


		return cls(
			id=event.item_id,
			title=event.subject,
			start=event.start.isoformat(),
			end=event.end.isoformat(),
			all_day=event.is_all_day,
			location=event.location,
			description=description
		)

	def to_dict(self):
		d = {
			'title': self.title,
			'start': self.start
		}
		for k in self.optional_props:
			try:
				v = self.__getattribute__(k)
				dict_key = self.dict_keys[k] if k in self.dict_keys.keys() else k
				d[dict_key] = v
			except AttributeError:
				pass

		return d
