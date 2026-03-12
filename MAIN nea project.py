################ NEA project: OBSTACLE ODYSSEY - OMIT THE OBSTACLES IF YOU CAN #######
######### THE 2D PLATFORMER GAME FROM THE PAST - REINTRODUCED! #######################
######### alagu ######### 5.7.24 #####################################################
import pygame
from pygame.locals import *  # helps to import everything you need to start the game
from pygame import mixer
import pickle
from os import path

pygame.mixer.init()

pygame.init()                                   # initialise pygame

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

#background music
pygame.mixer_music.load("Fletcher BGM _ Devi Sri Prasad _ Dasavathaaram.mp3")
pygame.mixer_music.play(loops=-1)

#all sound files
collision_sound = pygame.mixer.Sound("img_game_over.wav")
jumpup_sound = pygame.mixer.Sound("img_jump.wav")
coin_sound = pygame.mixer.Sound("img_coin.wav")



screen = pygame.display.set_mode((screen_width, screen_height))    # creates a game window
pygame.display.set_caption('OBSTACLE ODYSSEY - OMIT THE OBSTACLES IF YOU CAN')


#define font
font = pygame.font.SysFont('Herculanum', 70)
font_score = pygame.font.SysFont('Herculanum', 30)

# defining game variables
tile_size = 50
game_over = 0
main_menu = True
level = 1
max_levels = 7
score = 0

#define colours
black = (255, 255, 255)
blue = (0, 0, 255)


#loading images
moon_img = pygame.image.load('crescent-moon-png-35142.png')   
background_img = pygame.image.load('2472521.jpg')
restart_img = pygame.image.load('restart_btn.png')
start_img = pygame.image.load('start_btn.png')
exit_img = pygame.image.load('exit_btn.png')

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

#function to reset level
def reset_level(level):
	player.reset(100, screen_height - 130)
	blob_group.empty()
	platform_group.empty()
	lava_group.empty()
	exit_group.empty()                                   #### all the items are destroyed and the player is reset to level 0
	#load in level data and create world
	if path.exists(f'level{level}_data'):
		pickle_in = open(f'level{level}_data', 'rb')
		world_data = pickle.load(pickle_in)
	world = World(world_data)

	return world

class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False

	def draw(self):
		action = False           ### variable that tells the user that they clicked the button
		# get mouse position
		pos = pygame.mouse.get_pos()
		# check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True
		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False
		# draw button
		screen.blit(self.image, self.rect)
		return action

class Player():
	def __init__(self, x, y):
		self.reset(x, y)
	def update (self, game_over):
		dx = 0
		dy = 0
		walk_cooldown = 5
		collision_threshold = 20
		
		if game_over == 0:
			#get keypresses
			key = pygame.key.get_pressed()
			if key [pygame.K_SPACE] and self.jumped == False and self.in_air == False:
				jumpup_sound.play()
				self.vel_y = -15
				self.jumped = True
			if key [pygame.K_SPACE] == False:
				self.jumped = False
			if key[pygame.K_a]:
				dx -= 5
				self.counter += 1
				self.direction = -1                #### flipping valkyrie to the left
			if key[pygame.K_d]:
				dx += 5
				self.counter += 1
				self.direction = 1

			if key[pygame.K_a] == False and key [pygame.K_d] == False:
				self.counter = 0
				self.index = 0
				if self.direction == 1:            ### prevents valkyrie from turning back to the right when the key is not pressed
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]

			#handle animation
			self.counter += 1
			if self.counter > walk_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]              

			#add gravity
			self.vel_y += 1
			if self.vel_y > 10:
				self.vel_y = 10
			dy += self.vel_y

			#check for collision
			self.in_air = True
			for tile in world.tile_list:
				#check for collision in x direction
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#check for collision in y direction
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below the ground i.e. jumping
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					#check if above the ground i.e. falling
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False

			#check for collisions with enemies
			if pygame.sprite.spritecollide(self, blob_group, False):
				game_over = -1
				collision_sound.play()
			#check for collisions with lava
			if pygame.sprite.spritecollide(self, lava_group, False):
				game_over = -1
				collision_sound.play()
			#check for collisions with exit
			if pygame.sprite.spritecollide(self, exit_group, False):
				game_over = 1       ## not -1 as the player is not dead and is moving on to the next level

			#check for collision with platforms
			for platform in platform_group:
				#collision in the x-direction
				if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#collision in the y-direction
				if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below platform 
					if abs((self.rect.top + dy) - platform.rect.bottom) < collision_threshold:
						self.vel_y = 0    ### valkyrie must stop moving in the y-direction when it hits something
						dy = platform.rect.bottom - self.rect.top
					#check if above platform
					elif abs((self.rect.bottom + dy) - platform.rect.top) < collision_threshold:
						self.rect.bottom = platform.rect.top - 1       ### so that valkyrie keeps falling as the platform moves up and down
						dy = 0
						self.in_air = False
					#move sideways with the platform
					if platform.move_x != 0:
						self.rect.x  += platform.move_direction


										

			#update player coordinates
			self.rect.x += dx
			self.rect.y += dy

		elif game_over == -1:
			self.image = self.killed_image
			draw_text('GAME OVER!', font, blue, (screen_width // 2) - 200, screen_height // 2)
			if self.rect.y > 200:
				self.rect.y -= 5

			
		

		# drawing the player onto the screen
		screen.blit(self.image, self.rect)
		pygame.draw.rect(screen, (255,255,255), self.rect, 2)

		return game_over
	def reset (self, x , y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range (1, 5):
			img_right = pygame.image.load(f'valkyrie{num}.png')
			img_right = pygame.transform.scale(img_right, (40,80))
			img_left = pygame.transform.flip(img_right, True, False)         # flipping the right image on the axis
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.killed_image = pygame.image.load('ghost.png')
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()     ### creating a rectangle
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.direction = 0
		self.in_air = True                         ## assuming that valkyrie starts off in mid-air


		
		
            
class World():
	def __init__(self, data):
		self.tile_list = []

		#load images
		dirt_img = pygame.image.load('dirt.png')
		grass_img = pygame.image.load('grass.png')
		

		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
				if tile == 1:
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 2:
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 3:
					blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
					blob_group.add(blob)
				if tile == 4:
					platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)    ### moving in the x-direction by 1 and in the y-direction by 0
					platform_group.add(platform)
				if tile == 5:
					platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)    ### moving in the x-direction by 0 and in the y-direction by 1
					platform_group.add(platform)
				if tile == 6:
					lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
					lava_group.add(lava)
				if tile == 7:
					coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
					coin_group.add(coin)
				if tile == 8:
					exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2) )
					exit_group.add(exit)
				col_count += 1
			row_count += 1

	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])
     
