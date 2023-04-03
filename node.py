import pygame as pg

class Node():
    _circle_cache = {}
    def __init__(self, key:str, text:str = "", parent=None, root:bool|int=0, initial_pos = (0, 0), radius=12):
        self.radius = radius
        # self.connections = []
        self.pos = pg.math.Vector2(initial_pos)
        self.text = self.render(text if text else key.replace('_', ' '), pg.font.SysFont("Arial", 16))
        self.key = key
        self.parent = parent
        self.root = False if parent else True
        self.speed = 50
        
    def update(self, screen):
        if self.parent:
            pg.draw.line(screen, (0,255,0), self.pos, self.parent.pos)
        pg.draw.circle(screen, (255,255,255), self.pos, self.radius)
        # pg.draw.circle(screen, (0,0,255), self.pos, 50, 1)
        screen.blit(self.text, self.pos - (self.text.get_size()[0]/2, self.text.get_size()[1]/2))

    def move(self, _dir, dt, limits):
        diretion = pg.Vector2(_dir)
        if diretion.magnitude() > 0:
            self.pos += diretion * self.speed * dt

        if self.pos.x < limits[0] + self.radius:
            self.pos.x = limits[0] + self.radius
        elif self.pos.y < limits[1] + self.radius:
            self.pos.y = limits[1] + self.radius
        elif self.pos.x > limits[2] - self.radius:
            self.pos.x = limits[2]- self.radius
        elif self.pos.y > limits[3]- self.radius:
            self.pos.y = limits[3]- self.radius



    def _circlepoints(self, r):
        r = int(round(r))
        if r in self._circle_cache:
            return self._circle_cache[r]
        x, y, e = r, 0, 1 - r
        self._circle_cache[r] = points = []
        while x >= y:
            points.append((x, y))
            y += 1
            if e < 0:
                e += 2 * y - 1
            else:
                x -= 1
                e += 2 * (y - x) - 1
        points += [(y, x) for x, y in points if x > y]
        points += [(-x, y) for x, y in points if x]
        points += [(x, -y) for x, y in points if y]
        points.sort()
        return points

    def render(self, text, font, gfcolor=(255,255,255), ocolor=(0,0,0), opx=1):
        textsurface = font.render(text, True, gfcolor).convert_alpha()
        w = textsurface.get_width() + 2 * opx
        h = font.get_height()

        osurf = pg.Surface((w, h + 2 * opx)).convert_alpha()
        osurf.fill((0, 0, 0, 0))

        surf = osurf.copy()

        osurf.blit(font.render(text, True, ocolor).convert_alpha(), (0, 0))

        for dx, dy in self._circlepoints(opx):
            surf.blit(osurf, (dx + opx, dy + opx))

        surf.blit(textsurface, (opx, opx))
        return surf