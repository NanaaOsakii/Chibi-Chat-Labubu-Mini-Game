import pygame
import sys
import random
import time
import math
from enum import Enum

# Constants
HELL_WIDTH, HELL_HEIGHT = 1000, 800
NEON_GREEN = (0, 255, 0)
SHADOW_BLACK = (0, 0, 0)
GHOST_WHITE = (255, 255, 255)
FPS = 70
fkn_fragz = 0

class RiotMode(Enum):
    MENU = 0
    CHAOS = 1
    DEAD = 2
    FROZEN = 3

class RamRaid:
    def __init__(self):
        self.riot_coord = [HELL_WIDTH, 717]
        self.hp = 50
        self.charge_speed = 5
        self.dmg = 25
        self.hitbox = 40
        self.load_img()

    def load_img(self):
        try:
            self.image = pygame.image.load('hm-removebg-preview.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.hitbox * 2, self.hitbox * 2))
        except:
            print("No ram sprite, circle chaos")
            self.image = None

class PsychoRodent:
    def __init__(self):
        self.riot_coord = [HELL_WIDTH, 717]
        self.hp = 75
        self.dash_speed = 5
        self.hitbox = 40
        self.load_img()

    def load_img(self):
        try:
            self.image = pygame.image.load('labbb-removebg-preview.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.hitbox * 2, self.hitbox * 2))
        except:
            print("No squirrel sprite, circle chaos")
            self.image = None

class Hellspawn:
    def __init__(self):
        self.heat_packed = False
        self.hellspawn_coords = [400, 400]
        self.hitbox = 40
        self.gravity = 0
        self.jump_core = 20
        self.sprint = 7
        self.facing_right = True
        self.hp = 100
        self.hp_max = 100
        self.mag = 5
        self.mag_max = 5
        self.burst_cd = 0
        self.load_images()

    def load_images(self):
        try:
            self.image = pygame.image.load('labubu.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.hitbox * 2, self.hitbox * 2))
            self.image_left = pygame.transform.flip(self.image, True, False)
        except:
            print("No player sprite, draw chaos")
            self.image = None

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.hellspawn_coords[0] -= self.sprint
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.hellspawn_coords[0] += self.sprint
            self.facing_right = True

        self.gravity += 0.8
        self.hellspawn_coords[1] += self.gravity

        self.hellspawn_coords[1] = max(self.hitbox, min(HELL_HEIGHT - 85, self.hellspawn_coords[1]))

        if self.burst_cd > 0:
            self.burst_cd -= 1

    def jump(self):
        if self.hellspawn_coords[1] >= HELL_HEIGHT - 85 - self.hitbox:
            self.gravity = -self.jump_core

    def shoot(self):
        if not self.heat_packed:
            print("Where the piece at?!")
            return None
        if self.mag > 0 and self.burst_cd <= 0:
            self.mag -= 1
            self.burst_cd = 10
            bullet_x = self.hellspawn_coords[0] + (self.hitbox + 30 if self.facing_right else -self.hitbox - 30)
            return {
                'x': bullet_x,
                'y': self.hellspawn_coords[1] - 5,
                'rect': pygame.Rect(bullet_x, self.hellspawn_coords[1] - 5, 50, 20),
                'facing_right': self.facing_right
            }
        return None

    def reload(self):
        self.mag = self.mag_max

    def draw(self, screen):
        if self.image:
            img = self.image if self.facing_right else self.image_left
            screen.blit(img, (self.hellspawn_coords[0] - self.hitbox, self.hellspawn_coords[1] - self.hitbox))
        else:
            pygame.draw.circle(screen, NEON_GREEN, (int(self.hellspawn_coords[0]), int(self.hellspawn_coords[1])), self.hitbox)

class ChaosGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((HELL_WIDTH, HELL_HEIGHT))
        pygame.display.set_caption("Shooting Nana: Hellspawn Edition")
        self.clock = pygame.time.Clock()
        self.state = RiotMode.MENU
        self.player = Hellspawn()
        self.bullets = []
        self.rams = []
        self.last_ram_spawn = 0
        self.ram_spawn_interval = 2000  # 2 seconds
        self.psyrodents = []
        self.last_psyrodent_spawn = 0
        self.psyrodent_spawn_interval = 2000
        self.load_assets()
        self.setup_audio()
        self.fkn_fragz = 0

        self.back_button = pygame.Rect(HELL_WIDTH - 80, 20, 60, 30)  # Petit bouton, en haut à droite
        self.font_back = pygame.font.SysFont("arial", 28)

       
        self.back_button_menu = pygame.Rect(20, 20, 100, 40)
        self.font_back_menu = pygame.font.SysFont("arial", 28)

    def spawn_ram(self):
        ram = RamRaid()
        ram.riot_coord = [HELL_WIDTH + ram.hitbox, 717]
        self.rams.append(ram)
        self.last_ram_spawn = pygame.time.get_ticks()

    def update_rams(self):
        current_time = pygame.time.get_ticks()
        if self.fkn_fragz < 5 and current_time - self.last_ram_spawn > self.ram_spawn_interval:
            self.spawn_ram()
        for ram in self.rams[:]:
            if ram.hp <= 0:
                self.rams.remove(ram)
                self.fkn_fragz += 1
                continue
            ram.riot_coord[0] -= ram.charge_speed
            if ram.riot_coord[0] < -ram.hitbox:
                self.rams.remove(ram)

    def draw_rams(self):
        for ram in self.rams:
            if ram.hp <= 0:
                continue
            if ram.image:
                img = ram.image
                self.screen.blit(img, (ram.riot_coord[0] - ram.hitbox, ram.riot_coord[1] - ram.hitbox))
            else:
                pygame.draw.circle(self.screen, GHOST_WHITE, (int(ram.riot_coord[0]), int(ram.riot_coord[1])), ram.hitbox)

    def spawn_psyrodent(self):
        psyrodent = PsychoRodent()
        psyrodent.riot_coord = [HELL_WIDTH + psyrodent.hitbox, 717]
        self.psyrodents.append(psyrodent)
        self.last_psyrodent_spawn = pygame.time.get_ticks()

    def update_psyrodents(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_psyrodent_spawn > self.psyrodent_spawn_interval:
            self.spawn_psyrodent()
        for psyrodent in self.psyrodents[:]:
            if psyrodent.hp <= 0:
                self.psyrodents.remove(psyrodent)
                continue
            psyrodent.riot_coord[0] -= psyrodent.dash_speed
            if psyrodent.riot_coord[0] < -psyrodent.hitbox:
                self.psyrodents.remove(psyrodent)

    def draw_psyrodents(self):
        for psyrodent in self.psyrodents:
            if psyrodent.hp <= 0:
                continue
            if psyrodent.image:
                img = psyrodent.image
                self.screen.blit(img, (psyrodent.riot_coord[0] - psyrodent.hitbox, psyrodent.riot_coord[1] - psyrodent.hitbox))
            else:
                pygame.draw.circle(self.screen, GHOST_WHITE, (int(psyrodent.riot_coord[0]), int(psyrodent.riot_coord[1])), psyrodent.hitbox)

    def check_collisions_psyrodents(self):
        for psyrodent in self.psyrodents:
            if psyrodent.hp <= 0:
                continue
            dx = self.player.hellspawn_coords[0] - psyrodent.riot_coord[0]
            dy = self.player.hellspawn_coords[1] - psyrodent.riot_coord[1]
            distance = math.sqrt(dx*dx + dy*dy)
            if distance < self.player.hitbox + psyrodent.hitbox:
                self.player.hp -= 2

    def check_collisions(self):
        for ram in self.rams:
            if ram.hp <= 0:
                continue
            dx = self.player.hellspawn_coords[0] - ram.riot_coord[0]
            dy = self.player.hellspawn_coords[1] - ram.riot_coord[1]
            distance = math.sqrt(dx*dx + dy*dy)
            if distance < self.player.hitbox + ram.hitbox:
                self.player.hp -= 1

    def load_assets(self):
        try:
            self.bullet_img = pygame.image.load('pngtree-burning-fire-icon-transparent-vector-png-image_6460035.png').convert_alpha()
            self.bullet_img = pygame.transform.scale(self.bullet_img, (50, 20))
            self.bullet_img_left = pygame.transform.flip(self.bullet_img, True, False)
        except:
            print("No bullet sprite")
            self.bullet_img = None
        try:
            self.gun_img = pygame.image.load('gun.png').convert_alpha()
            self.gun_img = pygame.transform.scale(self.gun_img, (100, 60))
            self.gun_img_left = pygame.transform.flip(self.gun_img, True, False)
        except:
            print("No gun sprite")
            self.gun_img = None
        try:
            self.ground = pygame.transform.scale(pygame.image.load('valentina-saldaneri-nana4.jpg').convert_alpha(), (HELL_WIDTH, HELL_HEIGHT // 2))
            self.sky = pygame.transform.scale(pygame.image.load('valentina-saldaneri-nana4.jpg').convert_alpha(), (HELL_WIDTH, HELL_HEIGHT))
        except:
            print("No background sprites")
            self.ground = None
            self.sky = None

    def setup_audio(self):
        try:
            pygame.mixer.music.load("Jimmy Fontanez - Dub Hub ♫ NO COPYRIGHT 8-bit Music.mp3")
            pygame.mixer.music.set_volume(0.7)
            pygame.mixer.music.play(-1)
            self.gun_toggle_sound = pygame.mixer.Sound("reload.mp3")
            self.gun_toggle_sound.set_volume(1.0)
        except:
            print("No audio files")
            self.gun_toggle_sound = None

    def draw_menu(self):
        self.screen.fill((10, 10, 10))
        title_font = pygame.font.SysFont("impact", 90)
        text_font = pygame.font.SysFont("consolas", 32)
        title = title_font.render("Accoustic game", True, (0, 255, 100))
        self.screen.blit(title, (HELL_WIDTH // 2 - title.get_width() // 2, 80))
        instructions = [
            "← / → : Strafe like a legend",
            "↑ : Gravity-defying leap",
            "X : Ready your weapon",
            "SPACE : Let the bullets fly",
            "R : Reload — stay sharp",
            "P : Pause reality",
            "",
            "If you are accoustic, play "
        ]
        for i, line in enumerate(instructions):
            txt = text_font.render(line, True, (200, 255, 200))
            self.screen.blit(txt, (HELL_WIDTH // 2 - txt.get_width() // 2, 220 + i * 38))
        button_rect = pygame.Rect(HELL_WIDTH // 2 - 130, 600, 260, 65)
        pygame.draw.rect(self.screen, (0, 255, 100), button_rect, border_radius=12)
        pygame.draw.rect(self.screen, (0, 150, 50), button_rect, width=4, border_radius=12)
        btn_text = text_font.render("Let's go ", True, SHADOW_BLACK)
        self.screen.blit(btn_text, (
            button_rect.centerx - btn_text.get_width() // 2,
            button_rect.centery - btn_text.get_height() // 2
        ))
                               
        return button_rect

    def draw_gun(self):
        if self.player.heat_packed:
            if self.player.facing_right:
                gun_x = self.player.hellspawn_coords[0] + self.player.hitbox - 38
                gun_y = self.player.hellspawn_coords[1] - 30
                if self.gun_img:
                    self.screen.blit(self.gun_img, (gun_x, gun_y))
            else:
                gun_x = self.player.hellspawn_coords[0] - self.player.hitbox - 62
                gun_y = self.player.hellspawn_coords[1] - 30
                if self.gun_img:
                    self.screen.blit(self.gun_img_left, (gun_x, gun_y))

    def draw_hud(self):
        font = pygame.font.SysFont(None, 28)
        for i in range(self.player.mag):
            pygame.draw.rect(self.screen, (255, 255, 0), (20 + i * 15, 20, 10, 20))
        ammo_label = font.render("Ammo", True, GHOST_WHITE)
        self.screen.blit(ammo_label, (20, 0))
        gun_status = "READY" if self.player.heat_packed else "HIDDEN"
        status_color = (0, 255, 0) if self.player.heat_packed else (255, 0, 0)
        status_text = font.render(f"Gun: {gun_status}", True, status_color)
        self.screen.blit(status_text, (20, 120))
        health_width = (self.player.hp / self.player.hp_max) * 200
        pygame.draw.rect(self.screen, (255, 0, 0), (20, 50, health_width, 20))
        health_label = font.render("Health", True, GHOST_WHITE)
        self.screen.blit(health_label, (20, 75))
        kills_text = font.render(f"Fragz: {self.fkn_fragz}", True, GHOST_WHITE)
        self.screen.blit(kills_text, (HELL_WIDTH - 200, 20))

    def update_bullets(self):
        for bullet in self.bullets[:]:
            if bullet['facing_right']:
                bullet['x'] += 25
            else:
                bullet['x'] -= 25
            bullet['rect'].x = bullet['x'] 
            if bullet['x'] > HELL_WIDTH or bullet['x'] < 0:
                self.bullets.remove(bullet)
                continue
            for psyrodent in self.psyrodents[:]:
                if psyrodent.hp <= 0:
                    continue
                dx = bullet['x'] - psyrodent.riot_coord[0]
                dy = bullet['y'] - psyrodent.riot_coord[1]
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < psyrodent.hitbox:
                    psyrodent.hp -= 25
                    psyrodent.riot_coord[0] += 155
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if psyrodent.hp <= 0:
                        self.psyrodents.remove(psyrodent)
                    break
            for ram in self.rams[:]:
                if ram.hp <= 0:
                    continue
                dx = bullet['x'] - ram.riot_coord[0]
                dy = bullet['y'] - ram.riot_coord[1]
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < ram.hitbox:
                    ram.hp -= 25
                    ram.riot_coord[0] += 155
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if ram.hp <= 0:
                        self.rams.remove(ram)
                        self.fkn_fragz += 1
                    break

    def draw_bullets(self):
        for bullet in self.bullets:
            if self.bullet_img:
                img = self.bullet_img if bullet['facing_right'] else self.bullet_img_left
                self.screen.blit(img, (bullet['x'], bullet['y']))
            else:
                pygame.draw.rect(self.screen, (255, 0, 0), bullet['rect'])

    def draw_back_button(self):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.back_button.collidepoint(mouse_pos)

        # Couleurs avec transparence
        normal_color = (0, 0, 0, 120)       # fond noir semi-transparent
        hover_color = (255, 255, 255, 160)  # fond blanc semi-transparent
        text_color = (255, 255, 255) if not is_hovered else (0, 0, 0)

        # Créer un bouton transparent
        surface = pygame.Surface((self.back_button.width, self.back_button.height), pygame.SRCALPHA)
        surface.fill(hover_color if is_hovered else normal_color)
        self.screen.blit(surface, (self.back_button.x, self.back_button.y))

        # Texte centré
        back_text = self.font_back.render("Back", True, text_color)
        self.screen.blit(back_text, (
            self.back_button.centerx - back_text.get_width() // 2,
            self.back_button.centery - back_text.get_height() // 2
        ))

    def run(self):
        running = True
        first_ram_spawned = False
        
        while running:
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.state == RiotMode.MENU:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        button_rect = self.draw_menu()
                        if button_rect.collidepoint(event.pos):
                            self.state = RiotMode.CHAOS
                            first_ram_spawned = False
                            self.last_ram_spawn = pygame.time.get_ticks()
                        if self.back_button_menu.collidepoint(event.pos):
                            return "back"  # Retour à l'écran principal

                elif self.state == RiotMode.CHAOS:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.back_button.collidepoint(event.pos):
                            
                            self.state = RiotMode.MENU
                            self.player = Hellspawn()
                            self.bullets.clear()
                            self.rams.clear()
                            self.psyrodents.clear()
                            self.fkn_fragz = 0

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                            pass  # Movement handled in update
                        if event.key == pygame.K_UP:
                            self.player.jump()
                        if event.key == pygame.K_x:
                            self.player.heat_packed = True
                            if self.gun_toggle_sound:
                                self.gun_toggle_sound.play()
                        if event.key == pygame.K_r:
                            self.player.reload()
                        if event.key == pygame.K_SPACE:
                            bullet = self.player.shoot()
                            if bullet:
                                self.bullets.append(bullet)
                        if event.key == pygame.K_p:
                            self.state = RiotMode.FROZEN
                
                elif self.state == RiotMode.FROZEN:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                        self.state = RiotMode.CHAOS

            keys = pygame.key.get_pressed()
            if self.state == RiotMode.CHAOS:
                self.player.update(keys)
                self.update_rams()
                self.update_psyrodents()
                self.check_collisions()
                self.check_collisions_psyrodents()
                self.update_bullets()
                if self.player.hp <= 0:
                    self.state = RiotMode.DEAD
            
            # Draw everything
            if self.sky:
                self.screen.blit(self.sky, (0, 0))
            else:
                self.screen.fill((0, 0, 0))

            if self.state == RiotMode.MENU:
                self.draw_menu()
               
                pygame.draw.rect(self.screen, (100, 100, 100), self.back_button_menu, border_radius=8)
                back_text = self.font_back_menu.render("Back", True, (255, 255, 255))
                self.screen.blit(back_text, (self.back_button_menu.centerx - back_text.get_width() // 2,
                                            self.back_button_menu.centery - back_text.get_height() // 2))

            elif self.state == RiotMode.CHAOS:
                if self.ground:
                    self.screen.blit(self.ground, (0, HELL_HEIGHT // 2))
                else:
                    pygame.draw.rect(self.screen, (40, 40, 40), (0, HELL_HEIGHT // 2, HELL_WIDTH, HELL_HEIGHT // 2))
                self.draw_rams()
                self.draw_psyrodents()
                self.player.draw(self.screen)
                self.draw_bullets()
                self.draw_gun()
                self.draw_hud()
                self.draw_back_button()  # Petit bouton "Back" en jeu

            elif self.state == RiotMode.DEAD:
                self.screen.fill((255, 0, 0))
                font_dead = pygame.font.SysFont("impact", 72)
                dead_text = font_dead.render("YOU DIED", True, (255, 255, 255))
                self.screen.blit(dead_text, (HELL_WIDTH // 2 - dead_text.get_width() // 2, HELL_HEIGHT // 2))
                pygame.display.flip()
                time.sleep(3)
                running = False
                return "back"  # Retour accueil après mort

            elif self.state == RiotMode.FROZEN:
                pause_font = pygame.font.SysFont("impact", 64)
                pause_text = pause_font.render("PAUSED - Press P to resume", True, (255, 255, 255))
                self.screen.blit(pause_text, (HELL_WIDTH // 2 - pause_text.get_width() // 2, HELL_HEIGHT // 2))

            pygame.display.flip()
            self.clock.tick(FPS)

def chaos_dropkick():
    game = ChaosGame()
    return game.run()
