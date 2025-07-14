import pygame
import math
import random
from openai import OpenAI
from accoustic_game import chaos_dropkick
from dotenv import load_dotenv
import os


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print(api_key)  # Use this key securely in your client


def play_music(path):
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("Erreur lecture musique:", e)


pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chibi Anime with Game & Interaction")

clock = pygame.time.Clock()
FPS = 60

# Charger musique (optionnel, adapte le chemin)
try:
    pygame.mixer.music.load("Rick Astley - Never Gonna Give You Up (Official Music Video).mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except Exception as e:
    print("Erreur chargement musique:", e)

def scaled(val):
    return int(val * 0.75)

# Images (met les tiens dans le même dossier)
hehe_img = pygame.transform.scale(pygame.image.load("hehe.png").convert_alpha(), (scaled(120), scaled(120)))
surprized_img = pygame.transform.scale(pygame.image.load("surprized.png").convert_alpha(), (scaled(120), scaled(120)))
lol_img = pygame.transform.scale(pygame.image.load("lol.png").convert_alpha(), (scaled(120), scaled(120)))

character_imgs = {
    "happy": pygame.transform.scale(pygame.image.load("happy.png").convert_alpha(), (scaled(160), scaled(160))),
    "sad": pygame.transform.scale(pygame.image.load("sad.png").convert_alpha(), (scaled(160), scaled(160))),
    "angry": pygame.transform.scale(pygame.image.load("angry.png").convert_alpha(), (scaled(160), scaled(160))),
}

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
    
)

# Couleurs, polices...
BG_COLOR = (230, 245, 230)
GRASS_GREEN = (80, 150, 60)
FLOWER_PINK = (255, 160, 190)
SUN_YELLOW = (255, 230, 100)
CLOUD_WHITE = (245, 245, 255)

font = pygame.font.SysFont("comicsansms", 32)
font_input = pygame.font.SysFont("arial", 24)

chat_lines = [
    "Hi! Where are you?",
    "Why not chat with me?",
    "I'm here waiting~",
    "Tell me something!",
    "You look nice today 😊",
]

shy_lines = [
    "Oh, you’re writing?",
    "You’re talking to me?",
    "I’m a little shy...",
    "Eek! Don’t stare too long!",
]

angry_lines = [
    "Hey! Are you ignoring me?! 😠",
    "I'm getting mad here!",
    "Don't leave me hanging!",
]

BLINK_DURATION = 10

# Variables d’état du chat
is_hover = False
is_shy = False
shy_timer = 0
shy_duration = FPS * 4

dance_mode = 0
dance_timer = 0
dance_switch_time = FPS * 4

input_active = True
user_text = ""
response_text = ""
response_timer = 0
response_duration = FPS * 5

last_interaction_time = 0
ANGRY_THRESHOLD = FPS * 3
is_angry = False

angry_text_index = 0
angry_text_timer = 0
ANGRY_SPEECH_INTERVAL = FPS * 4

chat_history = [{"role": "system", "content": "You are a friendly, cute chibi anime character who chats with the user."}]

EXTRA_HEADERS = {
    "HTTP-Referer": "http://localhost",
    "X-Title": "Cute Chibi Game"
}

PHASES = [
    {"img": hehe_img, "text": "You have been hacked! ENJOY", "duration": 6 * FPS},
    {"img": surprized_img, "text": "Oh wait, just kidding! C'mon~", "duration": 3 * FPS},
    {"img": lol_img, "text": "Wanna play or chat? ", "duration": None},
]


def get_openai_response(user_message):
    global chat_history
    chat_history.append({"role": "user", "content": user_message})
    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=chat_history,
            extra_headers=EXTRA_HEADERS,
            extra_body={}
        )
        assistant_msg = completion.choices[0].message.content.strip()
        chat_history.append({"role": "assistant", "content": assistant_msg})
        return assistant_msg
    except Exception as e:
        print("OpenRouter API error:", e)
        return "Oops! Something went wrong. Maybe no credits or rate limit hit?"
    

