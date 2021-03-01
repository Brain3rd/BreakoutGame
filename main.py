import pygame
import os
import random

pygame.font.init()

WIDTH, HEIGHT = 768, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('BreakOut')

# Colors
COLOR_BG = (0, 0, 0)  # Black
COLOR_FONT = (255, 255, 255)

# Frames / second
FPS = 60

# Load images
PADDLE_IMG_BLUE = pygame.image.load(os.path.join('images', 'paddle_blue.png'))
# PADDLE_IMG_RED = pygame.image.load(os.path.join('images', 'paddle_red.png'))
BALL_IMG = pygame.image.load(os.path.join('images', 'ball_blue.png'))
# Brick images
BRICK_IMG = []
for n in range(1, 6):
    brig = pygame.image.load(os.path.join('images', f'brick_{n}.png'))
    BRICK_IMG.append(brig)

# Resize
PADDLE_SIZE = (PADDLE_IMG_BLUE.get_width() + 0, PADDLE_IMG_BLUE.get_height())
PADDLE_BLUE = pygame.transform.scale(PADDLE_IMG_BLUE, PADDLE_SIZE)
BALL_SIZE = (BALL_IMG.get_width() + 0, BALL_IMG.get_height())
BALL_BLUE = pygame.transform.scale(BALL_IMG, BALL_SIZE)

# Rotate
# PADDLE_RED = pygame.transform.rotate(PADDLE_IMG_RED, 90)


class Paddle:
    def __init__(self, x_pos, y_pos):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.paddle_img = None

    def refresh(self, window):
        # Draw objects (text/images) on screen
        # (0, 0) is top left, x += right, y += down
        window.blit(self.paddle_img, (self.x_pos, self.y_pos))

    def get_width(self):
        return self.paddle_img.get_width()

    def get_height(self):
        return self.paddle_img.get_height()

    def move(self, vel):
        self.x_pos += vel


class Player(Paddle):
    def __init__(self, x_pos, y_pos, image):
        super().__init__(x_pos, y_pos)
        self.paddle_img = image
        self.mask = pygame.mask.from_surface(self.paddle_img)

    def refresh(self, window):
        super().refresh(window)
        # self.status(window)

    def control_com(self, ball, speed, screen_width):
        # Move right
        if self.x_pos < ball.x_pos and self.x_pos - speed + self.get_width() + 10 < screen_width:
            self.x_pos += speed
        # Move left
        elif self.x_pos > ball.x_pos:
            self.x_pos -= speed


class Ball:
    def __init__(self, x_pos, y_pos, img, speed):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.img = img
        self.vel_x = speed
        self.vel_y = speed
        self.mask = pygame.mask.from_surface(self.img)

    def refresh(self, window):
        window.blit(self.img, (self.x_pos, self.y_pos))

    def move(self):
        # move ball / refresh rate
        self.x_pos += self.vel_x
        self.y_pos += self.vel_y

    def bounce_x(self):
        # Chance ball direction
        self.vel_x *= -1

    def bounce_y(self):
        # Change ball direction
        self.vel_y *= -1

    def bounce_ball(self, screen_width, screen_height, ball_with):
        # Move the ball
        self.move()
        # Bounce from walls
        if self.y_pos == 0:
            self.bounce_y()
        if self.x_pos > screen_width - ball_with or self.x_pos == 0:
            self.bounce_x()
        if self.y_pos > screen_height:
            return True

    def collision(self, object_1):
        # If ball collide with paddle
        offset_x = self.x_pos - object_1.x_pos
        offset_y = self.y_pos - object_1.y_pos
        return object_1.mask.overlap(self.mask, (offset_x, offset_y)) is not None


class Brick:

    def __init__(self, x_pos, y_pos, img):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def refresh(self, window):
        window.blit(self.img, (self.x_pos, self.y_pos))


def bricks_overlap(new_brick, all_bricks):
    # If ball collide with paddle
    offset_x = new_brick.x_pos - all_bricks.x_pos
    offset_y = new_brick.y_pos - all_bricks.y_pos
    return all_bricks.mask.overlap(new_brick.mask, (offset_x, offset_y)) is not None


