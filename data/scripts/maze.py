# Import --------------------------------------------------------- #
try:
    import sys, os, pygame, random, time, json
    from pygame.locals import *
    from data.scripts.color import Color
# Error verification import -------------------------------------- #
except ImportError as err:
    print("Unable to load module %s" %(err))
    sys.exit()
# Version -------------------------------------------------------- #
version = "1.0"
# Setup pygame/window -------------------------------------------- #
pygame.init()
# Define clock time (FPS)
mainClock = pygame.time.Clock()
# Open a new window
display_size = [1152, 648]
pygame.display.set_caption("Game nomekop - Maze Generator v" + version)
screen = pygame.display.set_mode((display_size[0], display_size[1]), 0, 32)
display = pygame.Surface((300,200))
font = pygame.font.SysFont(None, 5)
# Load tiles ----------------------------------------------------- #
tile_list = os.listdir('data/images/tiles')
tile_database = {}
not_valid = ['Thumbs.db','tilesets']
for tile in tile_list:
    if tile not in not_valid:
        img = pygame.image.load('data/images/tiles/' + tile).convert()
        img.set_colorkey((255,255,255))
        tile_database[tile] = img.copy()
tileset_list = os.listdir('data/images/tiles/tilesets')
tileset_types = []
for tile in tileset_list:
    img = pygame.image.load('data/images/tiles/tilesets/' + tile).convert()
    img.set_colorkey((255,255,255))
    tile_type = tile[:tile.find('_')]
    tile_subtype = tile[tile.find('_')+1:]
    if tile_type not in tile_database:
        tile_database[tile_type] = {}
        tileset_types.append(tile_type)
    tile_database[tile_type][tile_subtype] = img.copy()
