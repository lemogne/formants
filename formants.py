#!/usr/bin/python3
import pygame as pg
import pyaudio as a
import numpy as np

resolution = (800, 600)

pg.init()
pg.display.init()
#pg.display.set_icon(pg.image.load("icon.ico"))
pg.display.set_caption("Formants")
screen = pg.display.set_mode(resolution)

background=pg.image.load("background.png")
background = pg.transform.scale(background, resolution)
backg=background.get_rect()
screen.blit(background, (0, 0))
pg.display.flip()

p=a.PyAudio()

frames_in_buffer = 1024

stream = p.open(format=a.paFloat32,
				channels=1,
				rate=44100,
				output=True,
				frames_per_buffer=frames_in_buffer)

def quit_program():
	stream.close()
	p.terminate()
	pg.quit()
	quit()

def freq(coords):
	norm_x = 1 - (coords[0] / resolution[0])
	norm_y = coords[1] / resolution[1]
	return np.array((100 + 20 * norm_x, norm_y * 900 + 100, norm_x * 2400 + 300, 300 * norm_x + 2400))

def ampl(coords):
	norm_x = 1 - (coords[0] / resolution[0])
	norm_y = coords[1] / resolution[1]
	return (0.1, 0.25 * norm_y - 0.1 * norm_x + 0.2, 0.04 * norm_x - 0.06 * norm_y + 0.05, 0.02 * norm_x)

t = np.arange(frames_in_buffer * 4)

def play(pos, s, loudness):
	def wave(t, i):
		return np.sin(2 * np.pi * (t + i))
	def base(t):
		return np.abs(np.clip(t & 255, 0, 127) - 64) / 63		# Trapezoid wave
		#return ((t & 256 == 0).astype(np.int8) * 2) - 1		# Square wave
		#return np.abs((t & 255) - 128) / 127					# Sawtooth wave
	freqs = freq(pos)
	f = ampl(pos)
	y = (sum(f[i] * wave(freqs[i] * t / 44100, s[i]) for i in range(4)) * base(t)) * loudness
	stream.write(y.astype(np.float32))
	return s + freqs * frames_in_buffer / 44100

s = np.array([0, 0, 0, 0])
playing = False
while True:
	for e in pg.event.get():
		if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE or e.type == pg.QUIT:
			quit_program()
		elif e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
			playing = True
		elif e.type == pg.MOUSEBUTTONUP and e.button == 1:
			playing = False
	if playing:
		s = play(pg.mouse.get_pos(), s, 1)
	else:
		stream.write(np.zeros(frames_in_buffer))

