#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2021 Jose Gonzalez ~ All rights reserved. MIT license.
import sys

import numpy as np
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.constants import *

from pyvmol import MoleculeLoad


class MolViewer:

    def __init__(self, file, style: str = 'Default'):
        self.style = style
        self.size_radius = 5
        self.mol = MoleculeLoad(file)
        self.coordinates, self.radios, self.colors = self.mol.load()
        self.connectivity = self.mol.connect()
        self.x, self.y, self.z = self.centroid()
        self.width = None
        self.height = None
        self.init()
        self.sphere = gluNewQuadric()
        self.cylinder = gluNewQuadric()
        self.display()

    def coords(self):
        return self.coordinates

    @staticmethod
    def init():
        pygame.init()
        viewport = (600, 600)
        pygame.display.set_caption('PyVMolecule')
        pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)

        # Light
        glLightfv(GL_LIGHT0, GL_POSITION, (-40, 200, 100, 0.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.4, 0.4, 0.4, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        # glShadeModel(GL_FLAT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        width, height = viewport
        gluPerspective(45, width / float(height), 1, 100.0)

    def centroid(self):
        array = np.array(self.coordinates)
        length = array.shape[0]
        sum_x = np.sum(array[:, 0])
        sum_y = np.sum(array[:, 1])
        sum_z = np.sum(array[:, 2])
        return sum_x / length, sum_y / length, sum_z / length

    def display(self):
        rx, ry = (self.x, self.y)
        tx, ty = (0, 0)
        # ADJUST ZOOM ACCORDING TO FIGURE SIZE !!!!!!!
        # zoom_position = (self.z * (100 / (self.x + self.y + self.z))) + 25
        zoom_position = 45
        rotate = move = False
        glMatrixMode(GL_MODELVIEW)
        run = True
        while run:
            for e in pygame.event.get():
                if e.type == QUIT:
                    run = False
                elif e.type == KEYDOWN and e.key == K_ESCAPE:
                    run = False
                elif e.type == MOUSEBUTTONDOWN:
                    if e.button == 4:
                        zoom_position = max(1, zoom_position - 1)
                    elif e.button == 5:
                        zoom_position += 1
                    elif e.button == 1:
                        rotate = True
                    elif e.button == 3:
                        move = True
                elif e.type == MOUSEBUTTONUP:
                    if e.button == 1:
                        rotate = False
                    elif e.button == 3:
                        move = False
                elif e.type == MOUSEMOTION:
                    i, j = e.rel
                    if rotate:
                        rx += i
                        ry += j
                    if move:
                        tx += i
                        ty -= j
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            glTranslate(tx / 20., ty / 20., - zoom_position)
            glRotate(ry, 1, 0, 0)
            glRotate(rx, 0, 1, 0)
            if self.style == 'Default':
                self.draw_spheres()
                self.draw_lines()
            elif self.style == 'wire':
                self.draw_lines()
            elif self.style == 'cpk':
                self.draw_spheres()
                self.size_radius = 1.5
            else:
                self.draw_spheres()
                self.draw_lines()
            pygame.display.flip()

    def get_coords(self, num: int):
        return self.coordinates[num - 1]

    def get_colors(self, num: int):
        return self.colors[num - 1]

    def draw_lines(self):
        for connect in self.connectivity:
            coord1 = self.get_coords(connect[0])
            coord2 = self.get_coords(connect[1])
            color1 = self.get_colors(connect[0])
            color2 = self.get_colors(connect[1])
            glBegin(GL_LINES)
            glColor3f(color1[0], color1[1], color1[2])
            glVertex3f(coord1[0] - self.x, coord1[1] -
                       self.y, coord1[2] - self.z)
            glColor3f(color2[0], color2[1], color2[2])
            glVertex3f(coord2[0] - self.x, coord2[1] -
                       self.y, coord2[2] - self.z)
            glEnd()
            glLineWidth(1.5)

    def draw_spheres(self):
        i = 0
        for coord in self.coordinates:
            glPushMatrix()
            glTranslate(coord[0] - self.x, coord[1] -
                        self.y, coord[2] - self.z)
            glColor3f(self.colors[i][0], self.colors[i][1], self.colors[i][2])
            gluSphere(self.sphere, self.radios[i] / self.size_radius, 20, 20)
            glPopMatrix()
            i += 1


if __name__ == '__main__':
    try:
        MolViewer(sys.argv[1], sys.argv[2])
    except IndexError:
        try:
            MolViewer(sys.argv[1])
        except IndexError:
            print('FileNotFoundError')
    except OSError:
        print('FileNotFoundError')
