# C:/Users/BADUNGS/AppData/Local/Programs/Python/Python37/argon
import pygame
from pygame.locals import *
from gameobjects.vector2 import Vector2
from sys import exit
from random import *
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
GRID_HEIGHT = HEIGHT/(HEIGHT/ROWS) # How come not by ROWS?
GRID_WIDTH = WIDTH/(WIDTH/COLUMNS)
GRID_SIZE = (GRID_WIDTH, GRID_HEIGHT)

clock = pygame.time.Clock()

def drawBlock(block_list, col):
    for block in block_list:
        if block.colour:
             pygame.draw.rect(screen, block.colour, block)
        else:
            pygame.draw.rect(screen, col, block)
    # pass

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
        self.pos = (randint(2,WIDTH/COLUMNS-2)*GRID_WIDTH, 
                randint(2,HEIGHT/ROWS-2)*GRID_HEIGHT)
        snake_poses = [segment.pos for segment in snake.body]
        while self.pos in snake_poses:
            info('Food in snake')
            self.pos = (randint(1,WIDTH/COLUMNS-1)*GRID_WIDTH, 
                    randint(1,HEIGHT/ROWS-1)*GRID_HEIGHT)
        self.block = Block(*self.pos)

    def repos(self, snake):
        snake_poses = [segment.pos for segment in snake.body]
        self.pos = (randint(1,WIDTH/COLUMNS-1)*GRID_WIDTH, 
                randint(1,HEIGHT/ROWS-1)*GRID_HEIGHT)
        while self.pos in snake_poses:
            info('Food in snake')
            self.pos = (randint(1,WIDTH/COLUMNS-1)*GRID_WIDTH, 
                    randint(1,HEIGHT/ROWS-1)*GRID_HEIGHT)
        self.x, self.y = self.pos[0], self.pos[1]

    def draw(self):
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

    def eatFood(self, food):
        # If head meets food, add a segment to snake body
        if (self.head.x, self.head.y) == food.pos:

            self.head.x += self.head.direction.x * GRID_WIDTH
            self.head.y += self.head.direction.y * GRID_HEIGHT
            self.head.pos = (self.head.x, self.head.y)
            self.all_pos.append(self.head.pos)
            # self.head.ind += 1

            segment = Block()
            segment.ind = self.body[-1].ind - 1
            segment.pos = self.all_pos[segment.ind]
            segment.x = segment.pos[0]
            segment.y = segment.pos[1]
            self.body.append(segment)
            # Signal to reposition food
            repos_food = pygame.event.Event(REFOOD, message="Reposition Food")
            pygame.event.post(repos_food)

            self.length = len(self.body)
        
            return 1
        return 0

    def turn(self, turn_direction):
        self.head.direction = turn_direction
        # self.turn_points.append((self.head.x, self.head.y))
        # info(str(len(self.body)))
    
    def die(self):
        self.is_dead = True
        # snake_is_dead = pygame.event.Event(DEADSNAKE, message="Snake is dead")
        # pygame.event.post(snake_is_dead)
    
    def moveForward(self):
        # Change position of all snake segments
        if self.hasCrashed():
            repos_food = pygame.event.Event(REFOOD, message="Reposition Food")
            pygame.event.post(repos_food)
            self.__init__()
            self.all_pos = []

        elif not self.is_dead:
            self.head.x += self.head.direction.x * GRID_WIDTH
            self.head.y += self.head.direction.y * GRID_HEIGHT

            # handle entering boundaries
            if self.head.x < 0:
                self.head.x = WIDTH - GRID_WIDTH
            elif self.head.x > WIDTH-5:
                self.head.x = 0 
            if self.head.y < 0:
                self.head.y = HEIGHT - GRID_HEIGHT
            elif self.head.y > HEIGHT-5:
                self.head.y = 0 

            self.head.pos = (self.head.x, self.head.y)
            # self.head.ind += 1
            self.all_pos.append(self.head.pos)

            for i in range(1, len(self.body)): # segment in self.body:
                try:
                    segment = self.body[i]
                    # segment.ind += 1
                    segment.pos = self.all_pos[segment.ind]
                    segment.x = segment.pos[0]
                    segment.y = segment.pos[1]
                except IndexError:
                    info('list index out of range')
                    # print(self.all_pos)
            
            if len(self.body) > 2:
                self.all_pos = self.all_pos[-len(self.body):]
    
    def draw(self):
        # draw snake blocks onto the screen
        drawBlock(self.body, SNAKE_GREEN)

    def hasCrashed(self):
        self.all_pos = self.all_pos[-len(self.body):]
        # if self.head.x>=WIDTH or self.head.x<0 or self.head.y>=HEIGHT or self.head.y<0:
        #     self.die()
        #     info("Snake is is_dead")
        if self.head.pos in self.all_pos[:-1]:
            self.die()
        # self.just_crashed.append(self.is_dead)
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
