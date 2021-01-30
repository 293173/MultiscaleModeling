import multiprocessing
import os
import tkinter as tk
from collections import Counter, OrderedDict
from itertools import islice
from tkinter import filedialog as fd
import math
from joblib import Parallel, delayed

import numpy as np

from Cell import Cell
import pygame
from pip._vendor.urllib3.connectionpool import xrange
import random
from PIL import Image

if not os.path.exists('res'):
    os.makedirs('res')
size_of_nucleon = 2
def generate_colors():
    for i in range(2, 5000):
        color = list(np.random.choice(range(10, 245), size=3))
        im = Image.new("RGB", (size_of_nucleon, size_of_nucleon), (color[0], color[1], color[2]))
        im.save("res/"+str(i)+".png")
generate_colors()
im = Image.new("RGB", (size_of_nucleon, size_of_nucleon), (0, 0, 0))
im.save("res/0.png")
im = Image.new("RGB", (size_of_nucleon, size_of_nucleon), (255, 255, 255))
im.save("res/1.png")
master = tk.Tk()
pygame.init()
v2 = tk.IntVar()
v2.set(0)
v3 = tk.IntVar()
v3.set(0)
v4 = tk.IntVar()
v4.set(0)
v5 = tk.IntVar()
v5.set(0)
tk.Label(master, text="""Pick CA space size""", font=("Helvetica", 16), justify=tk.LEFT, padx=20).pack()
e1 = tk.Entry(master)
e1.pack()
e1.insert(100, '100')

e2 = tk.Entry(master)
e2.pack()
e2.insert(100, '100')
width = 1
height = 1
speed = 10
screen_size = width, height

screen = pygame.display.set_mode(screen_size)
map_sizey = 0
map_sizex = 0
ilosc_ziaren = 0

colors = []
for i in range(0, 5000):
    #colors.append(pygame.Color((random_color[0], random_color[1], random_color[2])))
    colors.append(pygame.image.load("res/"+str(i)+".png").convert())

warunki = [
    "Absorbing",
    "Periodic"
]

inclusions_start_end = [
    "before growth",
    "after growth",
]

inclusions_type = [
    "circular",
    "square",
]

rule_type= [
    "simple",
    "curvature",
]

e3 = tk.Entry(master)
e4 = tk.Entry(master)
e4 = tk.Entry(master)


def most_frequent(List):
    counter = Counter(List)
    return counter.most_common(2)[0]

def rule_1_fullfilled(List):
    counter = Counter(List)
    size_of_counter_list = len(counter.most_common())
    for i in range(0, size_of_counter_list):
        if counter.most_common(size_of_counter_list)[i][0] != 0 and counter.most_common(size_of_counter_list)[i][1] > 4:
            return True

def rule_2_3_fullfilled(List):
    counter = Counter(List)
    size_of_counter_list = len(counter.most_common())
    for i in range(0, size_of_counter_list):
        if counter.most_common(size_of_counter_list)[i][0] != 0 and counter.most_common(size_of_counter_list)[i][1] > 2:
            return True

def shuffle2d(arr2d, rand=random):
    """Shuffes entries of 2-d array arr2d, preserving shape."""
    reshape = []
    data = []
    iend = 0
    for row in arr2d:
        data.extend(row)
        istart, iend = iend, iend+len(row)
        reshape.append((istart, iend))
    rand.shuffle(data)
    return [data[istart:iend] for (istart, iend) in reshape]

def cell_list(board):
    lst = []
    for i in xrange(map_sizex):
        lst.append([])
        for g in xrange(map_sizey): lst[i].append(
            (board.map[i][g].location[0] * size_of_nucleon, board.map[i][g].location[1] * size_of_nucleon))
    return lst


