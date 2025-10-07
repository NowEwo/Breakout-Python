# -*- coding: utf-8 -*-
import pygame
import pygame.freetype
import random
import sys
import math
import moderngl
import numpy as np

pygame.init()
pygame.freetype.init()

icon = pygame.image.load("assets/Icon.png")

width, height = 800, 600
render_width, render_height = 800, 600

pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
screen = pygame.Surface((render_width, render_height))

pygame.mouse.set_visible(False)

pygame.display.set_caption("Broken out - v0.1.5")

ctx = moderngl.create_context()

with open("shaders/crt.glsl") as f:
    frag_shader_src = f.read()

vertex_shader_src = """
#version 120
attribute vec2 in_vert;
varying vec2 v_text;
void main() {
    v_text = (in_vert + 1.0) / 2.0;
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
"""

prog = ctx.program(vertex_shader=vertex_shader_src, fragment_shader=frag_shader_src)

vertices = np.array([
    -1.0, -1.0,
     1.0, -1.0,
    -1.0,  1.0,
     1.0,  1.0,
], dtype="f4")

vbo = ctx.buffer(vertices.tobytes())
vao = ctx.simple_vertex_array(prog, vbo, "in_vert")

texture = ctx.texture((width, height), 3)
texture.repeat_x = False
texture.repeat_y = False

pygame.mixer.init()
pygame.mixer.music.load("audio/BackgroundMusic.opus")
pygame.mixer.music.set_volume(1)

main_font = pygame.freetype.Font("fonts/font.ttf", 36)

clock = pygame.time.Clock()

