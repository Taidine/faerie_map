class Hold:
	"""An individual realm in Faerie"""
	import xml.etree.ElementTree as ET
	
	def __init__(self, hold_xml):
		# Initialize empty variables
		self.id = hold_xml.attrib['id']
		self.name = hold_xml.find('name').text
		self.ruler = 'unknown'
		self.ruler_id = ''
		self.desc = ''
		self.res = []
		self.journey = []
		self.exit = []
		self.notes = []
		self.coords = []
		#Fill string variables
		if hold_xml.find('ruler') is not None:
			self.ruler = hold_xml.find('ruler').text
			self.ruler_id = hold_xml.find('ruler').attrib['id']
		if hold_xml.find('desc') is not None:
			self.desc = hold_xml.find('desc').text
		# Fill list variables
		for resident in hold_xml.iter('res'):
			self.res.append(resident.text)
		for journey in hold_xml.iter('journey'):
			if journey.attrib['type'] == 'in':
				self.journey.append(journey.attrib['dest'])
			else:
				self.exit.append(journey.text)
		for note in hold_xml.iter('aspect'):
			self.notes.append(note.text)
	
	def get(self):
		print (self.name)
		print 'Ruled by', self.ruler
		print 'Notes: ', self.desc
		print 'Journies', self.journey
	
	def get_id(self):
		return self.id
	
	def set_coords(self, x, y):
		self.coords = [x, y]
	
		