class Board:

    def __init__(self):
        self.map = []
        self.from_file = False

    def fill(self, ran):
        for i in xrange(map_sizex):
            self.map.append([])
            for g in xrange(map_sizey):
                self.map[i].insert(g, Cell((i, g)))
        if v4.get() == 0:
            self.add_inclusions(int(e4.get()), int(e5.get()))

    def fillRandom(self, ilosc):
        tmp = 0
        while tmp <= ilosc:
            x = random.randint(1, map_sizex - 2)
            y = random.randint(1, map_sizey - 2)
            if self.map[x][y].grain == 0 and self.map[x][y].grain != -1 and self.map[x][y].dualPhased is not True:
                self.map[x][y].grain = tmp
                tmp += 1

    def draw(self, screen):
        for i in xrange(map_sizex):
            for g in xrange(map_sizey):
                self.map[i][g].bordertobe = False
                cell = self.map[i][g]
                loc = cell.location
                if cell.grain > 1 and cell.grain % len(colors) == 0:
                    cell.grain += 1
                if cell.alive:
                    if cell.dualPhased is not False:
                        screen.blit(colors[4999], (loc[0] * size_of_nucleon, loc[1] * size_of_nucleon))
                    elif cell.grain != -1:
                        screen.blit(colors[cell.grain % len(colors) + 1], (loc[0] * size_of_nucleon, loc[1] * size_of_nucleon))
                    else:
                        screen.blit(colors[0],(loc[0] * size_of_nucleon, loc[1] * size_of_nucleon))
                else:
                    if cell.dualPhased is not False:
                        screen.blit(colors[4999],
                                    (loc[0] * size_of_nucleon, loc[1] * size_of_nucleon))
                    elif cell.grain != -1:
                        screen.blit(colors[cell.grain % len(colors) + 1], (loc[0] * size_of_nucleon, loc[1] * size_of_nucleon))
                    else:
                        screen.blit(colors[0], (loc[0] * size_of_nucleon, loc[1] * size_of_nucleon))

    def fill_circle_inclusion(self, x0, y0, radius):
        x = radius
        y = 0
        xchange = 1 - (radius << 1)
        ychange = 0
        radiusError = 0

        while x >= y:
            for i in range(x0 - x, x0 + x+1):
                self.map[i][y0 + y].grain = -1
                self.map[i][y0 - y].grain = -1
                self.map[i][y0 + y].graintobe = -1
                self.map[i][y0 - y].graintobe = -1
            for i in range(x0 - y, x0 + y + 1):
                self.map[i][y0 + x].grain = -1
                self.map[i][y0 - x].grain = -1
                self.map[i][y0 + x].graintobe = -1
                self.map[i][y0 - x].graintobe = -1
            y+=1
            radiusError += ychange
            ychange +=2
            if ((radiusError << 1) + xchange) > 0:
                x-=1
                radiusError += xchange
                xchange += 2

    # def fill_circle_inclusion(self, x, y, r):
    #     PI = 3.1415926535
    #     for i in range(1, 3600):
    #         angle = i / 10
    #         x1 = int(r * math.cos(angle * PI / 180))
    #         y1 = int(r * math.sin(angle * PI / 180))
    #         self.map[x + x1][y + y1].grain = -1
    #         self.map[x + x1][y + y1].graintobe = -1

    def get_cells_moore(self, cell):
        if cell.grain == 0:
            mapa = self.map
            a = []
            b = []
            cell_loc = cell.location

            try:
                a.append(mapa[(cell_loc[0]) % map_sizex][(cell_loc[1] - 1) % map_sizey].location)
                a.append(mapa[(cell_loc[0] - 1) % map_sizex][(cell_loc[1]) % map_sizey].location)
                a.append(mapa[(cell_loc[0] + 1) % map_sizex][(cell_loc[1]) % map_sizey].location)
                a.append(mapa[(cell_loc[0]) % map_sizex][(cell_loc[1] + 1) % map_sizey].location)
                a.append(mapa[(cell_loc[0] - 1) % map_sizex][(cell_loc[1] - 1) % map_sizey].location)
                a.append(mapa[(cell_loc[0] + 1) % map_sizex][(cell_loc[1] + 1) % map_sizey].location)
                a.append(mapa[(cell_loc[0] - 1) % map_sizex][(cell_loc[1] + 1) % map_sizey].location)
                a.append(mapa[(cell_loc[0] + 1) % map_sizex][(cell_loc[1] - 1) % map_sizey].location)
            except Exception:
                pass

            num = len(list(OrderedDict.fromkeys(a)))
            for i in xrange(len(a)):
                if mapa[a[i][0]][a[i][1]].grain != 0 and mapa[a[i][0]][a[i][1]].grain != -1 and mapa[a[i][0]][a[i][1]].dualPhased is not True:
                        b.append(mapa[a[i][0]][a[i][1]].grain)
            if b:
                # if most_frequent(b)[0] != most_frequent(b)[1]:
                tmp = most_frequent(b)[0]
                if self.map[cell_loc[0]][cell_loc[1]].graintobe != -1 or self.map[cell_loc[0]][cell_loc[1]].grain != -1 and mapa[a[i][0]][a[i][1]].dualPhased is not True:
                    self.map[cell_loc[0]][cell_loc[1]].graintobe = tmp

    def get_cells_curvature(self, cell):  # gets the cells around a cell
        if cell.grain == 0:
            mapa = self.map
            a = []
            b = []
            cell_loc = cell.location

            try:
                a.append(mapa[(cell_loc[0]) % map_sizex][(cell_loc[1] - 1) % map_sizey].location)
                a.append(mapa[(cell_loc[0] - 1) % map_sizex][(cell_loc[1]) % map_sizey].location)
                a.append(mapa[(cell_loc[0] + 1) % map_sizex][(cell_loc[1]) % map_sizey].location)
                a.append(mapa[(cell_loc[0]) % map_sizex][(cell_loc[1] + 1) % map_sizey].location)
                a.append(mapa[(cell_loc[0] - 1) % map_sizex][(cell_loc[1] - 1) % map_sizey].location)
                a.append(mapa[(cell_loc[0] + 1) % map_sizex][(cell_loc[1] + 1) % map_sizey].location)
                a.append(mapa[(cell_loc[0] - 1) % map_sizex][(cell_loc[1] + 1) % map_sizey].location)
                a.append(mapa[(cell_loc[0] + 1) % map_sizex][(cell_loc[1] - 1) % map_sizey].location)
            except Exception:
                pass

            for i in xrange(len(a)):
                if mapa[a[i][0]][a[i][1]].grain != 0 and mapa[a[i][0]][a[i][1]].grain != -1 and mapa[a[i][0]][a[i][1]].dualPhased is not True:
                        b.append(mapa[a[i][0]][a[i][1]].grain)
            if b:
                if rule_1_fullfilled(b):
                    self.map[cell_loc[0]][cell_loc[1]].graintobe = most_frequent(b)[0]
                    return

            a = []
            b = []

            try:
                a.append(mapa[(cell_loc[0]) % map_sizex][(cell_loc[1] - 1) % map_sizey].location)
                a.append(mapa[(cell_loc[0] - 1) % map_sizex][(cell_loc[1]) % map_sizey].location)
                a.append(mapa[(cell_loc[0] + 1) % map_sizex][(cell_loc[1]) % map_sizey].location)
                a.append(mapa[(cell_loc[0]) % map_sizex][(cell_loc[1] + 1) % map_sizey].location)
            except Exception:
                pass

            for i in xrange(len(a)):
                if mapa[a[i][0]][a[i][1]].grain != 0 and mapa[a[i][0]][a[i][1]].grain != -1 and mapa[a[i][0]][a[i][1]].dualPhased is not True:
                    b.append(mapa[a[i][0]][a[i][1]].grain)
            if b:
                if rule_2_3_fullfilled(b):
                    self.map[cell_loc[0]][cell_loc[1]].graintobe = most_frequent(b)[0]
                    return

            a = []
            b = []

            try:
                a.append(mapa[(cell_loc[0] - 1) % map_sizex][(cell_loc[1] - 1) % map_sizey].location)
                a.append(mapa[(cell_loc[0] + 1) % map_sizex][(cell_loc[1] + 1) % map_sizey].location)
                a.append(mapa[(cell_loc[0] - 1) % map_sizex][(cell_loc[1] + 1) % map_sizey].location)
                a.append(mapa[(cell_loc[0] + 1) % map_sizex][(cell_loc[1] - 1) % map_sizey].location)
            except Exception:
                pass

            for i in xrange(len(a)):
                if mapa[a[i][0]][a[i][1]].grain != 0 and mapa[a[i][0]][a[i][1]].grain != -1 and mapa[a[i][0]][a[i][1]].dualPhased is not True:
                        b.append(mapa[a[i][0]][a[i][1]].grain)
            if b:
                if rule_2_3_fullfilled(b):
                    self.map[cell_loc[0]][cell_loc[1]].graintobe = most_frequent(b)[0]
                    return

            a = []
            b = []

            try:
                x = random.randint(1, 100)
                if x <= int(e6.get()):
                    a.append(mapa[(cell_loc[0] - 1) % map_sizex][(cell_loc[1] - 1) % map_sizey].location)
                    a.append(mapa[(cell_loc[0] + 1) % map_sizex][(cell_loc[1] + 1) % map_sizey].location)
                    a.append(mapa[(cell_loc[0] - 1) % map_sizex][(cell_loc[1] + 1) % map_sizey].location)
                    a.append(mapa[(cell_loc[0] + 1) % map_sizex][(cell_loc[1] - 1) % map_sizey].location)
                    a.append(mapa[(cell_loc[0]) % map_sizex][(cell_loc[1] - 1) % map_sizey].location)
                    a.append(mapa[(cell_loc[0] - 1) % map_sizex][(cell_loc[1]) % map_sizey].location)
                    a.append(mapa[(cell_loc[0] + 1) % map_sizex][(cell_loc[1]) % map_sizey].location)
                    a.append(mapa[(cell_loc[0]) % map_sizex][(cell_loc[1] + 1) % map_sizey].location)
            except Exception:
                    pass

            num = len(list(OrderedDict.fromkeys(a)))
            for i in xrange(len(a)):
                if mapa[a[i][0]][a[i][1]].grain != 0 and mapa[a[i][0]][a[i][1]].grain != -1 and mapa[a[i][0]][a[i][1]].dualPhased is not True:
                        b.append(mapa[a[i][0]][a[i][1]].grain)
            if b:
                # if most_frequent(b)[0] != most_frequent(b)[1]:
                tmp = most_frequent(b)[0]
                if self.map[cell_loc[0]][cell_loc[1]].graintobe != -1 or self.map[cell_loc[0]][cell_loc[1]].grain != -1 and mapa[a[i][0]][a[i][1]].dualPhased is not True:
                    self.map[cell_loc[0]][cell_loc[1]].graintobe = tmp

    def update_frame(self, border):
        if border:
            if v3.get() == 1:
                for i in xrange(map_sizex):
                    for g in xrange(map_sizey):
                        cell = self.map[i][g]
                        self.get_cells_curvature(cell)
            else:
                for i in xrange(map_sizex):
                    for g in xrange(map_sizey):
                        cell = self.map[i][g]
                        self.get_cells_moore(cell)
        else:
            if v3.get() == 1:
                for i in xrange(0, map_sizex - 1):
                    for g in xrange(0, map_sizey - 1):
                        cell = self.map[i][g]
                        self.get_cells_curvature(cell)
            else:
                for i in xrange(0, map_sizex - 1):
                    for g in xrange(0, map_sizey - 1):
                        cell = self.map[i][g]
                        self.get_cells_moore(cell)

    def update(self, border, screen):
        if border:
            for i in xrange(map_sizex):
                for g in xrange(map_sizey):
                    cell = self.map[i][g]
                    cell.grain = cell.graintobe
                    loc = cell.location
                    if cell.dualPhased is not False:
                        screen.blit(colors[4999],
                                    (loc[0] * size_of_nucleon, loc[1] * size_of_nucleon))
                    elif cell.grain != -1:
                        screen.blit(colors[cell.grain % len(colors) + 1], (loc[0] * size_of_nucleon, loc[1] * size_of_nucleon))
                    else:
                        screen.blit(colors[0], (loc[0] * size_of_nucleon, loc[1] * size_of_nucleon))
        else:
            for i in xrange(1, map_sizex - 1):
                for g in xrange(1, map_sizey - 1):
                    cell = self.map[i][g]
                    cell.grain = cell.graintobe
                    loc = cell.location
                    if cell.dualPhased is not False:
                        screen.blit(colors[4999],
                                    (loc[0] * size_of_nucleon, loc[1] * size_of_nucleon))
                    elif cell.grain != -1:
                        screen.blit(colors[cell.grain% len(colors) + 1], (loc[0] * size_of_nucleon, loc[1] * size_of_nucleon))
                    else:
                        screen.blit(colors[0], (loc[0] * size_of_nucleon, loc[1] * size_of_nucleon))

    def add_inclusions(self, inclusion_number, inclusion_size):
        tmp = 0
        while tmp <= inclusion_number:
            x = random.randint(1, map_sizex - 2 - inclusion_size)
            y = random.randint(1, map_sizey - 2 - inclusion_size)
            for i in range(0, inclusion_size):
                for j in range(0, inclusion_size):
                    if v5.get() == 0:
                        self.fill_circle_inclusion(x, y, int(inclusion_size/2))
                    else:
                        self.map[x+i][y+j].grain = -1
                        self.map[x+i][y+j].graintobe = -1
            tmp += 1

    def find_borders(self):
        for i in xrange(map_sizex):
            for g in xrange(map_sizey):
                cell = self.map[i][g]
                mapa = self.map
                cell_loc = cell.location
                self.map[cell_loc[0]][cell_loc[1]].bordertobe = False
                a = [mapa[(cell_loc[0] - 1) % map_sizex][(cell_loc[1] - 1) % map_sizey].location,
                     mapa[(cell_loc[0] + 1) % map_sizex][(cell_loc[1] + 1) % map_sizey].location,
                     mapa[(cell_loc[0] - 1) % map_sizex][(cell_loc[1] + 1) % map_sizey].location,
                     mapa[(cell_loc[0] + 1) % map_sizex][(cell_loc[1] - 1) % map_sizey].location,
                     mapa[(cell_loc[0]) % map_sizex][(cell_loc[1] - 1) % map_sizey].location,
                     mapa[(cell_loc[0] - 1) % map_sizex][(cell_loc[1]) % map_sizey].location,
                     mapa[(cell_loc[0] + 1) % map_sizex][(cell_loc[1]) % map_sizey].location,
                     mapa[(cell_loc[0]) % map_sizex][(cell_loc[1] + 1) % map_sizey].location]
                for k in xrange(len(a)):
                    if mapa[a[k][0]][a[k][1]].grain != cell.grain:
                        self.map[cell_loc[0]][cell_loc[1]].bordertobe = True

    def add_inclusions_at_borders(self, inclusion_number, inclusion_size):
        print("ADDING")
        self.find_borders()
        a = []
        for i in xrange(inclusion_size*2, map_sizex - 2 - inclusion_size):
            for g in xrange(inclusion_size*2, map_sizex - 2 - inclusion_size):
                if self.map[i][g].bordertobe:
                    a.append(self.map[i][g].location)
        random.shuffle(a)

        tmp = 0
        while tmp <= inclusion_number:
            cell_loc = a.pop()
            for i in range(0, inclusion_size):
                for j in range(0, inclusion_size):
                    if v5.get() == 0:
                        self.fill_circle_inclusion(cell_loc[0], cell_loc[1], int(inclusion_size/2))
                    else:
                        self.map[cell_loc[0]+i][cell_loc[1]+j].grain = -1
                        self.map[cell_loc[0]+i][cell_loc[1]+j].graintobe = -1
            tmp += 1

    def draw_borders(self):
        self.find_borders()
        for i in xrange(map_sizex):
            for g in xrange(map_sizey):
                cell = self.map[i][g]
                loc = cell.location
                if cell.bordertobe:
                    screen.blit(colors[0], (loc[0] * size_of_nucleon, loc[1] * size_of_nucleon))
                else:
                    screen.blit(colors[1], (loc[0] * size_of_nucleon, loc[1] * size_of_nucleon))

    def phase_grain_from_id(self, grain_id):
        for i in xrange(map_sizex):
            for g in xrange(map_sizey):
                if self.map[i][g].grain == grain_id and self.map[i][g].grain != 0 and self.map[i][g].grain != -1:
                    self.map[i][g].dualPhased = True
                    self.map[i][g].grain = 5000

    def clear_for_dual_phase(self):
        for i in xrange(map_sizex):
            for g in xrange(map_sizey):
                if self.map[i][g].grain != -1:
                    self.map[i][g].grain = 0
                    self.map[i][g].graintobe = 0



