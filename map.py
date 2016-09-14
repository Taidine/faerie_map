# Display the main map of Faerie

import pygame._view, pygame, sys, os, random, math
from pygame.locals import *
import xml.etree.ElementTree as ET
import hold

### Models ###

def make_hold_objects(court):
	import hold
	hold_dict={}
	for child in court.findall('hold'):
		hold_dict[child.get('id')]=hold.Hold(child)
	return hold_dict
	
def make_fae_objects(court):
	import fae
	fae_dict={}
	for child in court.findall('fae'):
		fae_dict[child.get('id')]=fae.Fae(child)
	return fae_dict

def parse_court(courtName):
	filepath = os.path.join('Faerie/data/'+courtName+'.xml')
	court = ET.parse(filepath)
	court = court.getroot()
	return court

### Views ###
	
def draw_map(screen):
	map_surface = pygame.Surface(MAPRECT)
	map_surface.fill(pygame.Color(255,255,255))
	screen.blit(map_surface, (0,0))
	for holdId in PLACED:
	# Pass one: Draw unbold lines
		coords = PLACED[holdId]
		hold_object = HOLDS[holdId]
		start = (coords[0], coords[1])
		for dest in hold_object.journey:
			if dest in PLACED:
				endcoords = PLACED[dest]
				end = (endcoords[0], endcoords[1])
				if (coords[2] + endcoords[2] != 3):
					pygame.draw.aaline(screen, COLOR, start, end)
	for holdId in PLACED:
	# Pass two: Draw dots
		coords = PLACED[holdId]
		hold_object = HOLDS[holdId]
		start = (coords[0], coords[1])
		holdsprite = HoldSprite(hold_object)
		holdsprite.draw(coords,screen)
	for holdId in PLACED:
	# Pass three: Draw bold lines
		coords = PLACED[holdId]
		hold_object = HOLDS[holdId]
		start = (coords[0], coords[1])
		for dest in hold_object.journey:
			if dest in PLACED:
				endcoords = PLACED[dest]
				end = (endcoords[0], endcoords[1])
				if (coords[2] + endcoords[2] == 3):
					pygame.draw.aaline(screen, (0,0,0), start, end, 3)
	pygame.display.update(pygame.Rect(0,0,MAPRECT[0],MAPRECT[1]))

def draw_modebar(screen):
	bar_surface = pygame.Surface(MODERECT)
	bar_surface.fill(pygame.Color(255,255,255))
	bar_font = pygame.font.Font(None, 18)
	mapButton = bar_font.render(' Map ', 1, (0,0,0))
	mapButtonSize = bar_font.size(' Map ')
	resButton = bar_font.render(' Residents ', 1, (0,0,0))
	resButtonSize = bar_font.size(' Residents ')
	bar_surface.blit(mapButton, (5,4))
	bar_surface.blit(resButton, (5+mapButtonSize[0]+5, 4))
	screen.blit(bar_surface, (0,MAPRECT[1]+5))
	pygame.display.update(pygame.Rect(0,MAPRECT[1]+5, MODERECT[0],MODERECT[1]))
	return (mapButtonSize[0], mapButtonSize[1], resButtonSize[0], resButtonSize[1])

def draw_database(screen,fontsize=15):
	database_surface = pygame.Surface(MAPRECT)
	database_surface.fill(pygame.Color(255,255,255))
	for id in PLACED_NAMES:
		fae_object = FAE[id]
		coords = PLACED_NAMES[id]
		faesprite = FaeSprite(fae_object)
		faesprite.print_name(fontsize, coords, database_surface)
	screen.blit(database_surface, (0,0))
	pygame.display.update(pygame.Rect(0,0,MAPRECT[0],MAPRECT[1]))
	
### Controllers ###
	
def place_all_holds():
	global PLACED
	PLACED = {}
	journies = 0
	prevHold = ''
	firstHold = ''
	while len(PLACED) == 0:
		try:
			#Put the hold with the greatest number of journies in the middle
			for holdId in HOLDS:
				hold_object = HOLDS[holdId]
				if journies < len(hold_object.journey):
					journies = len(hold_object.journey)
					firstHold = hold_object
			place_hold(firstHold, prevHold)
			for holdId in HOLDS: 
				if holdId not in PLACED:
					# TODO: Place holds that are not connected.
					print holdId
		except RuntimeError as e:
			pass
	
