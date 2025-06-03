import pygame
import random
import math
import json
from datetime import datetime


# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((600, 400))  # Wider screen for sidebar
pygame.display.set_caption("Pong Championship")
clock = pygame.time.Clock()

# Constants
COLORS = {
    'BLACK': (0,0,0), 
    'WHITE': (255,255,255), 
    'GREEN': (0,255,0),
    'RED': (255,0,0), 
    'YELLOW': (255,255,0), 
    'CYAN': (0,255,255),
    'ORANGE': (255,165,0)
}

DIFFICULTIES = {
    pygame.K_1: {'speed': 3, 'paddle': 80, 'label': 'Beginner'},
    pygame.K_2: {'speed': 4, 'paddle': 60, 'label': 'Advanced'},
    pygame.K_3: {'speed': 5, 'paddle': 40, 'label': 'Expert'}
}

# Game Classes
class Paddle:
    def __init__(self, x):
        self.rect = pygame.Rect(x, 160, 10, 80)
        self.score = 0
        
    def move(self, dy):
        self.rect.y = max(0, min(400 - self.rect.height, self.rect.y + dy))
        
    def draw(self):
        pygame.draw.rect(screen, COLORS['GREEN'], self.rect)

class Ball:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.rect = pygame.Rect(
            random.randint(100, 300),
            random.randint(100, 300),
            10, 10
        )
        angle = math.radians(random.choice([
            random.randint(45, 135),
            random.randint(225, 315)
        ]))
        self.speed = DIFFICULTIES[pygame.K_1]['speed']  # Default speed
        self.dx = math.cos(angle)
        self.dy = math.sin(angle)
        
    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        
        # Wall collisions (keep within left 400px)
        if self.rect.top <= 0 or self.rect.bottom >= 400:
            self.dy *= -1
            
        if self.rect.right >= 400:  # Right boundary at 400px
            self.dx *= -1
            
        if self.rect.left <= 0:
            return True
        return False

# Game Functions
def show_text(text, color, x, y, size=20, center=True):
    font = pygame.font.Font('freesansbold.ttf', size)
    surf = font.render(text, True, color)
    if center:
        rect = surf.get_rect(center=(x, y))
    else:
        rect = surf.get_rect(topleft=(x, y))
    screen.blit(surf, rect)
    return rect

def format_time(seconds):
    return f"{seconds//60:02}:{seconds%60:02}"