board = Board()


def save_to_file():
    filename = fd.asksaveasfilename(filetypes=[("Plik tekstowy", "*.txt")],
                                    defaultextension="*.txt")
    if filename:
        with open(filename, "w", -1, "utf-8") as file:
            file.write(str(map_sizex)+' '+str(map_sizey)+'\n')
            for i in xrange(map_sizex):
                for g in xrange(map_sizey):
                    cell = board.map[i][g]
                    loc = cell.location
                    file.write(str(loc[0])+" "+str(loc[1])+' '+' '+'0'+' '+str(cell.grain) + '\n')


def draw_from_file():
    board.from_file = True
    go()
def run_simulation():
    board.from_file = False
    go()

def go():
    done = False
    if not board.from_file:
        global map_sizex
        global map_sizey
        global ilosc_ziaren
        map_sizey = int(e2.get())
        if map_sizey > 1000:
            map_sizey = 1000
        map_sizex = int(e1.get())
        if map_sizex > 1000:
            map_sizex = 1000
        ilosc_ziaren = int(e3.get())
        if ilosc_ziaren < 1:
            ilosc_ziaren = 1
        width = map_sizex * size_of_nucleon
        height = map_sizey * size_of_nucleon
        screen_size = width, height
        screen = pygame.display.set_mode(screen_size)
        clock = pygame.time.Clock()
        manual = False
        licznik = 0
        board.fill(False)
        board.fillRandom(ilosc_ziaren)
    else:
        filename = fd.askopenfilename(filetypes=[("Plik tekstowy", "*.txt")])
        board.from_file = True
        if filename:
            with open(filename, "r") as file:
                first_line = file.readline()
                size_values = first_line.split()
                map_sizey = int(size_values[0])
                map_sizex = int(size_values[1])
                ilosc_ziaren = 0
                print(map_sizey,map_sizex)
                width = map_sizex * size_of_nucleon
                height = map_sizey * size_of_nucleon
                screen_size = width, height
                screen = pygame.display.set_mode(screen_size)
                clock = pygame.time.Clock()
                manual = False
                board.fill(False)
                for aline in islice(file, 1, map_sizey*map_sizex - 1):
                    values = aline.split()
                    board.map[int(values[0])][int(values[1])].grain = int(values[3])
                    board.map[int(values[0])][int(values[1])].graintobe = board.map[int(values[0])][int(values[1])].grain

    board.draw(screen)
    tp = 0
    run = False
    while not done:

        milliseconds = clock.tick(60)
        tp += milliseconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    run = not run
                if event.key == pygame.K_b:
                    run = False
                    board.draw_borders()
                if event.key == pygame.K_i:
                    run = False
                    board.add_inclusions_at_borders(int(e4.get()), int(e5.get()))
                if event.key == pygame.K_d:
                    run = False
                    board.clear_for_dual_phase()
                    board.draw(screen)
                    board.fillRandom(ilosc_ziaren)
            if event.type == pygame.MOUSEBUTTONUP:
                for i in xrange(map_sizex):
                    for g in xrange(map_sizey):
                        board.map[i][g].pressed = False

        mouse = pygame.mouse.get_pressed()
        pos = pygame.mouse.get_pos()

        if run == True and tp >= 1000 / speed:
            tp = 0
            board.update_frame(v2.get)
            board.update(v2.get(), screen)

        if mouse[0]:  # makes cells alive
            rects = cell_list(board)
            for i in xrange(map_sizex):
                for g in xrange(map_sizey):
                    if rects[i][g][0] <= pos[0] < rects[i][g][0] + size_of_nucleon and rects[i][g][1] <= pos[1] < \
                            rects[i][g][
                                1] + \
                            size_of_nucleon and board.map[i][g].pressed is False:
                        licznik += 1
                        grain_id_to_phase = board.map[i][g].grain
                        board.phase_grain_from_id(grain_id_to_phase)
                        board.draw(screen)

        if mouse[2]:  # kills cells
            rects = cell_list(board)
            for i in xrange(map_sizex):
                for g in xrange(map_sizey):
                    if rects[i][g][0] <= pos[0] < rects[i][g][0] + size_of_nucleon and rects[i][g][1] <= pos[1] < \
                            rects[i][g][1] + size_of_nucleon and board.map[i][g].pressed is False:
                        licznik -= 1
                        board.map[i][g].grain = 0
                        board.map[i][g].graintobe = 0
                        board.map[i][g].pressed = False
                        board.update(v2.get(), screen)

        pygame.display.flip()

    pygame.quit()
