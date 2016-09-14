class Fae:
	"""An individual resident of Faerie"""
	import xml.etree.ElementTree as ET
	
	def __init__(self, fae_xml):
		# Initialize empty variables
		self.id = fae_xml.attrib['id']
		self.name = fae_xml.find('name').text
		self.spec = ''
		self.rank = ''
		self.desc = ''
		self.hold = ''
		self.title = []
		self.notes = []
		self.coords = []
		#Fill string variables
		if fae_xml.find('spec') is not None:
			self.spec = fae_xml.find('spec').text
		if fae_xml.find('rank') is not None:
			self.rank = fae_xml.find('rank').text
		if fae_xml.find('desc') is not None:
			self.desc = fae_xml.find('desc').text
		if fae_xml.find('hold') is not None:
			self.hold = fae_xml.find('hold').attrib['id']
		# Fill list variables
		for title in fae_xml.iter('title'):
			self.title.append(title.text)
		for note in fae_xml.iter('aspect'):
			self.notes.append(note.text)
	
	def get(self):
		print (self.name)
		print 'Name: ', self.name
		print 'Species: ', self.spec
		print 'Rank: ', self.rank
	
	def get_id(self):
		return self.id
	
	def set_coords(self, x, y):
		self.coords = [x, y]