primary_color = (255, 153, 191)
background = [i//3 for i in primary_color]
bg_gradient = []

rayon_balle = 10
x_min, y_min = 0, 0
x_max, y_max = width, height

shake_offset = [0, 0]
shake_duration = 0
shake_magnitude = 5

def start_shake(duration=10, magnitude=5):
    global shake_duration, shake_magnitude
    shake_duration = duration
    shake_magnitude = magnitude

def get_shake_offset():
    global shake_duration, shake_offset
    if shake_duration > 0:
        shake_offset[0] = random.randint(-shake_magnitude, shake_magnitude)
        shake_offset[1] = random.randint(-shake_magnitude, shake_magnitude)
        shake_duration -= 1
    else:
        shake_offset[0] = 0
        shake_offset[1] = 0
    return tuple(shake_offset)

class Balle:
    def vitesse_par_angle(self,angle):
        self.vx = self.vitesse * math.cos(math.radians(angle))
        self.vy = -self.vitesse * math.sin(math.radians(angle))

    def __init__(self):
        self.x, self.y = (400, 400)
        self.vitesse = 8
        self.vitesse_par_angle(60)
        self.sur_Player = True

        self.trail = []

    def afficher(self, offset_x=0, offset_y=0):
        self.trail.insert(0, (int(self.x -rayon_balle + offset_x), int(self.y -rayon_balle + offset_y)))
        if(len(self.trail) > 15):
            self.trail.pop()
        i = 0
        gradient = np.linspace(background,primary_color,num=15,dtype=int)
        if jeu.started:
            for b in range(len(self.trail)):
                pygame.draw.circle(screen, gradient[i], self.trail[-b], rayon_balle, 0)
                i += 1

        pygame.draw.circle(screen, primary_color, (int(self.x -rayon_balle + offset_x), int(self.y -rayon_balle + offset_y)), rayon_balle, 0)


    def rebond_Player(self, Player):
        diff = Player.x - self.x
        longueur_totale = Player.longueur/2 + rayon_balle
        angle = 90 + 80*diff/longueur_totale
        self.vitesse_par_angle(angle)

    def deplacer(self, Player):
        if self.sur_Player:
            self.y = Player.y - 1.5*rayon_balle
            self.x = Player.x + rayon_balle
        else:
            self.x += self.vx
            self.y += self.vy
            if Player.collision_balle(self) and self.vy > 0:
                self.rebond_Player(Player)
            if (self.x + rayon_balle > x_max) or (self.x - rayon_balle < x_min):
                self.vx = -self.vx
            if self.y + rayon_balle > y_max:
                self.sur_Player = True
            if self.y - rayon_balle < y_min:
                self.vy = -self.vy

class Player:
    def __init__(self):
        self.x = (x_min + x_max)/2
        self.y = y_max - rayon_balle - 5
        self.longueur = 10 * rayon_balle
        self.life = 3
        self.score = 0

    def afficher(self, offset_x=0, offset_y=0):
        pygame.draw.rect(screen, primary_color, (int(self.x -self.longueur/2 + offset_x), int(self.y -rayon_balle + offset_y), self.longueur,2*rayon_balle), 0)

    def deplacer(self, x):
        if x - self.longueur/2 < x_min:
            self.x = x_min + self.longueur/2
        elif x + self.longueur/2 > x_max:
            self.x = x_max -self.longueur/2
        else:
            self.x = x


    def collision_balle(self, balle):
        vertical = abs(self.y - balle.y) < 2*rayon_balle
        horizontal = abs(self.x - balle.x) < self.longueur/2 + rayon_balle
        return vertical and horizontal

class Brique:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vie = 1
        self.longueur = 5*rayon_balle
        self.largeur = 3*rayon_balle
        rd = random.randint(2,5)
        self.color = [i//(rd//2) for i in primary_color]

    def en_vie(self):
        return self.vie > 0

    def afficher(self, offset_x=0, offset_y=0):
        pygame.draw.rect(screen, self.color, (int(self.x - self.longueur/2 + offset_x), int(self.y - self.largeur/2 + offset_y), self.longueur ,self.largeur), 0)

    def collision_balle(self, balle):
        marge = self.largeur/2 + rayon_balle
        dy = balle.y - self.y
        touche = False
        if balle.x >= self.x:
            dx = balle.x - (self.x + self.longueur/2 - self.largeur/2)
            if abs(dy) <= marge and dx <= marge:
                touche = True
                if dx <= abs(dy):
                    balle.vy = - balle.vy
                else:
                    balle.vx = -balle.vx
        else:
            dx = balle.x - (self.x - self.longueur/2 + self.largeur/2)
            if abs(dy) <= marge and -dx <= marge:
                touche = True
                if -dx <= abs(dy):
                    balle.vy = - balle.vy
                else:
                    balle.vx = -balle.vx
        if touche:
            self.vie = -1
            start_shake(duration=3, magnitude=3)
            jeu.Player.score += int(25*dy)
            prog["warp"].value = 0.41
            jeu.briques.remove(self)
        return touche

class Jeu:
    def __init__(self):
        self.balle = Balle()
        self.Player = Player()
        self.started = False
        self.generate_bricks()

        prog["warp"].value = 0

    def generate_bricks(self):
        self.briques = []
        for i in range(9):
            for j in range(14):
                self.briques.append(Brique(50+(j*53), 59+(i*33)))

    def gestion_evenements(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.balle.sur_Player:
                        self.balle.sur_Player = False
                        self.balle.vitesse_par_angle(60)
                        if not self.started:
                            self.started = True
                            pygame.mixer.music.play(-1)
            elif event.type == pygame.VIDEORESIZE:
                global width, height
                width, height = event.size
                pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
                ctx.viewport = (0, 0, width, height)


    def mise_a_jour(self):
        x, y = pygame.mouse.get_pos()
        x = x * render_width / width
        y = y * render_height / height
        self.balle.deplacer(self.Player)

        if(len(self.briques) == 0):
            global primary_color, background
            primary_color = [random.randint(100,255) for i in range(3)]
            background = [i//3 for i in primary_color]

            self.generate_bricks()
            self.Player.life += 1

        for i in self.briques:
            if i.en_vie():
                i.collision_balle(self.balle)
        self.Player.deplacer(x)

    def affichage(self):
        offset_x, offset_y = get_shake_offset()

        screen.fill(background)

        self.balle.afficher(offset_x, offset_y)
        self.Player.afficher(offset_x, offset_y)
        for brique in self.briques:
            if brique.en_vie():
                brique.afficher(offset_x, offset_y)

        main_font.render_to(screen, (31 + offset_x, 13 + offset_y), 
                        f'score: {self.Player.score} | Lifes: {self.Player.life}', primary_color)
        main_font.render_to(screen, (render_width-251 + offset_x, 13 + offset_y), 
                        'Broken out', primary_color)

        flipped = pygame.transform.flip(screen, False, True)
        texture_data = pygame.image.tostring(flipped, "RGB")
        texture.write(texture_data)
        texture.use(0)

        prog["iResolution"].value = (width, height)
        if self.started and prog["warp"].value < 0.5:
            prog["warp"].value = prog["warp"].value + 0.01
        prog["scan"].value = 0.1
        prog["iChannel0"].value = 0

        ctx.clear(0.0, 0.0, 0.0)
        vao.render(moderngl.TRIANGLE_STRIP)

        pygame.display.flip()
        clock.tick(60)


jeu = Jeu()

while True:
    jeu.gestion_evenements()
    jeu.mise_a_jour()
    jeu.affichage()

pygame.quit()