tk.Label(master, text="""Number of nucleons""", font=("Helvetica", 16), justify=tk.LEFT, padx=20).pack()
e3 = tk.Entry(master)
e3.pack()
e3.insert(0, '100')

tk.Label(master, text="""Number of inclusions""", font=("Helvetica", 16), justify=tk.LEFT, padx=20).pack()
e4 = tk.Entry(master)
e4.pack()
e4.insert(0, '0')

tk.Label(master, text="""Size of inclusions""", font=("Helvetica", 16), justify=tk.LEFT, padx=20).pack()
e5 = tk.Entry(master)
e5.pack()
e5.insert(0, '0')

tk.Label(master, text="""Inclusion insertion time""", font=("Helvetica", 16), justify=tk.LEFT, padx=20).pack()
for val4, inclusion_moment in enumerate(inclusions_start_end):
    tk.Radiobutton(master,
                   text=inclusion_moment,
                   indicatoron=0,
                   width=40,
                   padx=20,
                   variable=v4,
                   value=val4).pack(anchor=tk.W)

tk.Label(master, text="""Inclusion shape""", font=("Helvetica", 16), justify=tk.LEFT, padx=20).pack()
for val5, inclusion_shape in enumerate(inclusions_type):
    tk.Radiobutton(master,
                   text=inclusion_shape,
                   indicatoron=0,
                   width=40,
                   padx=20,
                   variable=v5,
                   value=val5).pack(anchor=tk.W)

