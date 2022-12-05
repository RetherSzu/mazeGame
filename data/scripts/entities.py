# Import --------------------------------------------------------- #
try:
        import pygame
        from pygame.locals import *
# Error verification import -------------------------------------- #
except ImportError as err:
        print("Unable to load module %s" % (err))
        sys.exit()
# CollisionTest function ----------------------------------------- #
def CollisionTest(Object1, ObjectList):
    CollisionList = []
    for Object in ObjectList:
        ObjectRect = pygame.Rect(Object[0],Object[1],Object[2],Object[3])
        if ObjectRect.colliderect(Object1):
            CollisionList.append(ObjectRect)
    return CollisionList
# Class PhysicsObject -------------------------------------------- #
class PhysicsObject(object):
    def __init__(self, x, y, x_size, y_size):
        self.x = x
        self.y = y
        self.width = x_size
        self.height = y_size
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def move(self, move, platforms):
        self.x += move[0]
        self.rect.x = int(self.x)
        collision_types = {'top':False,'bottom':False,'right':False,'left':False}
        block_hit_list = CollisionTest(self.rect,platforms)
        for block in block_hit_list:
            if move[0] > 0:
                self.rect.right = block.left
                collision_types['right'] = True
            elif move[0] < 0:
                self.rect.left = block.right
                collision_types['left'] = True
            self.x = self.rect.x
        self.y += move[1]
        self.rect.y = int(self.y)
        block_hit_list = CollisionTest(self.rect,platforms)
        for block in block_hit_list:
            if move[1] > 0:
                self.rect.bottom = block.top
                collision_types['bottom'] = True
            elif move[1] < 0:
                self.rect.top = block.bottom
                collision_types['top'] = True
            self.change_y = 0
            self.y = self.rect.y
        return collision_types

# Class Entity ------------------------------------------------ #
class Entity(object):
    def __init__(self, x, y, x_size, y_size, entity_type):
        self.x = x
        self.y = y
        self.x_size = x_size
        self.y_size = y_size
        self.obj = PhysicsObject(x, y, x_size, y_size)
        self.type = entity_type

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.obj.x = x
        self.obj.y = y
        self.obj.rect = x
        self.obj.rect = y