def make_brigs(amount):
    bricks = []
    brick_width = BRICK_IMG[0].get_width()
    brick_height = BRICK_IMG[0].get_height()
    brick = Brick(random.randrange(0, WIDTH, brick_width),
                  random.randrange(0, HEIGHT - 300, brick_height),
                  BRICK_IMG[random.randint(0, 4)])
    bricks.append(brick)

    for i in range(amount):
        # Make new brig
        brick = Brick(random.randrange(0, WIDTH, brick_width),
                      random.randrange(0, HEIGHT - 300, brick_height),
                      BRICK_IMG[random.randint(0, 4)])
        # Check that new brick don't overlap with existing brick
        if not bricks_overlap(brick, bricks[-1]):
            bricks.append(brick)
    return bricks


def breakout():
    main_text = True
    game_on = True
    paddle_speed = 10
    score = 0
    player_control = False
    starting_bricks = 10

    # Fonts
    # random_font = random.choice(pygame.font.get_fonts())
    # print(random_font)
    title_font = pygame.font.SysFont('tahoma', 30)
    font = pygame.font.SysFont('tahoma', 30)

    # Make player with paddle; Insert x, y and color of the paddle
    # Paddle position
    paddle_blue_pos_x = int(400 - PADDLE_BLUE.get_width() / 2)
    paddle_blue_pos_y = 530
    player = Player(paddle_blue_pos_x, paddle_blue_pos_y, PADDLE_BLUE)
    # Make ball; Starting position, color and speed
    ball = Ball(100, 200, BALL_BLUE, 5)
    # Make Bricks
    bricks = make_brigs(starting_bricks)

    clock = pygame.time.Clock()

    # Draw objects on the screen
    def refresh_window():
        # Background color
        WIN.fill(COLOR_BG)
        # If background image
        # WIN.blit(BG, (0,0))

        # Score
        score_label = font.render(f'Score: {score}', True, COLOR_FONT)
        WIN.blit(score_label, (10, HEIGHT - 40))

        # Refresh player in screen
        player.refresh(WIN)

        # Refresh ball too
        ball.refresh(WIN)

        if len(bricks) == 0:
            new_bricks = make_brigs(starting_bricks + 10)
            for brick in new_bricks:
                bricks.append(brick)

        # Refresh brigs
        for x in bricks:
            x.refresh(WIN)

        # Start text
        if main_text:
            title_text = title_font.render("Press mouse button to begin...", True, COLOR_FONT)
            WIN.blit(title_text, (WIDTH / 2 - title_text.get_width() / 2, 350))

        # Update window
        pygame.display.update()

    while game_on:
        # Keeps frame rate from going over; input refresh rate
        clock.tick(FPS)
        refresh_window()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                player_control = True
                score = 0
                main_text = False
                # Make brigs
                bricks = make_brigs(starting_bricks)
                refresh_window()
            if event.type == pygame.QUIT:
                quit()

        # Ball bounces from walls, if off screen returns True
        # Insert screen dimensions and ball width
        if ball.bounce_ball(WIDTH, HEIGHT, BALL_BLUE.get_width()):
            breakout()

        if player_control:
            # Gives control of the paddle; input paddle speed
            keys = pygame.key.get_pressed()
            # Left
            if keys[pygame.K_LEFT] and player.x_pos - paddle_speed > 0:
                player.x_pos -= paddle_speed
                if ball.collision(player):
                    ball.bounce_x()
            # Right
            if keys[pygame.K_RIGHT] and player.x_pos - paddle_speed + player.get_width() + 10 < WIDTH:
                player.x_pos += paddle_speed
                if ball.collision(player):
                    ball.bounce_x()
        else:
            # Computer controls paddle
            player.control_com(ball, 5, WIDTH)

        # Bounce from paddle
        if ball.collision(player):
            ball.bounce_y()

        # Bounce from brick
        for i in bricks:
            if ball.collision(i):
                if ball.y_pos - i.y_pos in range(-50, 50) and ball.y_pos > 10:
                    ball.bounce_y()
                if ball.x_pos - i.x_pos in range(-30, 30) and ball.x_pos in range(10, WIDTH):
                    ball.bounce_x()
                bricks.remove(i)
                score += 1

    pygame.quit()


if __name__ == "__main__":
    breakout()