tk.Label(master, text="""choose boundary condition""", font=("Helvetica", 16), justify=tk.LEFT, padx=20).pack()
for val2, warunek in enumerate(warunki):
    tk.Radiobutton(master,
                   text=warunek,
                   indicatoron=0,
                   width=40,
                   padx=20,
                   variable=v2,
                   value=val2).pack(anchor=tk.W)

tk.Label(master, text="""choose grain curvature type""", font=("Helvetica", 16), justify=tk.LEFT, padx=20).pack()
for val3, rules in enumerate(rule_type):
    tk.Radiobutton(master,
                   text=rules,
                   indicatoron=0,
                   width=40,
                   padx=20,
                   variable=v3,
                   value=val3).pack(anchor=tk.W)
tk.Label(master, text="""probability""", font=("Helvetica", 16), justify=tk.LEFT, padx=20).pack()
e6 = tk.Entry(master)
e6.pack()
e6.insert(100, '100')

tk.Label(master, text="""select option""", font=("Helvetica", 16), justify=tk.LEFT, padx=20).pack()
tk.Button(master, text="START", width=45, command=run_simulation).pack()
tk.Button(text="save to txt file", width=45, command=save_to_file).pack()
tk.Button(text="laod from txt file", width=45, command=draw_from_file).pack()

tk.Label(master, text="""I - add inclusions""", font=("Helvetica", 16), justify=tk.LEFT, padx=20).pack()
tk.Label(master, text="""SPACE - start animation""", font=("Helvetica", 16), justify=tk.LEFT, padx=20).pack()
tk.Label(master, text="""B - show borders""", font=("Helvetica", 16), justify=tk.LEFT, padx=20).pack()
tk.Label(master, text="""D - dualPhase""", font=("Helvetica", 16), justify=tk.LEFT, padx=20).pack()
master.mainloop()


def clear_colors():
    folder = 'res/'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

clear_colors()

