import socket
import RPi.GPIO as GPIO
import time
import sys
import os
import blynklib

BLYNK_AUTH = 'H_nfPJMaB7T6BZeLmnaHDeJ3YeSBzZeS' #insert your Auth Token here
BLYNK_BUTTON_VPIN = 0
BLYNK_LED_VPIN = 1
blynk = blynklib.Blynk(BLYNK_AUTH)

RASPBERRY_PI_IP ="192.168.1.23"
LAPTOP_IP = "192.168.1.8"

TCP_IP = LAPTOP_IP # this IP of my pc. When I want raspberry pi 2`s as a client, I replace it with its IP '169.254.54.195'
TCP_PORT = 5005
BUFFER_SIZE = 1024

MESSAGE = "Hello, World!"

sensor_calibration_time = 0
socket_connection_retry_time = 2

alarm_enabled = True
s = None
socket_connected = False
blynk_init = False

def setup_gpio():
	GPIO.setwarnings(True)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(18,GPIO.OUT)     
	GPIO.setup(23, GPIO.IN)   
	
def setup_socket():
	global s
	global socket_connected
	try: 
		print("\nTrying to connect to socket on "+str(LAPTOP_IP))
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((TCP_IP, TCP_PORT))
		socket_connected = True
		print("Laptop connected!")
	except Exception as e:
		print("Exception: " +str(e))
	# s.send(MESSAGE)
	# data = s.recv(BUFFER_SIZE)
	# print ("received data:", data)
	# s.close()
	
def init_blynk():	
	global blynk_init
	if blynk is not None:
		print("Resetting blynk states")
		blynk_init = True
		blynk.virtual_write(BLYNK_BUTTON_VPIN, alarm_enabled*255)
		blynk.virtual_write(BLYNK_LED_VPIN, 0)

"""
This handler starts everytime something is written on the pin V0 (e.g button is pressed and its value changes)
"""	
@blynk.handle_event('write V0')
def button_pressed_handler(pin, value):
	global alarm_enabled
	alarm_enabled = bool(int(value[0]))
	if alarm_enabled:
		print("Alarm Enabled")
	else:
		print("Alarm Disabled")


def print_counter(start_msg = "", end_msg="", secs=10):
	for i in range(secs):
			time.sleep(1)
			print(str(10-i), end= " ", flush=True)
	
def loop(socket=None):	
	global alarm_enabled
	global socket_connected
	intruder = False
	stabilising_sensor_time = 0
	last_connection_time = time.time()
	last_time = time.time()
	sensor_stabilised = False
	try:
		while True:	
			blynk.run()
			if not blynk_init:
				init_blynk()
			if not sensor_stabilised:
				if stabilising_sensor_time <= 0:
					print("Stabilising sensor", end="", flush=True)	
					stabilising_sensor_time = time.time()
				elif time.time() - stabilising_sensor_time < sensor_calibration_time:	
					if time.time() - last_time >= 1:
						print(".", end="", flush=True)
						last_time = time.time()
				else:
					sensor_stabilised = True
				continue
				
			if not socket_connected:
				if time.time() - last_connection_time >= socket_connection_retry_time:
					last_connection_time = time.time()
					setup_socket()
			else:
				if s is not None:
					try:
						s.send('0'.encode())
					except Exception as e:
						if socket_connected:
							print("Connection dropped. RECV Exception : "+str(e))
						socket_connected = False
				
			if alarm_enabled and GPIO.input(23):
				if not intruder:
					intruder = True
					GPIO.output(18,1)
					print('INTRUDER')
					if socket_connected:
						try:
							s.send('1'.encode())
						except Exception as e:
							socket_connected = False
					blynk.virtual_write(BLYNK_LED_VPIN, 255)
					print("Notifying blynk")
					blynk.notify('INTRUDER ALERT!') # send push notification to Blynk App 
					# wait_time = 5
					# print_counter("Waiting " +str(wait_time) +" seconds... ", "", wait_time)
			else:
				intruder = False
				GPIO.output(18,0)	
				blynk.virtual_write(BLYNK_LED_VPIN, 0)
			time.sleep(0.1)
	except Exception as e:
		print(e)
		GPIO.cleanup()
		s.close()




if __name__=="__main__":
	setup_gpio()
	loop()
