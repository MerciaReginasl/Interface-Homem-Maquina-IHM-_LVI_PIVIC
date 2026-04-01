import matplotlib.pyplot as plt
import RPi.GPIO as GPIO
from time import time
import numpy as np

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(14, GPIO.IN)

cont = 0
velocity = []
ctrl = []

while 1:
    try:
        delta = float(input("Digite o tempo de leitura da rampa (em segundos):\n-> "))
        break
    except:
        print("\nErro! O valor de entrada não é um número!\n")

print("Start")
start_time = runup_start = time()

while time()-runup_start < delta:
    if GPIO.input(14)==1:
        cont+=1
        while GPIO.input(14)==1:
            pass
    t = time()-start_time
    if t >= 0.2:
        ctrl.append(cont*300//(t*5))
        cont=0

        if len(ctrl)==5:
            velocity.append(int(np.average(ctrl)))
            ctrl = []
        start_time = time()

print("Break")

x = np.linspace(0, len(velocity)+1, len(velocity))

name = input("Como deseja salvar o seu arquivo? ")

np.savetxt(name, velocity, newline="\n")
np.savetxt(name + "_time", x, newline="\n")



plt.figure(1)
plt.plot(x, velocity, 'r')
plt.title("Runup", size=27)
plt.xlabel("Time execute, (s)", size=23)
plt.ylabel("Velocity (RPM)", size=23)
plt.show()