def place_hold(hold, prevHold):
	global PLACED
	if prevHold=='':
		x = MAPRECT[0]/2
		y = MAPRECT[1]/2
		center = (x,y)
	else:
		r = GRID
		xoffset = random.randint(-r,r)
		yoffset = int(math.sqrt(r**2 - xoffset**2))
		yoffset = random.choice((-yoffset,yoffset))
		x = prevHold.x + xoffset
		y = prevHold.y + yoffset
		center=(prevHold.x,prevHold.y)
	xy = collision_check(x, y, center)
	hold.x = xy[0]
	hold.y = xy[1]
	PLACED[hold.id] = (xy[0], xy[1], 0)
	for dest in hold.journey:
		if dest in PLACED:
			pass
		elif dest in HOLDS:
			dest_object = HOLDS[dest]
			PLACED[dest_object.id] = (xy[0], xy[1], 0)
			place_hold(dest_object, hold)
		else:
			pass

def collision_check(x,y,center):
	xy=(x,y)
	# First make sure you aren't running into any walls
	if x > (MAPRECT[0] - PENUMBRA) or x < PENUMBRA or y > (MAPRECT[1] - PENUMBRA) or y < PENUMBRA:
		r = GRID
		xoffset = random.randint(-r,r)
		yoffset = int(math.sqrt(r**2 - xoffset**2))
		yoffset = random.choice((-yoffset,yoffset))
		x = center[0] + xoffset
		y = center[1] + yoffset
		xy = collision_check(x,y,center)
	# Then make sure you are not occupying anyone else's space
	for dest in PLACED:
		oldx = PLACED[dest][0]
		oldy = PLACED[dest][1]
		if ((x-oldx)**2+(y-oldy)**2) <= (PENUMBRA**2):
			r = GRID
			xoffset = random.randint(-r,r)
			yoffset = int(math.sqrt(r**2 - xoffset**2))
			yoffset = random.choice((-yoffset,yoffset))
			x = center[0] + xoffset
			y = center[1] + yoffset
			xy = collision_check(x,y,center)
	x = xy[0]
	y = xy[1]
	return (x,y)

def bug_catch_hack():
	global PLACED
	bug = 0
	for dest1 in PLACED:
		for dest2 in PLACED:
			if PLACED[dest1][0] == PLACED[dest2][0] and PLACED[dest1][1] == PLACED[dest2][1] and not (dest1 == dest2):
				bug = 1
	if len(PLACED) != len(HOLDS):
		bug = 1
	if bug == 1:
		PLACED = {}
		place_all_holds()
		bug_catch_hack()
	
def _clear_placed_dict():
	# Clears PLACED of flags to bold holds/journies
	global PLACED
	for dest in PLACED:
		PLACED[dest] = (PLACED[dest][0], PLACED[dest][1], 0)

def place_fae(fontsize, margin=50, linespacing=10, colspacing=10):
	width = math.floor((MAPRECT[0]-2*margin-2*colspacing)/3)
	# coords = (top, left, bottom, right)
	coords = (margin+linespacing, margin, margin+(2*linespacing)+fontsize, margin+width)
	for fae in FAE:
		fae_object = FAE[fae]
		PLACED_NAMES[fae_object.id] = coords
		if coords[2] < (MAPRECT[1]-margin):
			coords = (coords[2]+linespacing, coords[1], coords[2]+fontsize+2*linespacing, coords[3])
		else:
			coords = (margin+linespacing, coords[1]+width+colspacing, margin+2*linespacing+fontsize, coords[3]+width+colspacing)
	

		
def input(events, buttons, screen):
	global PLACED
	global MODE
	for event in events:
		if event.type == pygame.QUIT:
			pygame.quit()
			return False
			break
		elif event.type == MOUSEBUTTONDOWN:
			pos = pygame.mouse.get_pos()
			clickx = pos[0]
			clicky = pos[1]
			if clickx < (buttons[0]+10) and clicky > MAPRECT[1]:
				draw_map(screen)
				MODE = 'map'
				return True
			elif clickx > (buttons[0]+10) and clickx < (buttons[2]+40) and clicky > MAPRECT[1]:
				draw_database(screen)
				MODE = 'residents'
				return True
			elif clickx > MAPRECT[0]+5 and clicky > 0:
				for name in PLACED_NAMES_INFO:
					nametop = PLACED_NAMES_INFO[name][0]
					nameleft = PLACED_NAMES_INFO[name][1]
					namebottom = PLACED_NAMES_INFO[name][2]
					nameright = PLACED_NAMES_INFO[name][3]
					if clickx >= nameleft and clickx <= nameright and clicky >= nametop and clicky <=namebottom:
						# Display information
						fae = FAE[name]
						faesprite = FaeSprite(fae)
						faesprite.display(screen)
				return True
			elif MODE == 'map':
				for dest in PLACED:
					holdx = PLACED[dest][0]
					holdy = PLACED[dest][1]
					if abs(holdx-clickx) < (RADIUS+2) and abs(holdy-clicky) < (RADIUS+2):
						hold = HOLDS[dest]
						# Display information
						holdsprite = HoldSprite(hold)
						holdsprite.display(screen)
						# Bold and redraw map
						PLACED[dest] = (PLACED[dest][0], PLACED[dest][1], 2)
						for adj in hold.journey:
							if adj in PLACED:
								PLACED[adj] = (PLACED[adj][0], PLACED[adj][1], 1)
						draw_map(screen)
						_clear_placed_dict()
				return True
			elif MODE == 'residents':
				for name in PLACED_NAMES:
					nametop = PLACED_NAMES[name][0]
					nameleft = PLACED_NAMES[name][1]
					namebottom = PLACED_NAMES[name][2]
					nameright = PLACED_NAMES[name][3]
					if clickx >= nameleft and clickx <= nameright and clicky >= nametop and clicky <=namebottom:
						# Display information
						name = FAE[name]
						faesprite = FaeSprite(name)
						faesprite.display(screen)
				return True
		elif event.type == KEYDOWN:
			place_all_holds()
			bug_catch_hack()
			draw_map(screen)
		else:
			pass
	return True
			