#defining an enemy class
class Enemy(pygame.sprite.Sprite):                   ### using sprite class that is already in pygame
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('blob.png')
		self.rect = self.image.get_rect()            ### creating a rectangle
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 1
		self.move_counter = 0
	
	def update(self):
		self.rect.x += self.move_direction           #### the x-coordinate will increase (so it moves to the right)
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1

class Platform(pygame.sprite.Sprite):
	def __init__(self, x, y, move_x, move_y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('platform.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2)) ## scaling the image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_counter = 0  ## only applies to any instances within the platform class so doesn't clash with the enemy class
		self.move_direction = 1
		self.move_x = move_x
		self.move_y = move_y
	
	def update(self):
		self.rect.x += self.move_direction * self.move_x                    ##### all of the platforms will run on this part of the code and their x & y coordinates are adjusted by these 2 lines of code
		self.rect.y += self.move_direction * self.move_y        
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1




#defining a lava class
class Lava(pygame.sprite.Sprite):
	def __init__ (self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('lava.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))          #### scaling the lava image
		self.rect = img.get_rect()
		self.rect.x = x
		self.rect.y = y

#defining a coin class
class Coin(pygame.sprite.Sprite):
	def __init__ (self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('coin.png')
		self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2)) 
		self.rect = img.get_rect()
		self.rect.center = (x,y)
		




# 0 = nothing, 1 = dirt, 2 = grass, 3 = blob, 6 = lava, 8 = exit to the next level
world_data = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1], 
[1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1], 
[1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1], 
[1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]


class Exit(pygame.sprite.Sprite):
	def __init__ (self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('exit.png')
		self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))         
		self.rect = img.get_rect()
		self.rect.x = x
		self.rect.y = y	

player = Player(100, screen_height - 130)
blob_group = pygame.sprite.Group()                  ### creating a new empty group like a list for the enemies (blob and lava)
lava_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
#load in level data and create world
if path.exists(f'level{level}_data'):
	pickle_in = open(f'level{level}_data', 'rb')
	world_data = pickle.load(pickle_in)
world = World(world_data)

#creating buttons
restart_button = Button (screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)
run = True
while run:

	clock.tick(fps)
	screen.blit(background_img, (0,0))               ### function to help put the image on the screen
	screen.blit(moon_img, (10,10))

	if main_menu == True:
		if start_button.draw():
			main_menu = False
		if exit_button.draw():
			run = False
	else:									         ### everything under the else statement is the game logic (controls of the player moving around + collision detection)
		world.draw()
		
		if game_over == 0:
			blob_group.update()
			platform_group.update()
			#update score
			#check if a coin has been collected
			if pygame.sprite.spritecollide(player, coin_group, True):
				score += 1
				coin_sound.play()
			draw_text('x ' + str (score), font_score, black, tile_size - 2, 15)

		blob_group.draw(screen)                      ### draws the enemies on the screen
		platform_group.draw(screen)
		lava_group.update()
		lava_group.draw(screen)
		exit_group.draw(screen)
		coin_group.draw(screen)

		#create dummy coin for showing the score
		score_coin = Coin(tile_size // 2, tile_size // 2)
		coin_group.add(score_coin)
		draw_text('Level ' + str(level), font_score, black, tile_size + 50, 10)
		

		game_over = player.update(game_over)
		# if player died
		if game_over == -1:
			if restart_button.draw():
				world_data = []                                               
				world = reset_level(level)                        ### clearing my world data and creating a new instance of it by calling that function to run the reset process
				game_over = 0
		# if player completed level
		if game_over == 1:
			#reset game and go to next level
			level += 1
			if level <= max_levels:
				#reset level
				world_data = []                                               ### resets current data and inserts the new data for the next level
				world = reset_level(level)
				game_over = 0
				pass
			else:
				draw_text('YOU WON!', font, blue, (screen_width // 2) - 140, screen_height // 2)
				if restart_button.draw():
					level = 1
					#reset level
					world_data = []                                               
					world = reset_level(level)
					game_over = 0
					score = 0
    
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()