# Local variables ------------------------------------------------ #
tall_tiles =  [('rocks','0011.png'),('rocks','0110.png'),('rocks','0111.png'),('rocks','0100.png'),('rocks','0101.png'),('rocks','0001.png'),('rocks','corner_0110.png'),('rocks','corner_0011.png'),('rocks','corner_0111.1.png'),('rocks','corner_0111.2.png'),('rocks','corner_0111.png')]
tile_size = [5, 5]
# Class Maze ----------------------------------------------------- #
class Maze():
    def __init__(self, width, height, player_x = 0, player_y = 1):
        if width % 2 == 0: self.width = width + 1
        else: self.width = width
        if height % 2 == 0: self.height = height + 1
        else: self.height = height
        self.tile_map = {
                'tile_map': {},
                'maze_solver': {},
                'end_maze': [self.width - 2, self.height - 1]
        }
        self.solver = {}
        self.player_x = player_x
        self.player_y = player_y
        self.maze = [[-1 for x in range(0, self.width)] for y in range(0, self.height)]
        self.maze_color = self.maze

    def print_banner(self):
        """
        """
        Color.pl('{?} Width  : ' + str(self.width))
        Color.pl('{?} height : ' + str(self.height))
        Color.pl('{?} position player (x, y) : ' + str(self.player_x) + ', ' + str(self.player_y))

    def set_width(self, width):
        """
        Cette fonction permet de paramètrer la largeur du maze
        """
        if width % 2 == 0:
            self.width = width + 1
        else:
            self.width = width

    def set_height(self, height):
        """
        Cette fonction permet de paramètrer la hauteur du maze
        """
        if height % 2 == 0:
            self.height = height + 1
        else:
            self.height = height

    def get_width(self):
        """
        Cette fonction permet de recupérer la largeur du maze
        """
        return self.width

    def get_height(self):
        """
        Cette fonction permet de recupérer la hauteur du maze
        """
        return self.height

    def add(self, x, y, test = True):
        """
        # Cette fonction permet d'ajouter à la liste tile_map la position d'un block
        :param x : position du block sur l'axe x
        :type_param : int
        :param y : position du block sur l'axe y
        :type_param : int
        """
        loc = str(x) + ';' + str(y)
        if test:
            self.tile_map['tile_map'][loc] = [[('rocks', '1111.png')], x, y]
        else:
            self.tile_map['tile_map'][loc] = [[('rocks', '1111_test.png')], x, y]

    def thick_wall(self, density = 3):
        """
        # Cette fonction permet de céer un mur autour du labyrinthe, l'épaisseur du mur est en fonction de la variable (density) donnée en paramètre
        :param density : épaisseur du mur
        :type_param : int
        """
        for x in range(-density, self.width + density):
            for y in range(-density, self.height + density):
                if x < self.player_x or y < self.player_y:
                    self.add(x, y)
                if x > self.width - 1 or y > self.height - 1:
                    self.add(x, y)
        Color.pl('{+} Génération des murs du labyrinthe terminé')

    def update(self):
        """
        # Cette fonction permet d'update toutes les tuiles de la map
        """
        start_time = time.time()
        for i in range(2):
            directions = [(0,-1),(1,0),(0,1),(-1,0)] # top, right, bottom, left
            for tile in self.tile_map['tile_map']:
                i_num = 0
                for img in self.tile_map['tile_map'][tile][0]:
                    if img not in tile_database:
                        found = ['0','0','0','0']
                        tile_types_found = []
                        n = 0
                        for direction in directions:
                            test_str = str(self.tile_map['tile_map'][tile][1]+direction[0]) + ';' + str(self.tile_map['tile_map'][tile][2]+direction[1])
                            if test_str in self.tile_map['tile_map']:
                                for img2 in self.tile_map['tile_map'][test_str][0]:
                                    if img2 not in tile_database:
                                        if img2[0] == img[0]:
                                            found[n] = '1'
                                            tile_types_found.append(img2[1])
                            if len(tile_types_found) <= n:
                                tile_types_found.append(None)
                            n += 1
                        f_copy = found.copy()
                        found = ''
                        switch = None
                        if (tile_types_found[0] in ['1110.png','0110.png']) and (tile_types_found[1] != None) and (tile_types_found[2] != None) and (tile_types_found[3] in ['0111.png','0110.png']):
                            switch = 'corner_0.png'
                        if (tile_types_found[0] in ['1011.png','0011.png']) and (tile_types_found[1] in ['0111.png','0011.png']) and (tile_types_found[2] != None) and (tile_types_found[3] != None):
                            switch = 'corner_1.png'
                        if (tile_types_found[0] != None) and (tile_types_found[1] != None) and (tile_types_found[2] in ['1110.png','1100.png']) and (tile_types_found[3] in ['1101.png','1100.png']):
                            switch = 'corner_2.png'
                        if (tile_types_found[0] != None) and (tile_types_found[1] in ['1101.png','1001.png']) and (tile_types_found[2] in ['1011.png','1001.png']) and (tile_types_found[3] != None):
                            switch = 'corner_3.png'
                        if (tile_types_found[0] in ['0010.png','1010.png']) and (tile_types_found[1] in ['0111.png','0011.png']) and (tile_types_found[2] != None) and (tile_types_found[3] in ['0110.png','0111.png']):
                            switch = 'corner_4.png'
                        if (tile_types_found[0] in ['0011.png','1011.png']) and (tile_types_found[1] in ['0101.png','0001.png']) and (tile_types_found[2] in ['1001.png','1011.png']) and (tile_types_found[3] != None):
                            switch = 'corner_5.png'
                        if (tile_types_found[0] != None) and (tile_types_found[1] in ['1001.png','1101.png']) and (tile_types_found[2] in ['1000.png','1010.png','corner_1001.png','corner_1100.png']) and (tile_types_found[3] in ['1101.png','1100.png']):
                            switch = 'corner_6.png'
                        if (tile_types_found[0] in ['0110.png','1110.png']) and (tile_types_found[1] != None) and (tile_types_found[2] in ['1110.png','1100.png']) and (tile_types_found[3] in ['0101.png','0100.png','corner_0110.png','corner_1100.png']):
                            switch = 'corner_7.png'
                        if (tile_types_found[0] in ['1010.png','0010.png','corner_0110.png','corner_0011.png']) and (tile_types_found[1] in ['0111.png','0011.png']) and (tile_types_found[2] in ['1110.png','1100.png']) and (tile_types_found[3] in ['0101.png','0100.png','corner_0110.png','corner_1100.png']):
                            switch = 'corner_8.png'
                        if (tile_types_found[0] in ['1010.png','0010.png','corner_0110.png','corner_0011.png']) and (tile_types_found[1] in ['0101.png','0001.png','corner_0011.png','corner_1001.png']) and (tile_types_found[2] in ['1011.png','10011.png']) and (tile_types_found[3] in ['0111.png','0110.png']):
                            switch = 'corner_9.png'
                        if (tile_types_found[0] in ['1011.png','0011.png']) and (tile_types_found[1] in ['0101.png','0001.png','corner_0011png','corner_1001.png']) and (tile_types_found[2] in ['1010.png','1000.png','corner_1100.png','corner_1001.png']) and (tile_types_found[3] in ['1101.png','1100.png']):
                            switch = 'corner_10.png'
                        if (tile_types_found[0] in ['1110.png','0110.png']) and (tile_types_found[1] in ['1101.png','1001.png']) and (tile_types_found[2] in ['1010.png','1000.png','corner_1100.png','corner_1001.png']) and (tile_types_found[3] in ['0100.png','0101.png','corner_1100.png','corner_0110.png']):
                            switch = 'corner_11.png'
                        if (tile_types_found[0] in ['1010.png','0010.png','corner_0110.png','corner_0011.png']) and (tile_types_found[1] in ['0101.png','0001.png','corner_0011.png','corner_1001.png']) and (tile_types_found[2] in ['1010.png','1000.png','corner_1001.png','corner_1100.png']) and (tile_types_found[3] in ['0101.png','0100.png','corner_0110.png','corner_1100.png']):
                            switch = 'corner_12.png'
                        if (tile_types_found[0] in ['0011.png','1011.png']) and (tile_types_found[1] in ['0111.png','0011.png']) and (tile_types_found[2] in ['1110.png','1100.png']) and (tile_types_found[3] in ['1101.png','1100.png']):
                            switch = 'corner_13.png'
                        if (tile_types_found[0] in ['1110.png','0110.png']) and (tile_types_found[1] in ['1101.png','1001.png']) and (tile_types_found[2] in ['1011.png','1001.png']) and (tile_types_found[3] in ['0111.png','0110.png']):
                            switch = 'corner_14.png'

                        if (tile_types_found[0] == None) and (tile_types_found[1] == None) and (tile_types_found[2] == None) and (tile_types_found[3] == None):
                            switch = '0000.png'
                        if (tile_types_found[0] != None) and (tile_types_found[1] == None) and (tile_types_found[2] == None) and (tile_types_found[3] == None):
                            switch = '1000.png'
                        if (tile_types_found[0] == None) and (tile_types_found[1] != None) and (tile_types_found[2] == None) and (tile_types_found[3] == None):
                            switch = '0100.png'
                        if (tile_types_found[0] == None) and (tile_types_found[1] == None) and (tile_types_found[2] != None) and (tile_types_found[3] == None):
                            switch = '0010.png'
                        if (tile_types_found[0] == None) and (tile_types_found[1] == None) and (tile_types_found[2] == None) and (tile_types_found[3] != None):
                            switch = '0001.png'

                        if (tile_types_found[0] == None) and (tile_types_found[1] in ['0111.png','0011.png']) and (tile_types_found[2] in ['1110.png','1100.png']) and (tile_types_found[3] == None):
                            switch = '0110.png'
                        if (tile_types_found[0] == None) and (tile_types_found[1] == None) and (tile_types_found[2] in ['1011','1001.png']) and (tile_types_found[3] in ['0111.png','0110.png']):
                            switch = '0011.png'
                        if (tile_types_found[0] in ['1011.png','0011.png']) and (tile_types_found[1] == None) and (tile_types_found[2] == None) and (tile_types_found[3] in ['1101.png','1100.png']):
                            switch = '1001.png'
                        if (tile_types_found[0] in ['1110.png','0110.png']) and (tile_types_found[1] in ['1101.png','1001.png']) and (tile_types_found[2] == None) and (tile_types_found[3] == None):
                            switch = '1100.png'

                        if (tile_types_found[0] == None) and (tile_types_found[1] in ['0101.png','0001.png','corner_0011.png','corner_1001.png']) and (tile_types_found[2] in ['1010.png','1000.png','corner_1100.png','corner_1001.png']) and (tile_types_found[3] == None):
                            switch = 'corner_0110.png'
                        if (tile_types_found[0] == None) and (tile_types_found[1] == None) and (tile_types_found[2] in ['1010.png','1000.png','corner_1100.png','corner_1001.png']) and (tile_types_found[3] in ['0100.png','0101.png','corner_0110.png','corner_1100.png']):
                            switch = 'corner_0011.png'
                        if (tile_types_found[0] in ['1010.png','0010.png','corner_0110.png','corner_0011.png']) and (tile_types_found[1] in ['0001.png','0101.png','corner_0011.png','corner_1001.png']) and (tile_types_found[2] == None) and (tile_types_found[3] == None):
                            switch = 'corner_1100.png'
                        if (tile_types_found[0] in ['0010.png','1010.png','corner_0011.png','corner_0110.png']) and (tile_types_found[1] == None) and (tile_types_found[2] == None) and (tile_types_found[3] in ['0101.png','0100.png','corner_0110.png','corner_1100.png']):
                            switch = 'corner_1001.png'

                        if (tile_types_found[0] == None) and (tile_types_found[1] in ['0101.png','0001.png','corner_0011.png','corner_1001.png']) and (tile_types_found[2] in ['1010.png','1000.png','corner_1100.png','corner_1001.png']) and (tile_types_found[3] in ['0101.png','0100.png','corner_0110.png','corner_1100.png']):
                            switch = 'corner_0111.png'
                        if (tile_types_found[0] == None) and (tile_types_found[1] in ['0101.png','0001.png','corner_0011.png','corner_1001.png']) and (tile_types_found[2] in ['1011.png','1001.png']) and (tile_types_found[3] in ['0111.png','0110.png']):
                            switch = 'corner_0111.1.png'
                        if (tile_types_found[0] == None) and (tile_types_found[1] in ['0111.png','0011.png']) and (tile_types_found[2] in ['1110.png','1100.png']) and (tile_types_found[3] in ['0101.png','0100.png','corner_0110.png','corner_1100.png']):
                            switch = 'corner_0111.2.png'

                        if (tile_types_found[0] in ['1010.png','0010.png','corner_0110.png','corner_0011.png']) and (tile_types_found[1] == None) and (tile_types_found[2] in ['1010.png','1000.png','corner_1001.png','corner_1100.png']) and (tile_types_found[3] in ['0101.png','0100.png','corner_1100.png','corner_0110.png']):
                            switch = 'corner_1011.png'
                        if (tile_types_found[0] in ['1010.png','0010.png','corner_0110.png','corner_0011.png']) and (tile_types_found[1] == None) and (tile_types_found[2] in ['1011.png','1001.png']) and (tile_types_found[3] in ['0111.png','0110.png']):
                            switch = 'corner_1011.1.png'
                        if (tile_types_found[0] in ['1011.png','0011.png']) and (tile_types_found[1] == None) and (tile_types_found[2] in ['1010.png','1000.png','corner_1100.png','corner_1001.png']) and (tile_types_found[3] in ['1101.png','1100.png']):
                            switch = 'corner_1011.2.png'

                        if (tile_types_found[0] in ['0010.png','1010.png','corner_0110.png','corner_0011.png']) and (tile_types_found[1] in ['0101.png','0001.png','corner_0011.png','corner_1001.png']) and (tile_types_found[2] == None) and (tile_types_found[3] in ['0101.png','0100.png','corner_0110.png','corner_1100.png']):
                            switch = 'corner_1101.png'
                        if (tile_types_found[0] in ['1011.png','0011.png']) and (tile_types_found[1] in ['0101.png','0001.png','corner_1001.png','corner_0011.png']) and (tile_types_found[2] == None) and (tile_types_found[3] in ['1101.png','1100.png']):
                            switch = 'corner_1101.1.png'
                        if (tile_types_found[0] in ['1110.png','0110.png']) and (tile_types_found[1] in ['1101.png','1001.png']) and (tile_types_found[2] == None) and (tile_types_found[3] in ['0101.png','0100.png','corner_0110.png','corner_1100.png']):
                            switch = 'corner_1101.2.png'

                        if (tile_types_found[0] in ['1010.png','0010.png','corner_0110.png','corner_0011.png']) and (tile_types_found[1] in ['0101.png','0001.png','corner_0011.png','corner_1001.png']) and (tile_types_found[2] in ['1010.png','1000.png','corner_1100.png','corner_1001.png']) and (tile_types_found[3] == None):
                            switch = 'corner_1110.png'
                        if (tile_types_found[0] in ['1010.png','0010.png','corner_0011.png','corner_0110.png']) and (tile_types_found[1] in ['0111.png','0011.png']) and (tile_types_found[2] in ['1110.png','1100.png']) and (tile_types_found[3] == None):
                            switch = 'corner_1110.1.png'
                        if (tile_types_found[0] in ['1110.png','0110.png']) and (tile_types_found[1] in ['1101.png','1001.png']) and (tile_types_found[2] in ['1010.png','1000.png','corner_1100.png','corner_1001.png']) and (tile_types_found[3] == None):
                            switch = 'corner_1110.2.png'

                        for char in f_copy:
                            found += char
                        if switch == None:
                            if found + '.png' in tile_database[img[0]]:
                                self.tile_map['tile_map'][tile][0][i_num] = (img[0],found + '.png')
                        else:
                            if switch in tile_database[img[0]]:
                                self.tile_map['tile_map'][tile][0][i_num] = (img[0],switch)
                    i_num += 1
        Color.pl('{+} Update des blocs terminé')
        Color.pl('{!} Time : ' + str(time.time() - start_time))

    def is_finished(self):
        """
        # Cette fonction permet de vérifier si le labyrinthe est terminé
        """
        for x in range(1, self.width - 1, 2):
            for y in range(1, self.height - 1, 2):
                if self.maze[x][y] != self.maze[1][1]:
                    return False
        return True

    def kruskal(self):
        """
        # Cette fonction permet de creer un labyrinthe à la façon de kruskal
        """
        display = False
        up = False
        down = False
        right = False
        left = False
        scroll_x = 0
        scroll_y = 0
        nb = 0
        for x in range(0, self.width):
            for y in range(0, self.height):
                if x % 2 != 0 and y % 2 != 0:
                    self.maze[x][y] = nb
                    nb += 1
        self.maze[0][1] = 1
        self.maze[self.width - 2][self.height - 1] = nb
        while self.is_finished() == 0: # if self.is_finished == False
            x = int(random.randint(0, self.width) % (101 - 2) + 1)
            if x % 2 == 0:
                y = int((random.randint(0, self.height) % ((101 - 1) / 2)) * 2 + 1)
            else:
                y = int((random.randint(0, self.height) % ((101 - 2) / 2)) * 2 + 2)
            if x >= 1 and y >= 1 and x <= self.width - 2 and y <= self.height - 2:
                if self.maze[x - 1][y] == -1:
                    cell_1 = self.maze[x][y - 1] # left
                    cell_2 = self.maze[x][y + 1] # right
                else:
                    cell_1 = self.maze[x - 1][y] # top
                    cell_2 = self.maze[x + 1][y] # bottom
                if cell_1 != cell_2:
                    self.maze[x][y] = cell_1
                    for i in range(1, self.width - 1, 2):
                        for j in range(1, self.height - 1, 2):
                            if self.maze[i][j] == cell_2:
                                self.maze[i][j] = cell_1
        for i in range(0, self.width - 1):
            x = int(random.randint(0, self.width) % (101 - 2) + 1)
            if x % 2 == 0:
                y = int((random.randint(0, self.height) % ((101 - 1) / 2)) * 2 + 1)
            else:
                y = int((random.randint(0, self.height) % ((101 - 2) / 2)) * 2 + 2)
            if x >= 1 and y >= 1 and x <= self.width - 2 and y <= self.height - 2:
                self.maze[x][y] = 0
        Color.pl('{+} Génération du labyrinthe terminé')
        dist = self.maze_solver()
        self.thick_wall()
        for x in range(self.width):
            for y in range(self.height):
                if self.maze[x][y] == dist + 300:
                    self.add(x, y)
        self.update()
        self.export_maze()

    def maze_solver(self):
        self.maze[0][1] = 0
        display_interface = True
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                if self.maze[x][y] >= 0:
                    self.maze[x][y] = 0
        distance = 1
        self.maze[self.width - 2][self.height - 1] = 1
        while self.maze[1][1] == 0:
            self.maze_color = self.maze
            for x in range(1, self.width - 1):
                for y in range(1, self.height - 1):
                    if self.maze[x][y] == 0:
                        if self.maze[y - 1][x] > 0 or self.maze[y + 1][x] > 0 or self.maze[y][x - 1] > 0 or self.maze[y][x + 1] > 0: # top, bottom, left , right
                            self.maze_color[x][y] = distance
                        #if self.maze[x - 1][y] > 0 or self.maze[x + 1][y] > 0 or self.maze[x][y - 1] > 0 or self.maze[x][y + 1] > 0: # top, bottom, left , right
                            #self.maze_color[x][y] = distance
            self.display_interface()
            distance += 1
            self.maze = self.maze_color
        self.maze[0][1] = distance + 20
        for x in range(0, self.width):
            for y in range(0, self.height):
                if self.maze[x][y] == 0:
                    self.maze[x][y] = distance + 1
                if self.maze[x][y] == -1:
                    self.maze[x][y] = distance + 300
        x, y = 1, 1
        Color.pl('{+} Génération des couleurs terminées')
        self.maze[x][y] = 255
        while x != self.width - 2 or y != self.height - 1:
            top    = self.maze[x    ][y - 1]
            right  = self.maze[x + 1][y    ]
            bottom = self.maze[x    ][y + 1]
            left   = self.maze[x - 1][y    ]
            if top <= bottom and top <= left and top <= right:
                y -= 1
            elif bottom <= top and bottom <= left and bottom <= right:
                y += 1
            elif right <= top and right <= bottom and right <= left:
                x += 1
            elif left <= top and left <= bottom and left <= right:
                x -= 1
            self.maze[x][y] = 255
            loc = str(x) + ';' + str(y)
            self.solver[loc] = ([x, y])
            self.display_interface()
        Color.pl('{+} Génération de la solution du labyrinthe terminé')
        self.display_interface()
        return distance

    def color(self, value, wall = False):
        value = int(value / self.width * 255)
        if value <= 255:
            return (255, 255 - value, 0)
        if value > 255 and value <= 255 * 2:
            return (2 * 255 - value, 0, value - 255)
        if value > 255 * 2 and value <= 255 * 3:
            return (0, 0, 255 * 3 - value)
        return (0, 0, 0)

    def display_interface(self, test = True, d = 10):
        up = False
        down = False
        right = False
        left = False
        scroll_x = 0
        scroll_y = 0
        running = True
        while running:
            display.fill((31,24,48))
            for x in range(self.width):
                for y in range(self.height):
                    if self.maze[x][y] == -1:
                        pygame.draw.rect(display, (46, 31, 60), pygame.Rect(x * tile_size[0] - scroll_x, y * tile_size[1] - scroll_y, 5, 5))
                    elif self.maze[x][y] == 255:
                        cell_color = (0, 255, 0)
                        pygame.draw.rect(display, cell_color, pygame.Rect(x * tile_size[0] - scroll_x, y * tile_size[1] - scroll_y, 5, 5))
                    elif self.maze[x][y] != -1:
                        cell_color = self.color(self.maze[x][y])
                        pygame.draw.rect(display, cell_color, pygame.Rect(x * tile_size[0] - scroll_x, y * tile_size[1] - scroll_y, 5, 5))
                        #if self.maze[x][y] != 0:
                            #text.show_text(str(self.maze[x][y]), x * tile_size[0], y * tile_size[1], 0, 999, font, display)
            if right: scroll_x += 4
            if left: scroll_x -= 4
            if up: scroll_y -= 4
            if down: scroll_y += 4
            # Buttons ---------------------------------------- #
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if event.key == K_LEFT:
                        left = True
                    if event.key == K_RIGHT:
                        right = True
                    if event.key == K_UP:
                        up = True
                    if event.key == K_DOWN:
                        down = True
                if event.type == KEYUP:
                    if event.key == K_LEFT:
                        left = False
                    if event.key == K_RIGHT:
                        right = False
                    if event.key == K_UP:
                        up = False
                    if event.key == K_DOWN:
                        down = False
            # Update ------------------------------------------------- #
            screen.blit(pygame.transform.scale(display,(300*4,200*4)),(0,0))
            pygame.display.update()
            if test:
                running = False
            # --- Limit to 60 frames per second (FPS)
            mainClock.tick(60)

    def export_maze(self):
        """
        # Cette fonction (export_maze) permet de mettre dans un fichier json le labyrinthe
        """
        try:
            for tile in self.tile_map['tile_map']:
                for img in self.tile_map['tile_map'][tile][0]:
                    self.tile_map['tile_map'][tile][0] = img[0] + '_' + img[1]
            loc = str(self.width - 2) + ';' + str(self.height - 1)
            self.tile_map['tile_map'][loc] = ['finish.png', self.width - 2, self.height - 1]
            self.tile_map['maze_solver'] = self.solver
            file = open('data/maps/maze.json','w')
            file.write(json.dumps(self.tile_map))
            file.close()
            Color.pl('{+} Le labyrinthe a été écrit dans un fichier json')
        except Exception as e:
            Color.pl('{!} Erreur lors de l\'écriture du labyrinthe dans un fichier json ')

if __name__ == '__main__':
    Color.pl('{+} Création d\'un labyrinthe')
    maze = Maze(20, 20)
    maze.kruskal()
    # pygame.quit()
