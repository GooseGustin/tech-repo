# C:/Users/BADUNGS/AppData/Local/Programs/Python/Python37/argon
import pygame
from pygame.locals import *
from pygame.math import Vector2
from sys import exit
from random import randint
from logging import *

basicConfig(
    level=DEBUG,
    format='%(asctime)s - %(message)s'
)
disable(level=WARNING)

# Initialise
pygame.init()
pygame.mixer.init()
pygame.font.init()

# Global Constants
WIDTH = 800; HEIGHT = 500
SCREEN_SIZE = (WIDTH, HEIGHT+1)
screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
pygame.display.set_caption('Snake with Pygame')

REFOOD = USEREVENT + 1 # event posted for repositioning food
# DEADSNAKE = USEREVENT + 1

SCORE_FONT = pygame.font.SysFont('comicsans', 40)
DARK_BLUE = (6,6,20)
CYAN = (0,100,100)
SNAKE_GREEN = (0,200,50)
DARK_GREEN = (0,150,0)
FOOD_PINK = (200,0,200)
COLUMNS = 20 # 40 # 10 # 20 # 5
ROWS = 25 # 50 # 10 # 25 # 5
GRID_HEIGHT = ROWS # How come not by ROWS?
GRID_WIDTH = COLUMNS
# GRID_SIZE = (GRID_WIDTH, GRID_HEIGHT)

clock = pygame.time.Clock()

def drawBlock(block_list, col):
    for block in block_list:
        if block.colour:
             pygame.draw.rect(screen, block.colour, block)
        else:
            pygame.draw.rect(screen, col, block)

def drawGrid():
    # Draw the grid lines
    for i in range(0, HEIGHT, ROWS):
        pygame.draw.line(screen, CYAN, (0,i), (WIDTH,i)) # screen, colour, (init_pos), (final_pos)

    for j in range(0, WIDTH, COLUMNS):
        pygame.draw.line(screen, CYAN, (j,0), (j,HEIGHT))

def drawWindow(snake, food, score_text):
    # This function updates the screen contents
    screen.fill(DARK_BLUE)
    drawGrid()
    score = SCORE_FONT.render(score_text, 1, CYAN)
    screen.blit(score, (20,20))
    snake.draw()
    food.draw()
    
    pygame.display.update()

class Block(pygame.Rect):
    def __init__(self, x=1, y=1, width=GRID_WIDTH, length=GRID_HEIGHT):
        super(Block, self).__init__(x, y, width, length)
        self.direction = Vector2(0,0)
        self.pos = (self.x, self.y)
        self.ind = 0
        self.colour = None
        

class Food(object):
    
    def __init__(self, snake):
        # Place food in a random position on the screen, not on the edge rows and columns
        self.pos = self.getNewPos()
        snake_poses = [segment.pos for segment in snake.body]
        # Avoid placement on snake
        while self.pos in snake_poses:
            self.pos = self.getNewPos()
        self.block = Block(*self.pos)   # create food block

    def getNewPos(self):
        x_pos = randint(1,WIDTH/COLUMNS-1)*GRID_WIDTH # ranges from 2nd column to 2nd to last
        y_pos = randint(1,HEIGHT/ROWS-1)*GRID_HEIGHT # ranges from 2nd row to 2nd to last
        return (x_pos, y_pos)

    def reposition(self, snake):
        # This fxn will be called from the snake class, when it detects that the food block has
        # been touched (eaten)
        snake_poses = [segment.pos for segment in snake.body]
        self.pos = self.getNewPos()
        while self.pos in snake_poses:
            self.pos = self.getNewPos()
        # self.x, self.y = self.pos[0], self.pos[1]

    def draw(self):
        # Draw the block a pink colour
        drawBlock([self.block], FOOD_PINK)