### Classes ###
			
class HoldSprite(pygame.sprite.Sprite):
	
	def __init__(self, hold):
		pygame.sprite.Sprite.__init__(self)
		self.hold = hold
		self.labelfontsize = 13
		self.labelFont = pygame.font.Font(None, self.labelfontsize)
		self.fontsize = 15
		self.font = pygame.font.Font(None, self.fontsize)
		
	def draw(self, coords, screen):
		if coords[2] == 0:
			pygame.draw.circle(screen, COLOR, (coords[0],coords[1]), RADIUS)
		else:
			pygame.draw.circle(screen, (0,0,0), (coords[0],coords[1]), RADIUS+2)
		name = self.hold.name
		word_list = name.split(' ')
		name_list = []
		i=0
		while i < len(word_list):
			if i+1 == len(word_list):
				name_list.append(word_list[i])
			else:
				name_list.append(word_list[i]+' '+word_list[i+1])
			i=i+2
		n=(RADIUS+2)
		for words in name_list:
			text = self.labelFont.render(words, 1, (0,0,0))
			textsize = self.labelFont.size(words)
			textcoords = ((coords[0]-(textsize[0]/2)), (coords[1]+n))
			n = n+self.labelfontsize
			screen.blit(text, textcoords)
		
	def display(self, screen):
		global PLACED_NAMES_INFO
		PLACED_NAMES_INFO = {}
		info_surface = pygame.Surface((INFORECT[0], INFORECT[1]))
		info_surface.fill((255,255,255))
		info_list = {}
		info_list['ruler'] = self.hold.ruler.split(' ')
		info_list['name'] = self.hold.name.split(' ')
		info_list['desc'] = self.hold.desc.split(' ')
		info_list['res'] = self.hold.res
		info_list['notes'] = self.hold.notes
		vline = 100
		margin = 20
		print_name = self._blit_text(info_list['name'], vline, margin, info_surface, 'Hold: ')
		print_ruler = self._blit_text(info_list['ruler'], print_name[1], margin, print_name[0], 'Ruler: ', 'ruler')
		print_desc = self._blit_text(info_list['desc'], print_ruler[1]+self.fontsize, margin, print_ruler[0], '')
		print_res = self._blit_text(('Other', 'residents:'), print_desc[1]+self.fontsize, margin, print_desc[0], '')
		for res in info_list['res']:
			word_list = res.split(' ')
			print_res = self._blit_text(word_list, print_res[1], margin, print_res[0], ' ', 'res')
		print_note = self._blit_text(('Notes:', ''), print_res[1]+self.fontsize, margin, print_res[0], '')
		for note in info_list['notes']:
			word_list = note.split(' ')
			print_note = self._blit_text(word_list, print_note[1], margin, print_note[0], ' ')
		screen.blit(print_desc[0], (MAPRECT[0]+5,0))
		pygame.display.update(pygame.Rect(MAPRECT[0]+5,0,INFORECT[0],INFORECT[1]))
		
	def _blit_text(self, word_list, vline, margin, surface, line=' ', record=False):
		global PLACED_NAMES_INFO
		word = 0
		while word < len(word_list):
			maxwidth = surface.get_width() - (4*margin + self.font.size(word_list[word]+'  ')[0])
			while self.font.size(line)[0] < maxwidth and word < len(word_list):
				line = line+word_list[word]+' '
				word = word+1
			print_line = self.font.render(line, 1, (0,0,0))
			if record == 'ruler' and self.hold.ruler_id is not '':
				PLACED_NAMES_INFO[self.hold.ruler_id] = (vline, MAPRECT[0]+5, vline+self.fontsize, MAPRECT[0]+INFORECT[0])
			elif record == 'res':
				word_list[0] = word_list[0].lower()
				id = ''
				for word in word_list:
					id = id+word
				PLACED_NAMES_INFO[id] = (vline, MAPRECT[0]+5, vline+self.fontsize, MAPRECT[0]+INFORECT[0])
			line = ''
			textcoords = (margin, (vline))
			vline = vline+self.fontsize
			surface.blit(print_line, textcoords)
		return surface, vline
		
		

