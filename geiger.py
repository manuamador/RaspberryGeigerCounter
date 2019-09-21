import time
import timeit
from datetime import datetime
import RPi.GPIO as GPIO
from PIL import ImageFont
from luma.core.interface.serial import i2c,spi
from luma.core.render import canvas
from luma.oled.device import sh1106
import numpy as np
import os


serial = i2c(port=1, address=0x3C)
device = sh1106(serial)


GPIO.setmode(GPIO.BOARD)
GPIO.setup(15,GPIO.IN,pull_up_down=GPIO.PUD_UP)
timespan=60
counter=0
hist=np.zeros(128)

nb_mes=0
nb_coups=0

def make_font(name, size):
    font_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'fonts', name))
    return ImageFont.truetype(font_path, size)


fontsize=8
font = make_font("tiny.ttf",  6)
fontl = make_font("C&C Red Alert [INET].ttf", 24)

def tube_impulse_callback(channel):
	global counter
	global nb_coups
	counter+=1
	nb_coups+=1

GPIO.add_event_detect(15,GPIO.FALLING,callback=tube_impulse_callback,bouncetime=500)


with canvas(device) as draw:
        dtheure=datetime.now().isoformat()
        draw.text((0,0),dtheure[0:10]+' '+dtheure[11:16],fill='white')
        draw.text((0,8),'---',font=fontl,fill='white')
	draw.text((28,8),'CPM',font=fontl,fill='white')
	draw.text((68,17),'MAX: 0',fill='white')
	draw.text((68,9),'AVG: 0',fill='white')
	draw.text((120,24),'0',font=font,fill='white')
	draw.text((64,59),'1h',font=font,fill='white')
        draw.text((4,59),'2h',font=font,fill='white')

max_coup=-1
try:
	while True:
		time.sleep(timespan)
		cpm=int(counter*60/timespan)
		if cpm>max_coup:
			max_coup=cpm
		hist[0]=cpm
		nb_mes+=1
		hist=np.roll(hist,-1)
		with canvas(device) as draw:
			cpm=int(counter*60/timespan)
			dtheure=datetime.now().isoformat()
			draw.text((0,0),dtheure[0:10]+' '+dtheure[11:16],fill='white')
			draw.text((0,8),str(cpm),font=fontl,fill='white')
			draw.text((28,8),'CPM',font=fontl,fill='white')
			draw.text((68,9),'AVG: '+str(round(nb_coups/nb_mes,1)),fill='white')
			draw.text((68,17),'MAX: '+str(max_coup),fill='white')
			h_max=hist.max()
			draw.text((120,24),str(int(h_max)),font=font,fill='white')
			draw.text((64,59),'1h',font=font,fill='white')
			draw.text((4,59),'2h',font=font,fill='white')
			for i in range(128):
				draw.line((i,58,i,58-int(round(hist[i]/h_max*26))),fill='white')
		counter=0

except KeyboardInterrupt:
	print ('kb interrupt')
	GPIO.cleanup()
except:
	print ('erreur')
	GPIO.cleanup()
