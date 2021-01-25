import pygame
import os
import random
import time

pygame.font.init()

w, h = 1000, 1000
window = pygame.display.set_mode((w, h))
pygame.display.set_caption('Space Invaders')

# LOAD IMAGES
redSpaceship = pygame.image.load(os.path.join('assets', 'pixel_ship_red_small.png'))
greenSpaceship = pygame.image.load(os.path.join('assets', 'pixel_ship_green_small.png'))
blueSpaceship = pygame.image.load(os.path.join('assets', 'pixel_ship_blue_small.png'))

# PLAYERS SHIP
yellowSpaceship = pygame.image.load(os.path.join('assets', 'pixel_ship_yellow.png'))

# LASERS
redLasers = pygame.image.load(os.path.join('assets', 'pixel_laser_red.png'))
yellowLasers = pygame.image.load(os.path.join('assets', 'pixel_laser_yellow.png'))
greenLasers = pygame.image.load(os.path.join('assets', 'pixel_laser_green.png'))
blueLasers = pygame.image.load(os.path.join('assets', 'pixel_laser_blue.png'))

# BACKGROUND IMAGE
background = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'background-black.png')), (w, h))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (height >= self.y >= 0)

    def collision(self, object):
        return collide(self, object)


class Ship:
    coolDownTime = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.shipImg = None
        self.laserImg = None
        self.lasers = []
        self.coolDown = 0

    def draw(self, window):
        window.blit(self.shipImg, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, pl):
        self.cool_down()
        for las in self.lasers:
            las.move(vel)
            if las.off_screen(h):
                self.lasers.remove(las)
            elif las.collision(pl):
                pl.health -= 10
                self.lasers.remove(las)

    def cool_down(self):
        if self.coolDown >= self.coolDownTime:
            self.coolDown = 0
        elif self.coolDown > 0:
            self.coolDown += 1

    def shoot(self):
        if self.coolDown == 0:
            laser = Laser(self.x, self.y, self.laserImg)
            self.lasers.append(laser)
            self.coolDown = 1

    def get_width(self):
        return self.shipImg.get_width()

    def get_height(self):
        return self.shipImg.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.shipImg = yellowSpaceship
        self.laserImg = yellowLasers
        self.mask = pygame.mask.from_surface(self.shipImg)
        self.maxHealth = health

    def move_lasers(self, vel, enemies):
        self.cool_down()
        for las in self.lasers:
            las.move(vel)
            if las.off_screen(h):
                self.lasers.remove(las)
            else:
                for enemy in enemies:
                    if las.collision(enemy):
                        enemies.remove(enemy)
                        self.lasers.remove(las)

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.shipImg.get_height() + 10, self.shipImg.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0),
                         (self.x, self.y + self.shipImg.get_height() + 10,
                          self.shipImg.get_width() * (self.health / self.maxHealth), 10))


class Enemy(Ship):
    colorMap = {
        'red': (redSpaceship, redLasers),
        'green': (greenSpaceship, greenLasers),
        'blue': (blueSpaceship, blueLasers)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.shipImg, self.laserImg = self.colorMap[color]
        self.mask = pygame.mask.from_surface(self.shipImg)

    def move(self, velocity):
        self.y += velocity

    def shoot(self):
        if self.coolDown == 0:
            laser = Laser(self.x - 20, self.y, self.laserImg)
            self.lasers.append(laser)
            self.coolDown = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def main():
    FPS = 60
    run = True

    clock = pygame.time.Clock()

    level = 0
    lives = 5

    font = pygame.font.SysFont('comicsans', 55)
    lostFont = pygame.font.SysFont('comicsans', 70)

    player = Player(500, 480)
    pVelocity = 7
    laserVel = 5

    enemies = []
    waveLength = 1
    enemyVelocity = 1

    lost = False
    lostTime = 0

    def redraw_window():
        window.blit(background, (0, 0))

        #    DRAW TEXT
        livesLabel = font.render(f'Lives: {lives}', 1, (255, 255, 255))
        levelLabel = font.render(f'Level: {level}', 1, (255, 255, 255))

        window.blit(livesLabel, (10, 10))
        window.blit(levelLabel, (w - levelLabel.get_width() - 10, 10))

        for x in enemies:
            x.draw(window)

        player.draw(window)

        if lost:
            lostLabel = lostFont.render('You Lost!!', 1, (255, 0, 0))
            window.blit(lostLabel, (w / 2 - lostLabel.get_width() / 2, 500))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lostTime += 1

        if lost:
            if lostTime > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            waveLength += 5
            for i in range(waveLength):
                enemy = Enemy(random.randrange(50, w - 100), random.randrange(-1500, -100),
                              random.choice(['red', 'blue', 'green']))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - pVelocity > 0:  # LEFT
            player.x -= pVelocity
        if keys[pygame.K_d] and player.x + pVelocity + player.get_width() < w:  # RIGHT
            player.x += pVelocity
        if keys[pygame.K_w] and player.y - pVelocity > 0:  # UP
            player.y -= pVelocity
        if keys[pygame.K_s] and player.y + pVelocity + player.get_height() + 10 < h:  # DOWN
            player.y += pVelocity
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies:
            enemy.move(enemyVelocity)
            enemy.move_lasers(laserVel, player)

            if random.randrange(0, 4 * FPS) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > h:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laserVel, enemies)


def main_menu():
    menuFont = pygame.font.SysFont('comicsans', 70)
    run = True
    while run:
        window.blit(background, (0, 0))
        menuTitle = menuFont.render('Press the mouse to begin...', 1, (255, 255, 255))
        window.blit(menuTitle, (w / 2 - menuTitle.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    quit()


main_menu()