class Snake(object):

    all_pos = []

    def __init__(self):
        self.head = Block(WIDTH/2, HEIGHT/2)
        self.head.direction = Vector2(-1,0)
        self.head.ind = -1
        self.head.colour = DARK_GREEN
        self.body = [self.head]
        self.all_pos.append(self.head.pos)
        self.length = len(self.body)
        self.is_dead = False

    def reset(self):
        self.head.x, self.head.y = (WIDTH/2, HEIGHT/2)
        self.all_pos = []
        self.head.direction = Vector2(-1,0)
        self.head.ind = -1
        # self.head.colour = DARK_GREEN
        self.body = [self.head]
        self.all_pos.append(self.head.pos)
        self.length = len(self.body)
        self.is_dead = False

    def eatFood(self, food):
        # If head meets food, add a segment to snake body
        if self.head.pos == food.pos:
            # Move the head, leaving a vacancy right behind it
            self.head.x += self.head.direction.x * GRID_WIDTH
            self.head.y += self.head.direction.y * GRID_HEIGHT
            self.head.pos = (self.head.x, self.head.y)
            self.all_pos.append(self.head.pos)

            # Create a new segment
            segment = Block()
            # Insert new segment right after the head, filling vacancy
            segment.ind = self.body[-1].ind - 1 # Get next index after last segment in body list --> head
            segment.pos = self.all_pos[segment.ind] # Get the position from all_pos using its index
            segment.x = segment.pos[0]
            segment.y = segment.pos[1]
            self.body.append(segment) # Add to body

            # Trigger signal (event) to reposition food
            repos_food = pygame.event.Event(REFOOD, message="Reposition Food")
            pygame.event.post(repos_food)

            # Update length (for score)
            self.length = len(self.body)

            return True # if food eaten
        return # if not food eaten

    def turn(self, turn_direction):
        self.head.direction = turn_direction

    def die(self):
        self.is_dead = True

    def moveForward(self):
        ''' Change the positions of all snake segments '''
        # Check whether it's already crashed or not
        if self.hasCrashed():
            # repos_food = pygame.event.Event(REFOOD, message="Reposition Food")
            # pygame.event.post(repos_food)
            self.reset()
            self.all_pos = []

        elif not self.is_dead:
            # Change the x and y coordinates of the head 1 cell unit in the snake's direction
            self.head.x += self.head.direction.x * GRID_WIDTH
            self.head.y += self.head.direction.y * GRID_HEIGHT

            # handle entering boundaries
            if self.head.x < 0: # leaves the left
                self.head.x = WIDTH - GRID_WIDTH 
                # WIDTH - GRID_WIDTH because the top-left of the head has to move into the screen by at least 1 
                # cell unit/width, not the edge/outside of the screen. Same with HEIGHT - GRID_HEIGHT
            elif self.head.x > WIDTH-5:  # leaves the right
                self.head.x = 0 
            if self.head.y < 0: # leaves the top
                self.head.y = HEIGHT - GRID_HEIGHT 
            elif self.head.y > HEIGHT-5: # leaves the bottom
                self.head.y = 0 

            self.head.pos = (self.head.x, self.head.y) # Update the position of the head and save it as the 
            self.all_pos.append(self.head.pos)  # last position in all_pos

            # Shift the segments along
            # Here, the segments will get the previous positions of the segments in front of them
            for i in range(1, len(self.body)): # Not from the first, because I'm not shifting the head.
                try:
                    segment = self.body[i] # get segment
                    segment.pos = self.all_pos[segment.ind] # get the position using its index, 1 more than the
                    segment.x = segment.pos[0]              # next one
                    segment.y = segment.pos[1] # update its x and y to the position returned
                except IndexError:
                    pass # list index out of range
            
            # Make the number of positions no longer than the number of segments, ie, truncate all_pos to 
            # contain only as many positions as the number of segments.
            if len(self.body) > 1: 
                self.all_pos = self.all_pos[-len(self.body):]
    
    def draw(self):
        # draw snake blocks onto the screen
        drawBlock(self.body, SNAKE_GREEN)

    def hasCrashed(self):
        self.all_pos = self.all_pos[-len(self.body):]
        if self.head.pos in self.all_pos[:-1]:
            self.die()
        return self.is_dead


def main():

    # Constants
    Kaa = Snake()
    fud = Food(Kaa)
    score = 0

    # Main loop
    running = True
    while running:
        clock.tick(10) # 5

        for event in pygame.event.get():
            # Escape
            if event.type == QUIT:
                running = False

            # Change food position
            if event.type == REFOOD:
                fud = Food(Kaa)

            # Handle turns
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    turn_direction = Vector2(0,-1)
                    Kaa.turn(turn_direction)
                elif event.key == K_DOWN:
                    turn_direction = Vector2(0,1)
                    Kaa.turn(turn_direction)
                elif event.key == K_LEFT:
                    turn_direction = Vector2(-1,0)
                    Kaa.turn(turn_direction)
                elif event.key == K_RIGHT:
                    turn_direction = Vector2(1,0)
                    Kaa.turn(turn_direction)
                else: pass
        
        Kaa.moveForward()
        Kaa.eatFood(fud)
        warning(str(Kaa.is_dead))
        score = Kaa.length-1
        score_text = "Score: " + str(score)
        
        drawWindow(Kaa, fud, score_text)
    
    pygame.quit()

if __name__ == "__main__":
    main()
    exit()
