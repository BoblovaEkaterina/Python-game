import pygame
import os
import time
import random
pygame.font.init()

WIDTH = 700
HEIGHT = 700
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("CORONAVIRUS SHOOTER GAME")

ENEMY = pygame.image.load(os.path.join("pics","zombie.png"))
DOCTOR = pygame.image.load(os.path.join("pics","doctor.png"))
VIRUS_RED = pygame.image.load(os.path.join("pics","virus_r.png"))
VIRUS_GREEN = pygame.image.load(os.path.join("pics","virus_gr.png"))
PILL = pygame.image.load(os.path.join("pics","pill.png"))
BG = pygame.transform.scale(pygame.image.load(os.path.join("pics", "backgroundd.png")), (WIDTH, HEIGHT))

class Bullet:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, mmovve):  # вирусы двигаются только вниз
        self.y += mmovve

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Object:
    COOLDOWN = 30

    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.obj_img = None
        self.bullet_img = None
        self.bullets = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.obj_img, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(window)

    def move_bullets(self, velocity, obj):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(velocity)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            elif bullet.collision(obj):
                obj.health -= 10
                self.bullets.remove(bullet)


    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            bullet = Bullet(self.x+20 , self.y, self.bullet_img)
            self.bullets.append(bullet)
            self.cool_down_counter = 1

    def get_width(self):
        return self.obj_img.get_width()

    def get_height(self):
        return self.obj_img.get_height()

class Player(Object):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health=100)
        self.obj_img = DOCTOR
        self.bullet_img = PILL
        self.mask = pygame.mask.from_surface(self.obj_img)
        self.max_health = health


    def move_bullets(self, velocity, objs):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(velocity)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            else:
                for obj in objs:
                    if bullet.collision(obj):
                        objs.remove(obj)
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.obj_img.get_height() + 10, self.obj_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.obj_img.get_height() + 10, self.obj_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Object):
    COLOR_MAP = {
        "red": (VIRUS_RED),
        "green": (VIRUS_GREEN),
    }
    def __init__(self, x, y,color, health=100):
        super().__init__(x, y, health=100)
        self.obj_img = ENEMY
        self.bullet_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.obj_img)

    def move(self, mmovve): # враги двигаются только вниз
        self.y += mmovve

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_velocity = 1

    player_velocity = 5 # за нажатие игрок двигается на 5 пикселей
    bullet_velocity = 5

    player = Player (300,600)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        # вставляю фон
        WIN.blit(BG, (0, 0))
        # текст
        levels_text = main_font.render(f"Уровень: {level}", 1, (255, 255, 255))
        lives_text = main_font.render(f"Жизни: {lives}", 1, (255, 255, 255))

        WIN.blit(levels_text, (10,10))
        WIN.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("Вы проиграли!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        # как только на экране становится 0 врагов, мы переходим на новый уровень
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "green"]))
                enemies.append(enemy)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # программа закрывается нажатием на крестик в углу окна
                run = False


        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_velocity > 0: #лево
            player.x -= player_velocity
        if keys[pygame.K_d] and player.x + player_velocity + player.get_width() < WIDTH :  #право
            player.x += player_velocity
        if keys[pygame.K_w]and player.y - player_velocity > 0 : #верх
            player.y -= player_velocity
        if keys[pygame.K_s] and player.y + player_velocity + player.get_height() < HEIGHT : #низ
            player.y += player_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_velocity)
            enemy.move_bullets(bullet_velocity, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_bullets(-bullet_velocity, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 45)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Нажмите кнопку мыши, чтобы начать...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()

