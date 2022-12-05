# Import --------------------------------------------------------- #
try:
        import pygame, random, sys, os, json
        from pygame.locals import *
        import data.scripts.core_funcs as core_funcs
        import data.scripts.text as text
        import data.scripts.shaders as shaders
        from data.scripts.entities import PhysicsObject
        from data.scripts.maze import Maze
# Error verification import -------------------------------------- #
except ImportError as err:
        print("Unable to load module : %s" % (err))
        sys.exit()
# Version -------------------------------------------------------- #
version = '1.0'
# Setup pygame/window -------------------------------------------- #
pygame.init()
# Define clock time (FPS)
mainClock = pygame.time.Clock()
# Open a new window
display_size = [384, 216]
pygame.display.set_caption("Game monkepo v" + version)
info = pygame.display.Info() # Allows you to retrieve the dimensions of the user's screen
display_fullscreen = [info.current_w, info.current_h]
# Video Functions ------------------------------------------------ #
def load_video_settings():
    """
    # Cette fonction (load_video_settings) permet de charger les paramètres video
    :return : data[1]
    :rtype : str
    """
    global scale
    file = open('data/settings/video_settings.txt', 'r')
    data = file.read()
    scale = int(data[0])
    file.close()
    return data[1]
def save_video_settings():
    """
    # Cette fonction (save_video_settings) permet de sauvegarder les paramètres video
    """
    global scale
    file = open('data/settings/video_settings.txt', 'w')
    file.write(str(scale) + fullscreened)
    file.close()
# Video setting -------------------------------------------------- #
global screen
fullscreened = load_video_settings()
if fullscreened == 'n':
    screen = pygame.display.set_mode((display_size[0] * scale, display_size[1] * scale), 0, 32)