class FaeSprite(pygame.sprite.Sprite):
				
	def __init__(self, fae):
		pygame.sprite.Sprite.__init__(self)
		self.fae = fae
		if fae.hold is '' or fae.hold not in HOLDS:
			self.hold = ''
		else:
			self.hold = HOLDS[fae.hold]
		self.fontsize = 15
		self.font = pygame.font.Font(None, self.fontsize)
		
	def print_name(self, fontsize, coords, surface):
		name = self.fae.name
		self.labelFont = pygame.font.Font(None, fontsize)
		name = self.labelFont.render(name, 1, (0,0,0))
		surface.blit(name, (coords[1], coords[0]))
	
	def display(self, screen):
		info_surface = pygame.Surface((INFORECT[0], INFORECT[1]))
		info_surface.fill((255,255,255))
		info_list = {}
		info_list['name'] = self.fae.name.split(' ')
		info_list['rank'] = self.fae.rank.split(' ')
		info_list['spec'] = self.fae.spec.split(' ')
		if self.hold is '':
			info_list['hold'] = ('none', '')
		else:
			info_list['hold'] = self.hold.name.split(' ')
		info_list['desc'] = self.fae.desc.split(' ')
		info_list['notes'] = self.fae.notes
		vline = 100
		margin = 20
		print_name = self._blit_text(info_list['name'], vline, margin, info_surface, 'Name: ')
		print_rank = self._blit_text(info_list['rank'], print_name[1], margin, print_name[0], 'Rank: ')
		print_spec = self._blit_text(info_list['spec'], print_rank[1], margin, print_rank[0], 'Species: ')
		print_hold = self._blit_text(info_list['hold'], print_spec[1], margin, print_spec[0], 'Hold: ')
		print_desc = self._blit_text(info_list['desc'], print_hold[1]+self.fontsize, margin, print_hold[0], '')
		print_note = self._blit_text(('Notes:', ''), print_desc[1]+self.fontsize, margin, print_desc[0], '')
		for note in info_list['notes']:
			word_list = note.split(' ')
			print_note = self._blit_text(word_list, print_note[1], margin, print_note[0], ' ')
		screen.blit(print_desc[0], (MAPRECT[0]+5,0))
		pygame.display.update(pygame.Rect(MAPRECT[0]+5,0,INFORECT[0],INFORECT[1]))
		
	def _blit_text(self, word_list, vline, margin, surface, line=' '):
			word = 0
			while word < len(word_list):
				maxwidth = surface.get_width() - (4*margin + self.font.size(word_list[word]+'  ')[0])
				while self.font.size(line)[0] < maxwidth and word < len(word_list):
					line = line+word_list[word]+' '
					word = word+1
				print_line = self.font.render(line, 1, (0,0,0))
				line = ''
				textcoords = (margin, (vline))
				vline = vline+self.fontsize
				surface.blit(print_line, textcoords)
			return surface, vline
			
## Main ##

SCREENRECT = (1100, 800)
MODERECT = (SCREENRECT[0], 20)
INFORECT = (240,SCREENRECT[1]-(MODERECT[1]+10))
MAPRECT = (SCREENRECT[0]-(INFORECT[0] + 5), SCREENRECT[1]-(MODERECT[1]+10))
GRID = 200
PENUMBRA = 50
RADIUS = 6
COLOR = (200,170,200)
COURTNAME = "Spider"
COURT = parse_court(COURTNAME)
HOLDS = make_hold_objects(COURT)
FAE = make_fae_objects(COURT)
PLACED = {}
PLACED_NAMES = {}
PLACED_NAMES_INFO = {}
MODE = 'map'

pygame.init()
running = True
window = pygame.display.set_mode(SCREENRECT)
pygame.display.set_caption(COURTNAME + ' Court')
screen = pygame.display.get_surface()
place_all_holds()
bug_catch_hack()
place_fae(15)
draw_map(screen)
buttons = draw_modebar(screen)
while running == True:
	pygame.time.Clock().tick(30)
	running = input(pygame.event.get(), buttons, screen)
