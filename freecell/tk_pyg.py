import pygame
from pygame.locals import *
import tkinter as tk
from tkinter import *
import os
import sys


root = tk.Tk()

embed = tk.Frame(root, width = 500, height = 500) #creates embed frame for pygame window
embed.grid(columnspan = (700), rowspan = 500) # Adds grid
embed.pack(side = LEFT) #packs window to the left

buttonwin = tk.Frame(root, width = 175, height = 500)
buttonwin.pack(side = RIGHT)

os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
os.environ['SDL_VIDEODRIVER'] = 'windib'

screen = pygame.display.set_mode((500,500))
screen.fill(pygame.Color(255,255,255))

pygame.display.init()
pygame.display.update()


def draw():
    pygame.draw.circle(screen, (0,0,0), (250,250), 125)
    pygame.display.update()


button1 = Button(buttonwin,text = 'Draw',  command=draw)
button1.pack(side=TOP)
button2 = Button(buttonwin,text = 'next',  command=draw)
button2.pack(side=BOTTOM)
button3 = Button(buttonwin,text = 'next3',  command=draw)
button3.pack(side=BOTTOM)

root.update()

cnt = 0
while True:
    for event in pygame.event.get():
        if event.type==QUIT:
            print("QUIT")
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            key_pressed = pygame.key.get_pressed()
            if key_pressed[K_UP]:
                print("key up")
            elif key_pressed[K_DOWN]:
                print("key down")
            elif key_pressed[K_LEFT]:
                print("key left")
            elif key_pressed[K_RIGHT]:
                print("key right")
            else:
                print("A")

    cnt +=1
    if cnt % 10000 == 0:
        print(cnt)
    pygame.display.update()
    root.update()