def draw_speech_bubble(surface, text, pos):
    padding = 10
    font_surface = font_input.render(text, True, (40, 40, 40))
    w, h = font_surface.get_size()
    rect = pygame.Rect(pos[0], pos[1], w + 2 * padding, h + 2 * padding)
    pygame.draw.rect(surface, (255, 255, 255), rect, border_radius=10)
    pygame.draw.rect(surface, (180, 180, 180), rect, width=2, border_radius=10)
    surface.blit(font_surface, (pos[0] + padding, pos[1] + padding))
    pointer = [(pos[0] + rect.width // 2 - 10, pos[1] + rect.height),
               (pos[0] + rect.width // 2 + 10, pos[1] + rect.height),
               (pos[0] + rect.width // 2, pos[1] + rect.height + 10)]
    pygame.draw.polygon(surface, (255, 255, 255), pointer)
    pygame.draw.polygon(surface, (180, 180, 180), pointer, 2)

def draw_input_box(surface, rect, text, active):
    color_inactive = (150, 150, 150)
    color_active = (80, 120, 200)
    color = color_active if active else color_inactive
    pygame.draw.rect(surface, (255, 255, 255), rect, border_radius=8)
    pygame.draw.rect(surface, color, rect, 3, border_radius=8)
    txt_surface = font_input.render(text, True, (0, 0, 0))
    surface.blit(txt_surface, (rect.x + 10, rect.y + (rect.height - txt_surface.get_height()) // 2))

def draw_background():
    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT - scaled(100), WIDTH, scaled(100)))
    for i in range(15):
        x = i * 50 + 20
        y = HEIGHT - scaled(100) + random.randint(scaled(20), scaled(60))
        pygame.draw.circle(screen, FLOWER_PINK, (x, y), scaled(7))
        pygame.draw.circle(screen, (255, 255, 255), (x, y), scaled(3))
    pygame.draw.circle(screen, SUN_YELLOW, (WIDTH - scaled(80), scaled(80)), scaled(50))
    for i in range(6):
        angle = i * math.pi / 3 + pygame.time.get_ticks() * 0.002
        x1 = WIDTH - scaled(80) + math.cos(angle) * scaled(60)
        y1 = scaled(80) + math.sin(angle) * scaled(60)
        pygame.draw.line(screen, SUN_YELLOW, (WIDTH - scaled(80), scaled(80)), (x1, y1), 5)
    cloud_x = (pygame.time.get_ticks() // 5) % (WIDTH + scaled(200)) - scaled(200)
    pygame.draw.ellipse(screen, CLOUD_WHITE, (cloud_x, scaled(50), scaled(120), scaled(50)))
    pygame.draw.ellipse(screen, CLOUD_WHITE, (cloud_x + scaled(40), scaled(30), scaled(120), scaled(60)))
    pygame.draw.ellipse(screen, CLOUD_WHITE, (cloud_x + scaled(80), scaled(50), scaled(120), scaled(50)))

def draw_accueil_background():
    screen.fill((255, 228, 225))
    heart_color = (255, 105, 180)
    for _ in range(30):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        pygame.draw.circle(screen, heart_color, (x, y), 5)
        pygame.draw.circle(screen, (255, 182, 193), (x + 2, y - 2), 3)

def draw_text_with_shadow(surface, text, font, pos, main_color, shadow_color, offset=(2, 2)):
    shadow_surf = font.render(text, True, shadow_color)
    surface.blit(shadow_surf, (pos[0] + offset[0], pos[1] + offset[1]))
    text_surf = font.render(text, True, main_color)
    surface.blit(text_surf, pos)

def accueil_screen():
    stage = 0
    timer = 0
    running = True

    BUTTON_PINK = (255, 105, 180)
    play_button = pygame.Rect(WIDTH // 2 - 110, HEIGHT - 350, 220, 60)  # Légèrement plus haut
    chat_button = pygame.Rect(WIDTH // 2 - 110, HEIGHT - 250, 220, 60)  # Légèrement plus bas

    while running:
        
        clock.tick(FPS)
        draw_accueil_background()

        current_phase = PHASES[stage]
        img = current_phase["img"]
        img_pos = (WIDTH // 2 - img.get_width() // 2, HEIGHT // 2 - img.get_height() // 2 - 100)  # Remonté
        screen.blit(img, img_pos)

        # Affichage du texte en dessous de l’image
        lines = current_phase["text"].split('\n')
        for i, line in enumerate(lines):
            text_pos = (WIDTH // 2 - font.size(line)[0] // 2, img_pos[1] + img.get_height() + 10 + i * 40)
            draw_text_with_shadow(screen, line, font, text_pos, (255, 105, 180), (150, 50, 100))

        # Bouton PLAY
        pygame.draw.rect(screen, BUTTON_PINK, play_button, border_radius=10)
        text_play = font.render("PLAY", True, (255, 255, 255))
        screen.blit(text_play, (play_button.centerx - text_play.get_width() // 2,
                                play_button.centery - text_play.get_height() // 2))

        # Bouton CHAT
        pygame.draw.rect(screen, BUTTON_PINK, chat_button, border_radius=10)
        text_chat = font.render("CHAT", True, (255, 255, 255))
        screen.blit(text_chat, (chat_button.centerx - text_chat.get_width() // 2,
                                chat_button.centery - text_chat.get_height() // 2))

        # Gestion des phases
        if current_phase["duration"] is not None:
            timer += 1
            if timer >= current_phase["duration"]:
                stage += 1
                timer = 0
                if stage >= len(PHASES):
                    stage = len(PHASES) - 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    return "play"
                elif chat_button.collidepoint(event.pos):
                    return "chat"

        pygame.display.flip()



def zelda_game():
    back_button = pygame.Rect(20, 20, 100, 40)
    font_back = pygame.font.SysFont("arial", 28)
    running = True

    while running:
        clock.tick(FPS)
        screen.fill((30, 30, 60))

        pygame.draw.rect(screen, (200, 0, 0), back_button, border_radius=8)
        back_text = font_back.render("Back", True, (255, 255, 255))
        screen.blit(back_text, (back_button.centerx - back_text.get_width() // 2,
                                back_button.centery - back_text.get_height() // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    running = False

        pygame.display.flip()

def main():
    global is_hover, is_shy, shy_timer, dance_mode, dance_timer
    global input_active, user_text, response_text, response_timer, last_interaction_time, is_angry
    global angry_text_index, angry_text_timer

    running = True
    back_button = pygame.Rect(20, 20, 100, 40)
    font_back = pygame.font.SysFont("arial", 28)

    player_pos = [WIDTH // 2, HEIGHT - scaled(180)]

    blink_time = 0
    is_blinking = False

    wave_frame = 0
    chat_index = 0
    chat_timer = 0
    CHAT_DISPLAY_TIME = FPS * 5

    shy_text_index = 0
    input_box = pygame.Rect(20, HEIGHT - 50, WIDTH - 40, 35)

    while running:
        dt = clock.tick(FPS)
        draw_background()
        pygame.draw.rect(screen, (200, 0, 0), back_button, border_radius=8)
        back_text = font_back.render("Back", True, (255, 255, 255))
        screen.blit(back_text, (back_button.centerx - back_text.get_width() // 2,
                                back_button.centery - back_text.get_height() // 2))

        mx, my = pygame.mouse.get_pos()
        head_rect = pygame.Rect(player_pos[0] - scaled(80), player_pos[1] - scaled(150), scaled(160), scaled(160))
        is_hover = head_rect.collidepoint(mx, my)

        blink_time += 1
        if blink_time > 400:
            is_blinking = True
        if is_blinking and blink_time > 400 + BLINK_DURATION:
            is_blinking = False
            blink_time = 0

        if is_shy:
            shy_timer += 1
            if shy_timer > shy_duration:
                is_shy = False
                shy_timer = 0

        dance_timer += 1
        if dance_timer > dance_switch_time:
            dance_mode = (dance_mode + 1) % 4
            dance_timer = 0

        last_interaction_time += 1
        if last_interaction_time > ANGRY_THRESHOLD:
            is_angry = True
        else:
            is_angry = False

        if is_angry:
            angry_text_timer += 1
            if angry_text_timer > ANGRY_SPEECH_INTERVAL:
                angry_text_index = (angry_text_index + 1) % len(angry_lines)
                angry_text_timer = 0

        jump_offset = 0
        if dance_mode == 3:
            jump_offset = int(20 * abs(math.sin(pygame.time.get_ticks() * 0.02)))

        if is_angry:
            current_img = character_imgs["angry"]
        elif is_shy:
            current_img = character_imgs["sad"]
        else:
            current_img = character_imgs["happy"]

        screen.blit(current_img, (player_pos[0] - current_img.get_width() // 2, player_pos[1] - jump_offset - current_img.get_height() // 2))

        wave_frame += 1

        if response_text:
            response_timer += 1
            draw_speech_bubble(screen, response_text, (player_pos[0] - 140, player_pos[1] - scaled(220)))
            if response_timer > response_duration:
                response_text = ""
                response_timer = 0
        elif is_shy:
            shy_line = shy_lines[shy_text_index % len(shy_lines)]
            draw_speech_bubble(screen, shy_line, (player_pos[0] - 140, player_pos[1] - scaled(220)))
        elif is_angry:
            angry_line = angry_lines[angry_text_index % len(angry_lines)]
            draw_speech_bubble(screen, angry_line, (player_pos[0] - 140, player_pos[1] - scaled(220)))
        else:
            chat_timer += 1
            if chat_timer > CHAT_DISPLAY_TIME:
                chat_index = (chat_index + 1) % len(chat_lines)
                chat_timer = 0
            draw_speech_bubble(screen, chat_lines[chat_index], (player_pos[0] - 140, player_pos[1] - scaled(220)))

        draw_input_box(screen, input_box, user_text, input_active)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False
                last_interaction_time = 0

            elif event.type == pygame.KEYDOWN and input_active:
                last_interaction_time = 0
                if event.key == pygame.K_RETURN:
                    if user_text.strip() != "":
                        response_text = get_openai_response(user_text)
                        response_timer = 0
                        is_shy = False
                        shy_timer = 0
                        dance_mode = 0

                        text_lower = user_text.lower()
                        if "angry" in text_lower or "mad" in text_lower:
                            is_angry = True
                            is_shy = False
                        elif "sad" in text_lower or "shy" in text_lower:
                            is_shy = True
                            is_angry = False
                        else:
                            is_angry = False
                            is_shy = False

                        user_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    if len(user_text) < 60:
                        user_text += event.unicode

            if event.type == pygame.MOUSEMOTION:
                if is_hover and not is_shy:
                    is_shy = True
                    shy_timer = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                 if back_button.collidepoint(event.pos):
                      return

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    while True:
        play_music("Rick Astley - Never Gonna Give You Up (Official Music Video).mp3")  
        action = accueil_screen()
        
        if action == "play":
            retour = chaos_dropkick()
            if retour == "back":
                continue  
                
        elif action == "chat":
            play_music("Violet Evergarden OST Automemories ~ Relaxing Anime Music.mp3") 
            main()  