def handle_highscore(name, level, best_time, total_time):
    try:
        with open('highscores.json') as f:
            highscores = json.load(f)
    except: 
        highscores = []
    
    highscores.append({
        'name': name,
        'level': level,
        'best_time': best_time,
        'total_time': total_time,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    
    highscores.sort(key=lambda x: x['best_time'], reverse=True)
    
    with open('highscores.json', 'w') as f:
        json.dump(highscores[:10], f, indent=2)
    
    return highscores

# Game States
current_state = "ENTER_NAME"
player_name = ""
selected_level = ""
session_best_time = 0
total_session_time = 0
current_attempt = 1
attempt_times = []

# Game Objects
paddle = Paddle(20)
ball = Ball()

# Main Game Loop
running = True
while running:
    screen.fill(COLORS['BLACK'])
    # Draw game area border
    pygame.draw.line(screen, COLORS['WHITE'], (400, 0), (400, 400), 2)
    events = pygame.event.get()
    
    # Event Handling
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if current_state == "ENTER_NAME":
                if event.key == pygame.K_RETURN and player_name:
                    current_state = "SELECT_LEVEL"
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 15:
                        player_name += event.unicode
                        
            elif current_state == "SELECT_LEVEL":
                if event.key in DIFFICULTIES:
                    selected_level = DIFFICULTIES[event.key]['label']
                    paddle.rect.h = DIFFICULTIES[event.key]['paddle']
                    ball.speed = DIFFICULTIES[event.key]['speed']
                    current_state = "PLAY"
                    start_time = pygame.time.get_ticks()
                elif event.key == pygame.K_h:
                    current_state = "VIEW_HIGHSCORES"
                    
            elif current_state == "ATTEMPT_OVER":
                if event.key == pygame.K_SPACE and current_attempt < 3:
                    current_attempt += 1
                    ball.reset()
                    current_state = "PLAY"
                    start_time = pygame.time.get_ticks()
                    
            elif current_state == "SESSION_OVER":
                if event.key == pygame.K_r:
                    current_state = "ENTER_NAME"
                    player_name = ""
                    selected_level = ""
                    session_best_time = 0
                    total_session_time = 0
                    current_attempt = 1
                    attempt_times = []
                    paddle = Paddle(20)
                    ball.reset()
                    
            elif current_state == "VIEW_HIGHSCORES":
                current_state = "SELECT_LEVEL"

    # Game Logic
    if current_state == "PLAY":
        keys = pygame.key.get_pressed()
        paddle.move(-7 if keys[pygame.K_UP] else 7 if keys[pygame.K_DOWN] else 0)
        
        if ball.update():
            elapsed = (pygame.time.get_ticks() - start_time) // 1000
            attempt_times.append(elapsed)
            if elapsed > session_best_time:
                session_best_time = elapsed
                
            if current_attempt < 3:
                current_state = "ATTEMPT_OVER"
            else:
                total_session_time = sum(attempt_times)
                current_state = "SESSION_OVER"
                handle_highscore(player_name, selected_level, session_best_time, total_session_time)
        
        if ball.rect.colliderect(paddle.rect):
            # Improved collision physics
            relative_y = (paddle.rect.centery - ball.rect.centery) / (paddle.rect.height/2)
            ball.dx = abs(ball.dx)
            ball.dy = relative_y
            
            # Maintain ball speed
            length = math.hypot(ball.dx, ball.dy)
            if length > 0:
                ball.dx /= length
                ball.dy /= length
            
            paddle.score += 1

    # Rendering
    if current_state == "ENTER_NAME":
        show_text("Enter Your Name:", COLORS['WHITE'], 200, 100, 24)
        pygame.draw.rect(screen, COLORS['WHITE'], (50, 175, 300, 40), 2)
        show_text(player_name, COLORS['WHITE'], 200, 195, 24)
        show_text("Press ENTER when ready", COLORS['CYAN'], 200, 300)
        
    elif current_state == "SELECT_LEVEL":
        show_text(f"Welcome {player_name}!", COLORS['WHITE'], 200, 80, 24)
        show_text("Select Difficulty Level:", COLORS['WHITE'], 200, 120)
        show_text("[1] Beginner   [2] Advanced   [3] Expert", COLORS['WHITE'], 200, 180)
        show_text("Press H for Highscores", COLORS['ORANGE'], 200, 300)
        
    elif current_state == "PLAY":
        # Draw game elements (left side)
        paddle.draw()
        pygame.draw.ellipse(screen, COLORS['WHITE'], ball.rect)
        
        # Draw UI (right side)
        show_text(f"Player: {player_name}", COLORS['CYAN'], 420, 20, 18, False)
        show_text(f"Level: {selected_level}", COLORS['CYAN'], 420, 50, 18, False)
        show_text(f"Attempt: {current_attempt}/3", COLORS['YELLOW'], 500, 360)
        current_time = (pygame.time.get_ticks() - start_time) // 1000
        show_text(f"Time: {format_time(current_time)}", COLORS['YELLOW'], 420, 380, 18, False)
        if session_best_time > 0:
            show_text(f"Best: {format_time(session_best_time)}", COLORS['GREEN'], 500, 320)
        
    elif current_state == "ATTEMPT_OVER":
        show_text(f"Attempt {current_attempt} Time: {format_time(attempt_times[-1])}", COLORS['RED'], 200, 150, 24)
        show_text(f"Best Time: {format_time(session_best_time)}", COLORS['YELLOW'], 200, 200)
        show_text("Press SPACE for next attempt", COLORS['CYAN'], 200, 280)
        
    elif current_state == "SESSION_OVER":
        # Left side
        show_text("Game Session Complete!", COLORS['ORANGE'], 200, 50, 28)
        show_text(f"Your Best: {format_time(session_best_time)}", COLORS['YELLOW'], 200, 90)
        show_text(f"Total Time: {format_time(total_session_time)}", COLORS['CYAN'], 200, 120)
        
        # Right side rankings
        show_text("- Top Rankings -", COLORS['WHITE'], 500, 160, 20)
        try:
            with open('highscores.json') as f:
                highscores = sorted(json.load(f), key=lambda x: x['best_time'], reverse=True)[:5]
            
            for i, score in enumerate(highscores):
                y_pos = 190 + i * 30
                text = f"{i+1}. {score['name'][:8]} - {format_time(score['best_time'])}"
                show_text(text, COLORS['WHITE'], 450, y_pos, 18, False)
        except:
            show_text("No rankings yet!", COLORS['RED'], 500, 200)
        
        show_text("Press R to restart", COLORS['WHITE'], 500, 360, 18, False)
        
    elif current_state == "VIEW_HIGHSCORES":
        try:
            with open('highscores.json') as f:
                highscores = json.load(f)
            show_text("Top 10 Highscores", COLORS['ORANGE'], 500, 40, 24)
            for i, score in enumerate(highscores[:10]):
                y_pos = 80 + i * 30
                text = f"{i+1}. {score['name']} - {score['level']}"
                show_text(text, COLORS['WHITE'], 420, y_pos, 18, False)
                show_text(f"Best: {format_time(score['best_time'])}", COLORS['WHITE'], 580, y_pos, 18, False)
        except:
            show_text("No highscores yet!", COLORS['RED'], 500, 200)
        show_text("Press any key to return", COLORS['CYAN'], 500, 360)
    
    pygame.display.update()
    clock.tick(60)

pygame.quit()