else:
    scale = int(display_fullscreen[0] // 384)
    screen = pygame.display.set_mode((display_size[0] * scale, display_size[1] * scale), pygame.FULLSCREEN)
display = pygame.Surface(display_size)
# Load controls function ----------------------------------------- #
def load_controls():
    """
    # Cette fonction (load_controls) permet de charger les controls par défaut ou du joueur
    """
    global up_key, down_key, left_key, right_key, select_key, c_scheme
    file = open('data/settings/controls_save.txt', 'r')
    data = file.read()
    file.close()
    control_data = data.split('\n')[0]
    if control_data == 'default':
        c_scheme = 'default'
    else:
        c_scheme = 'custom'
        n = 0
        for val in control_data.split(';'):
            if n == 0:
                up_key = int(val)
            if n == 1:
                down_key = int(val)
            if n == 2:
                left_key = int(val)
            if n == 3:
                right_key = int(val)
            if n == 4:
                select_key = int(val)
            n += 1
# Save controls function ----------------------------------------- #
def save_controls():
    """
    # Cette fonction (save_controls) permet de sauvegarder les controls du joueur
    """
    global up_key, down_key, right_key, left_key, select_key, c_scheme
    file = open('data/settings/controls_save.txt','r')
    data = file.read()
    file.close()
    data = data.split('\n')
    file = open('data/settings/controls_save.txt','w')
    out_str = str(up_key) + ';' + str(down_key) + ';' + str(left_key) + ';' + str(right_key) + ';' + str(select_key) + '\n' + data[1]
    file.write(out_str)
    file.close()
# Keys Settings -------------------------------------------------- #
global up_key, down_key, left_key, right_key, select_key
up_key = K_UP
down_key = K_DOWN
left_key = K_LEFT
right_key = K_RIGHT
select_key = K_RETURN
# Image function ------------------------------------------------- #
def load_img(path):
    """
    # Cette fonction (load_img) permet de charger une image
    :param : path
    :type_param : string
    :return : img
    :rtype : surface
    """
    img = pygame.image.load("data/images/" + path + ".png").convert()
    img.set_colorkey((255,255,255))
    return img
# Load image ----------------------------------------------------- #
opening_img = load_img('opening')
menu_bg = load_img('menu_bg')
options_bar = load_img('options_bar')
wide_bar = load_img('wide_bar')
camera_img = load_img('camera')
loading_img = load_img('loading')
# Load tiles ----------------------------------------------------- #
decor_list = ['skull_0.png','skull_1.png','spawn.png','finish.png']
tile_database = {}
tile_list = os.listdir('data/images/tiles')
not_valid = ['tilesets']
tall_tiles =  [('rocks','0011.png'),('rocks','0110.png'),('rocks','0111.png'),('rocks','0100.png'),('rocks','0101.png'),('rocks','0001.png'),('rocks','corner_0110.png'),('rocks','corner_0011.png'),('rocks','corner_0111.1.png'),('rocks','corner_0111.2.png'),('rocks','corner_0111.png')]
for tile in tile_list:
    if tile not in not_valid:
        img = pygame.image.load('data/images/tiles/' + tile).convert()
        img.set_colorkey((255,255,255))
        tile_database[tile] = img.copy()
tile_list = os.listdir('data/images/tiles/tilesets')
for tile in tile_list:
    if tile not in not_valid:
        img = pygame.image.load('data/images/tiles/tilesets/' + tile).convert()
        img.set_colorkey((255,255,255))
        tile_database[tile] = img.copy()
# Light img ------------------------------------------------------ #
light_img = pygame.image.load('data/images/light_2.png').convert()
light_img_2 = shaders.change_light_color(light_img.copy(),(99,90,124))
light_img = shaders.change_light_color(light_img,(169,162,187))
# Load map ------------------------------------------------------- #
def load_map(name):
    """
    Cette fonction (load_map) permet de charger une map via un path mis en paramètre
    :param : path du fichier
    :type_param : string
    :return : tile_map
    :rtype : dict
    """
    file = open('data/maps/' + name + '.json', 'r')
    data = file.read()
    file.close()
    json_data = json.loads(data)
    tile_map = json_data['tile_map']
    maze_solver = json_data['maze_solver']
    end_position = json_data['end_maze']
    spawn = [0, -1]
    # left, top, right, bottom
    edges = [99999,99999,-99999,-99999]
    return tile_map, spawn, maze_solver, end_position
tile_map, spawn, maze_solver, end_position = load_map('maze')
solver_list = []
for key, value in maze_solver.items():
    temp = [key,value]
    solver_list.append(temp)
xmc, ymc = 21, 21
# Text width Functions ------------------------------------------- #
def get_text_width(text, spacing):
    """
    # Cette fonction (get_text_width) permet d'avoir la taille d'une chaine de
    # caractère entrer en paramètre
    :param : text
    :param : spacing
    :type_param : str
    :type_param : int
    :return : img
    :rtype : surface
    """
    global font_data
    width = 0
    for char in text:
        if char in font_data:
            width += font_data[char][0] + spacing
        elif char == ' ':
            width += font_data['A'][0] + spacing
    return width
# outlined_text function ----------------------------------------- #
def outlined_text(bg_font, fg_font, text, surf, pos):
    bg_font.render(text, surf, [pos[0] - 1, pos[1]])
    bg_font.render(text, surf, [pos[0] + 1, pos[1]])
    bg_font.render(text, surf, [pos[0], pos[1] - 1])
    bg_font.render(text, surf, [pos[0], pos[1] + 1])
    fg_font.render(text, surf, [pos[0], pos[1]])
# Data Font ------------------------------------------------------ #
global font_data
font_data = {'A':[3],'B':[3],'C':[3],'D':[3],'E':[3],'F':[3],'G':[3],'H':[3],'I':[3],'J':[3],'K':[3],'L':[3],'M':[5],'N':[3],'O':[3],'P':[3],'Q':[3],'R':[3],'S':[3],'T':[3],'U':[3],'V':[3],'W':[5],'X':[3],'Y':[3],'Z':[3],
            'a':[3],'b':[3],'c':[3],'d':[3],'e':[3],'f':[3],'g':[3],'h':[3],'i':[1],'j':[2],'k':[3],'l':[3],'m':[5],'n':[3],'o':[3],'p':[3],'q':[3],'r':[2],'s':[3],'t':[3],'u':[3],'v':[3],'w':[5],'x':[3],'y':[3],'z':[3],
            '.':[1],'-':[3],',':[2],':':[1],'+':[3],'\'':[1],'!':[1],'?':[3],
            '0':[3],'1':[3],'2':[3],'3':[3],'4':[3],'5':[3],'6':[3],'7':[3],'8':[3],'9':[3],
            '(':[2],')':[2],'/':[3],'_':[5],'=':[3],'\\':[3],'[':[2],']':[2],'*':[3],'"':[3],'<':[3],'>':[3],';':[1]}
# Load Font ------------------------------------------------------ #
main_font = text.Font('data/fonts/small_font.png', (168, 217, 227))
bg_font = text.Font('data/fonts/small_font.png', (28, 17, 24))
global font
font = text.generate_font('data/fonts/small_font0.png', font_data, 5, 8, (248, 248, 248))
font_2 = text.generate_font('data/fonts/small_font0.png', font_data, 5, 8, (111, 70, 60))
font_3 = text.generate_font('data/fonts/small_font0.png', font_data, 5, 8,(16, 30, 41))
font_error = text.generate_font('data/fonts/small_font0.png', font_data, 5, 8,(190, 40, 40))
# Load music ----------------------------------------------------- #
def is_int(s):
    val = True
    try:
        s = int(s)
    except:
        val = False
    return val
# Load sound function -------------------------------------------- #
def load_sound(path):
    """
    # Cette fonction (load_sound) permet de charger dans un dictionnaire toutes les musics d'un dossier
    :param : path
    :typpe_param : string
    :return : sound_database
    :rtype : dict
    """
    sound_list = os.listdir(path)
    sound_database = {}
    for sound in sound_list:
        sound_database[sound.split('.')[0]] = pygame.mixer.Sound(path + sound)
    return sound_database
# Play sound function -------------------------------------------- #
def play_sound(sound_id):
    """
    # Cette fonction (play_sound) permet de lancer la musique choisie en paramètre
    :param : sound_id
    :typpe_param : string
    """
    global sound_database
    sound = sound_database[sound_id]
    if type(sound) == type([]):
        random.choice(sound).play()
    else:
        sound.play()
# Group sfx function --------------------------------------------- #
def group_sfx(sfx_database):
    groups = {}
    for sound in sfx_database:
        if is_int(sound.split('_')[-1]):
            base = sound.split('_')[:-1]
            base = '_'.join(base)
            if base not in groups:
                groups[base] = [sfx_database[sound]]
            else:
                groups[base].append(sfx_database[sound])
    for group in groups:
        sfx_database[group] = groups[group]
    return sfx_database
global sound_database
sound_database = load_sound("data/sounds/")
sound_database['menu_move'].set_volume(0.4)
sound_database['menu_select'].set_volume(0.4)
sound_database = group_sfx(sound_database)
# Fade screen ---------------------------------------------------- #
global fade_state
fade_state = 0
def fade(surf, direction):
    global fade_state
    surf = surf.copy()
    fade = 0
    while fade < 20:
        fade += 1
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        screen.blit(surf, (0, 0))
        black_surf = surf.copy()
        black_surf.fill(BG)
        if direction == 1:
            black_surf.set_alpha(int(255 / 20 * fade))
        else:
            black_surf.set_alpha(int(255 - 255 / 20 * fade))
        # Screen display ----------------------------------------- #
        screen.blit(black_surf, (0, 0))
        # Update ------------------------------------------------- #
        pygame.display.update()
        # --- Limit to 60 frames per second (FPS)
        mainClock.tick(60)
    fade_state = 20
def fade_in(surf):
    global fade_state
    if fade_state > 0:
        fade_state -= 1
        black_surf = surf.copy()
        black_surf.fill((62, 55, 86))
        black_surf.set_alpha(int(255 / 20 * fade_state))
        surf.blit(black_surf, (0, 0))
# Local Variables ------------------------------------------------ #
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BG = (31,24,48)
running = True
# Data ----------------------------------------------------------- #
global framerate, entity_database
framerate = 60
entity_database = { # x, y, offset_x, offset_y
        'alien' : []
    }
# Class Clock ---------------------------------------------------- #
class Clock(object):
    pass
# Opening function ----------------------------------------------- #
def opening():
    global display_size, fullscreened
    timer = 0
    while timer < 227:
        timer += 1
        # Background/Screen display ------------------------------ #
        display.fill(BG)
        menu_bg.set_alpha(min(timer, 100))
        display.blit(menu_bg, (0,0))
        opening_img.set_alpha(max(0, min((timer - 100) * 5, 255)))
        display.blit(opening_img, (70, 100))
        # Timer -------------------------------------------------- #
        if timer > 220:
            white_surf = pygame.Surface(display_size)
            white_surf.fill(WHITE)
            white_surf.set_alpha(min((timer - 220) * 40, 255))
            display.blit(white_surf, (0,0))
        # Buttons ------------------------------------------------ #
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        # Screen display ----------------------------------------- #
        if fullscreened == 'y':
            screen.blit(pygame.transform.scale(display, (display_fullscreen)), (0,0))
        else:
            screen.blit(pygame.transform.scale(display, (display_size[0] * scale, display_size[1] * scale)), (0,0))
        fade_in(screen)
        # Update ------------------------------------------------- #
        pygame.display.update()
        # --- Limit to 60 frames per second (FPS)
        mainClock.tick(60)
# Simple menu function ------------------------------------------- #
def simple_menu(menu_id):
    global up_key, down_key, left_key, right_key, select_key, menu_title, menu_options, key_order
    global display_size, screen, scale, fullscreened
    wide = False
    setting_controller = 0
    setting_key = 0
    current_selection = 0
    running = True
    timer = 0
    # Menu id ---------------------------------------------------- #
    if menu_id == 'options':
        menu_options = ['Video', 'Keyboard', 'Game settings', 'Back']
        menu_title = 'Options'
    if menu_id == 'video':
        menu_options = ['384x216', '768x432', '1152x648', '1536x684', '1920x1080', 'Apply Fullscreen', 'Back']
        menu_title = 'Video'
    if menu_id == 'keyboard':
        menu_options = ['Up: ', 'Down: ', 'Left: ', 'Right: ', 'Select: ', 'Back']
        menu_title = 'Keyboard Settings'
        wide = True
        key_order = [up_key, down_key, left_key, right_key, select_key]
    if menu_id == 'game settings':
        menu_options = ['Back']
        menu_title = 'Game settings'
    # Loop ------------------------------------------------------- #
    while running:
        # Background --------------------------------------------- #
        display.fill(BG)
        display.blit(menu_bg, (0,0))
        wide_bar_img = wide_bar.copy()
        display.blit(wide_bar_img, (138,24))
        text.show_text(menu_title, int((display_size[0] - get_text_width(menu_title, 1)) / 2), 28, 1, 999, font, display)
        # Menu options ------------------------------------------- #
        if menu_id == 'video' or 'keyboard':
            y = 0
            for option in menu_options:
                options_bar_img = options_bar.copy()
                if y == current_selection:
                    options_bar_img = core_funcs.swap_color(options_bar_img, (46,31,60), (99,90,124))
                display.blit(options_bar_img,(150, 60 + y * 20))
                ending =''
                if menu_id == 'keyboard':
                    if y <= 4:
                        ending = pygame.key.name(key_order[y])
                    if (setting_key == 1) and (current_selection == y):
                        ending = 'press a key'
                text.show_text(option + ending, 155, 64 + y * 20, 1, 999, font, display)
                if menu_id == 'video':
                    text.show_text('If you change the video settings, this can cause lot of lag', 80, 45, 1, 999, font_error, display)
                if menu_id == 'game settings':
                    pass
                y += 1
        else:
            x = 0
            for option in menu_options:
                options_bar_img = options_bar.copy()
                if wide:
                    options_bar_img = wide_bar.copy()
                if x == current_selection:
                    options_bar_img = core_funcs.swap_color(options_bar_img, (46,31,60), (99,90,124))
                display.blit(options_bar_img, (150, 80 + x * 25))
                text.show_text(option, 155, 84 + x * 25, 1, 999, font, display)
                x += 1
        # Pressed boolean ---------------------------------------- #
        pressed_select = False
        pressed_up = False
        pressed_down = False
        # Buttons ------------------------------------------------ #
        if setting_key == 0:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == up_key:
                        pressed_up = True
                    if event.key == down_key:
                        pressed_down = True
                    if event.key == left_key:
                        pressed_left = True
                    if event.key == right_key:
                        pressed_right = True
                    if event.key == select_key:
                        pressed_select = True
        if setting_key == 0:
            n = 0
            if pressed_select:
                play_sound('menu_select')
                option_select = menu_options[current_selection]
                if menu_id == 'options':
                    if option_select == 'Video':
                        fade(screen, 1)
                        simple_menu('video')
                    if option_select == 'Keyboard':
                        fade(screen, 1)
                        simple_menu('keyboard')
                    if option_select == 'Game settings':
                        fade(screen, 1)
                        simple_menu('game settings')
                    if option_select == 'Back':
                        running = False
                if menu_id == 'video':
                    if option_select == 'Back':
                        running = False
                    elif option_select == 'Apply Fullscreen':
                        fade(screen, 1)
                        fullscreened = 'y'
                        screen = pygame.display.set_mode((display_fullscreen),pygame.FULLSCREEN)
                    else:
                        fade(screen, 1)
                        fullscreened = 'n'
                        scale = current_selection + 1
                        screen = pygame.display.set_mode((display_size[0] * scale, display_size[1] * scale),0, 32)
                    save_video_settings()
                if menu_id == 'keyboard':
                    if option_select == 'Back':
                        running = False
                    else:
                        setting_key = 1

                if menu_id == 'game settings':
                    if option_select == 'Back':
                        running = False
            # Pressed up ----------------------------------------- #
            if pressed_up:
                play_sound('menu_move')
                current_selection -= 1
                if current_selection < 0:
                    current_selection = len(menu_options) - 1
            # Pressed down --------------------------------------- #
            if pressed_down:
                play_sound('menu_move')
                current_selection += 1
                if current_selection >= len(menu_options):
                    current_selection = 0
        else:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    setting_key = 0
                    if event.key not in key_order:
                        if current_selection == 0:
                            up_key = event.key
                        if current_selection == 1:
                            down_key = event.key
                        if current_selection == 2:
                            left_key = event.key
                        if current_selection == 3:
                            right_key = event.key
                        if current_selection == 4:
                            select_key = event.key
                    key_order = [up_key, down_key, left_key, right_key, select_key]
                    save_controls()
        # Screen/Display ----------------------------------------- #
        if fullscreened == 'y':
            screen.blit(pygame.transform.scale(display, (display_fullscreen)), (0, 0))
        else:
            screen.blit(pygame.transform.scale(display, (display_size[0] * scale, display_size[1] * scale)), (0, 0))
        fade_in(screen)
        # Update ------------------------------------------------- #
        pygame.display.update()
        # --- Limit to 60 frames per second (FPS)
        mainClock.tick(60) #FPS
    fade(screen, 1)
# Menu function -------------------------------------------------- #
def menu_run():
    global up_key, dow_key, right_key, left_key, select_key
    global running, dipslay_size, fullscreened
    menu_layout = ['Play', 'Options', 'Quit']
    selection = 0
    white_timer = 70
    # Loop ------------------------------------------------------- #
    while running:
        # Background --------------------------------------------- #
        display.fill(BG)
        display.blit(menu_bg, (0,0))
        # Locals variables --------------------------------------- #
        pressed_select = False
        pressed_up = False
        pressed_down = False
        pressed_left = False
        pressed_right = False
        x = 0
        # Buttons ------------------------------------------------ #
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == select_key:
                    pressed_select = True
                if event.key == up_key:
                    pressed_up = True
                if event.key == down_key:
                    pressed_down = True
                if event.key == left_key:
                    pressed_left = True
                if event.key == right_key:
                    pressed_right = True
        # Menu options ------------------------------------------- #
        for option in menu_layout:
            options_bar_img = options_bar.copy()
            if x == selection:
                options_bar_img = core_funcs.swap_color(options_bar_img, (46,31,60), (99,90,124))
            display.blit(options_bar_img, (50 + x * 100, 140))
            core_funcs.show_text(option, 92 + x * 100 - int(get_text_width(option, 1) / 2), 144, 1, 999, font, display)
            x += 1
        # Pressed select ----------------------------------------- #
        if pressed_select:
            play_sound('menu_select')
            menu_choice = menu_layout[selection]
            if menu_choice == 'Play':
                pygame.mixer.music.fadeout(333)
                fade(screen, 1)
                play_game()
            if menu_choice == 'Options':
                fade(screen, 1)
                simple_menu('options')
            if menu_choice == 'Quit':
                pygame.quit()
                sys.exit()
        # Pressed left ------------------------------------------- #
        if pressed_left:
            play_sound('menu_move')
            selection -= 1
            if selection < 0:
                selection = len(menu_layout) - 1
        # Pressed right ------------------------------------------ #
        if pressed_right:
            play_sound('menu_move')
            selection += 1
            if selection >= len(menu_layout):
                selection = 0
        if white_timer > 0:
            white_surf = pygame.Surface(display_size)
            white_surf.fill(WHITE)
            white_surf.set_alpha(int(white_timer * 3))
            white_timer -= 1
            display.blit(white_surf, (0, 0))
        # Screen display ----------------------------------------- #
        if fullscreened == 'y':
            screen.blit(pygame.transform.scale(display, (display_fullscreen)), (0,0))
        else:
            screen.blit(pygame.transform.scale(display, (display_size[0] * scale, display_size[1] * scale)), (0,0))
        fade_in(screen)
        # Update ------------------------------------------------- #
        pygame.display.update()
        # --- Limit to 60 frames per second (FPS)
        mainClock.tick(60)
# Loading function ----------------------------------------------- #
def loading(result, maze_constructor, x, y):
    global running, tile_map, spawn, maze_solver, end_position
    running = True
    while running:
        # Background --------------------------------------------- #
        display.fill(BG)
        # Create maze -------------------------------------------- #
        maze_constructor += 1
        if maze_constructor == 200:
            x += 2
            y += 2
            maze = Maze(x, y)
            maze.print_banner()
            maze.kruskal()
            tile_map, spawn, maze_solver, end_position = load_map('maze')
            play_game()
            break
        # Screen display ----------------------------------------- #
        if fullscreened == 'y': screen.blit(pygame.transform.scale(display, (display_fullscreen)), (0,0))
        else: screen.blit(pygame.transform.scale(display, (display_size[0] * scale, display_size[1] * scale)), (0,0))
        # Update ------------------------------------------------- #
        pygame.display.update()
        # --- Limit to 60 frames per second (FPS)
        mainClock.tick(60)
    return tile_map, spawn, maze_solver, end_position
# Display function ----------------------------------------------- #
def screen_display():
    # Screen display ----------------------------------------- #
    if fullscreened == 'y': screen.blit(pygame.transform.scale(display, (display_fullscreen)), (0,0))
    else: screen.blit(pygame.transform.scale(display, (display_size[0] * scale, display_size[1] * scale)), (0,0))
    # Update ------------------------------------------------- #
    pygame.display.update()
    # --- Limit to 60 frames per second (FPS)
    mainClock.tick(60)
    return
# Play game function --------------------------------------------- #
def play_game():
    # Local variables -------------------------------------------- #
    global running
    up, down, right, left = False, False, False, False
    player_x = 0
    player_y = -1
    shader_size = 100
    shader_dir = 1
    passage_player = 1
    finish = 0
    result = False
    maze_constructor = 0
    solver = 0
    scroll_x, scroll_y = spawn[0] - int(display_size[0] / 2), spawn[1] - int(display_size[1] / 2)
    player = PhysicsObject(spawn[0], spawn[1], 11, 6)
    # Loop ------------------------------------------------------- #
    while running:
        # Background --------------------------------------------- #
        display.fill(BG)
        scroll_x += (player.x - display_size[0] / 2 - scroll_x) / 12
        scroll_y += (player.y - display_size[1] / 2 - scroll_y) / 12
        # Tiles -------------------------------------------------- #
        tile_surf = pygame.Surface(display_size)
        tile_surf.set_colorkey(BLACK)
        visible_tiles = []
        collision_tiles = []
        for y in range(15):
            for x in range(21):
                target_x = x - 1 + int(scroll_x / 16)
                target_y = y - 1 + int(scroll_y / 16)
                target = str(target_x) + ';' + str(target_y)
                if target in tile_map:
                    visible_tiles.append(tile_map[target])
        for tile in visible_tiles:
            solid = False
            img = tile[0]
            if img not in decor_list:
                solid = True
            if img not in tall_tiles:
                tile_surf.blit(tile_database[img], (tile[1] * 16 - scroll_x, tile[2] * 16 - scroll_y))
            else:
                tile_surf.blit(tile_database[img], (tile[1] * 16 - scroll_x, tile[2] * 16 - 1 - scroll_y))
            if solid:
                collision_tiles.append([tile[1] * 16, tile[2] * 16, 16, 16])
        # Shaders ------------------------------------------------ #
        shader_size += shader_dir * 0.4
        #if finish == 0:
        if shader_size > 125: shader_dir = -1
        if shader_size < 110: shader_dir = 1
        lights = [[[player.rect.x - int(scroll_x), player.rect.y - int(scroll_y)], int(shader_size), 180]]
        shader_surf = pygame.Surface(display_size)
        shaders.draw_lights(shader_surf, lights, tile_surf, light_img_2)
        shader_surf.set_colorkey((0,0,0))
        shader_surf.set_alpha(100)
        display.blit(shader_surf,(0,0))
        overlay_surf = pygame.Surface(display_size)
        shaders.draw_raw_lights(overlay_surf, lights, light_img)
        # Show Tiles --------------------------------------------- #
        display.blit(tile_surf,(0,0))
        display.blit(overlay_surf, (0,0), special_flags = BLEND_MULT)
        # Solver ------------------------------------------------- #
        # If the player has arrived
        if player.x >= end_position[0] * 16 and player.y >= end_position[1] * 16:
            finish += 1
            if finish >= 100:
                if solver == len(solver_list):
                    break
                else:
                    xm, ym = solver_list[solver][1][0], solver_list[solver][1][1]
                    pygame.draw.rect(display, (0, 255, 0), pygame.Rect(xm * 16 - scroll_x, ym * 16 - scroll_y, 16, 16))
                    solver += 1
        # Player ------------------------------------------------- #
        player_position = [player_x, player_y]
        if player_x > 0:
            player_x -= 0.5
            if player_x > 2:
                player_x = 2
        if player_x < 0:
            player_x += 0.5
            if player_x < -2:
                player_x = -2
        if player_y > 0:
            player_y -= 0.5
            if player_y > 2:
                player_y = 2
        if player_y < 0:
            player_y += 0.5
            if player_y < -2:
                player_y = -2
        if up: player_y -= 1
        if down: player_y += 1
        if left: player_x -= 1
        if right: player_x += 1
        player_collisisons = player.move(player_position, collision_tiles)
        display.blit(camera_img,(player.rect.x - scroll_x, player.rect.y - scroll_y))
        # Buttons ------------------------------------------------ #
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.key == up_key:
                    up = True
                if event.key == down_key:
                    down = True
                if event.key == left_key:
                    left = True
                if event.key == right_key:
                    right = True
            if event.type == KEYUP:
                if event.key == up_key:
                    up = False
                if event.key == down_key:
                    down = False
                if event.key == left_key:
                    left = False
                if event.key == right_key:
                    right = False
        # Screen display ----------------------------------------- #
        if fullscreened == 'y':
            screen.blit(pygame.transform.scale(display, (display_fullscreen)), (0,0))
        else: screen.blit(pygame.transform.scale(display, (display_size[0] * scale, display_size[1] * scale)), (0,0))
        # Update ------------------------------------------------- #
        pygame.display.update()
        # --- Limit to 60 frames per second (FPS)
        mainClock.tick(60)
    os.system('cls')
    result = True
    maze_constructor += 1
    loading(result, maze_constructor, xmc, ymc)
opening()
menu_run()
play_game()
pygame.quit()
