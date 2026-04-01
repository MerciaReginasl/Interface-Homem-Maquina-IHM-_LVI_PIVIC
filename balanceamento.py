#ACCEL -> I2C
#TACHO -> 15

def Fast_Fuorier_Transform(x, fs):

    n = len(x)
    #Signal fft calculation
    fft = sc.fft(x)

    #Amplitude vector
    amp = abs(fft)[:n // 2] * 1 / n

    #Frequency vector
    freqs = abs(sc.fftfreq(len(fft))*fs)

    Xf = freqs[:len(amp)]
    Yf = amp

    return Xf, Yf



import smbus
import time
import RPi.GPIO as gpio
import matplotlib.pyplot as plt
import numpy as np
import scipy.fft as sc
from scipy.signal import butter, lfilter, freqz
import csv
import math

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)
gpio.setup(15, gpio.IN)

amostras = 2**13
tempo_total = 0
periodo = 0
taxa_de_amostragem = 0
AzCal = 0
Az = 0
z = []
magReaction = []
ir = []

PWR_M = 0x6B
DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_EN = 0x38
ACCEL_X = 0x3B
ACCEL_Y = 0x3D
ACCEL_Z = 0x3F
bus = smbus.SMBus(1)
Device_Address = 0x68 
RS = 18
EN = 23
D4 = 24
D5 = 25
D6 = 8
D7 = 7
 
def IniciaMPU():
    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    gpio.setup(RS, gpio.OUT)
    gpio.setup(EN, gpio.OUT)
    gpio.setup(D4, gpio.OUT)
    gpio.setup(D5, gpio.OUT)
    gpio.setup(D6, gpio.OUT)
    gpio.setup(D7, gpio.OUT)
    bus.write_byte_data(Device_Address, DIV, 7)
    bus.write_byte_data(Device_Address, PWR_M, 1)
    bus.write_byte_data(Device_Address, CONFIG, 0)
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
    bus.write_byte_data(Device_Address, INT_EN, 1)
    time.sleep(1)

def lerMPU(addr):
    high = bus.read_byte_data(Device_Address, addr)
    value = high << 8
    if(value > 32768):
        value = value - 65536
    return value

def calibrar():
    global AzCal
    ztemp=0
    for i in range(200):
        ztemp = ztemp + lerMPU(ACCEL_Z)
    ztemp= ztemp/200 #calcula o nivel dc do sinal
    AzCal = ztemp#/16384.0 #divide pelo fator de escala do mpu em 2g
 
def LerAcel():
    global Az
    ztemp = lerMPU(ACCEL_Z)
    Az = (ztemp-(AzCal)) #divide pelo fator de escala do mpu e subtrai a media para retirar o nivel dc do sinal

def gravar():
    global z, tempo_total
    del z[:]
    tempo_inicial = time.time()
    '''for i in range(amostras): 
        LerAcel()
        z.append(Az)
    tempo_total = time.time() - tempo_inicial'''
    initial_time = time.time()
    while time.time()-initial_time <10:
        LerAcel()
        z.append(Az)#SALVAR
     
def coletaMPU():
    global amostras, taxa_de_amostragem, periodo, tempo_total
    IniciaMPU()
    calibrar()
    gravar()
    amostras = len(z)
    tempo_total = 10
    periodo = tempo_total/amostras
    taxa_de_amostragem = 1/periodo

#filtro passa banda
sinalfiltrado = 0
def filtro(x):
    global taxa_de_amostragem, sinalfiltrado
    fL = 40/taxa_de_amostragem #nivel baixo
    fH = 60/taxa_de_amostragem #nivel alto
    m = 25/taxa_de_amostragem
    N = int(np.ceil((4 / m)))
    if not N % 2: N +=1
    n = np.arange(N)

    #passa baixa
    hlpf = np.sinc(2*fH*(n-(N-1) // 2.))
    hlpf *= np.blackman(N)
    hlpf = hlpf / np.sum(hlpf)

    #passa alta
    hhpf = np.sinc(2*fL*(n-(N-1) // 2.))
    hhpf *= np.blackman(N)
    hhpf = hhpf / np.sum(hhpf)
    hhpf = -hhpf
    hhpf[(N - 1)//2] += 1

    #convolução
    h = np.convolve(hlpf, hhpf)
    sinalfiltrado = np.convolve(x, h) #aplicando filtro

def coletaIR():
    global ir
    start_time = time.time()
    while time.time()-start_time<10:
            ir.append(int(gpio.input(15)))

#calcula a magnitude do vetor
def magnitude(vector): 
    return math.sqrt(sum(pow(element, 2) for element in vector))

#encontra o periodo da onda quadrada
Pir = []
def P_ir(x):
    global Pir
    a = 0
    for i in range(len(x)):
        if x[i] == 0.0 and x[i+1] == 1.0:
            a = i+1
            break
    b = 0
    for i in range(a+1, len(x)):
        if x[i] == 0.0 and x[i+1] == 1.0:
            b = i+1
            break
    Pir.append(a)
    Pir.append(b)

#encontra o periodo da onda senoidal filtrada
Pmpu = []
def P_mpu(x):
    global Pmpu
    c = 0
    for i in range(len(x)//2, len(x)):
        if x[i] < x[i+1] and x[i+1] > x[i+2]:
            c = i+1
            break
    d = 0
    for i in range(c, len(x)):
        if x[i] < x[i+1] and x[i+1] > x[i+2]:
            d = i+1
            break
    Pmpu.append(c)
    Pmpu.append(d)

i = 1
intensidades = []
fases = []
while i<10:
    amostras = 2**13
    tempo_total = 0
    periodo = 0
    taxa_de_amostragem = 0
    AzCal = 0
    Az = 0
    z = []
    ir = []
    Pir = []
    mpu = []
    
    coletaMPU()
    filtro(z)
    P_mpu(sinalfiltrado)
    coletaIR()
    P_ir(ir)

    tmpu = np.linspace(0, 10, len(sinalfiltrado))
    tir = np.linspace(0, 10, len(ir))

    delta_mpu = tmpu[Pmpu[1]] - tmpu[Pmpu[0]]
    delta_ir = tir[Pir[1]] - tir[Pir[0]]

    P = abs(delta_mpu - delta_ir)
    fase = round(360*P/delta_ir, 0)
        
    print("Reação do mancal:", magnitude(z))
    print('taxa de amostragem: ', taxa_de_amostragem)
    name = input('digute o nome do arquivo: ')
    np.savetxt(name+'.txt', z, delimiter='\n')
    print("Fase:", fase, "°")

    Xf = Fast_Fuorier_Transform(z, taxa_de_amostragem)[0]
    Yf = Fast_Fuorier_Transform(z, taxa_de_amostragem)[1]

    plt.figure(1)
    plt.plot(Xf, Yf)
    plt.show()
    
    #mostra os pontos dos periodos dos sinais
    plt.figure(1)
    plt.plot(tir, ir)
    plt.plot(tir[Pir[0]], 0, 'o', color='r')
    plt.plot(tir[Pir[1]], 0, 'o', color='r')
    plt.title('Tacho', fontsize=20)
    plt.grid()

    plt.figure(2)
    plt.plot(tmpu, sinalfiltrado)
    plt.plot(tmpu[Pmpu[0]], 0, 'o', color='r')
    plt.plot(tmpu[Pmpu[1]], 0, 'o', color='r')
    plt.title('Accel', fontsize=20)
    plt.grid()
    plt.show()
    
    intensidades.append(magnitude(sinalfiltrado))
    fases.append(fase)
    pausa = input("Tecle para continuar ")
    print("...")
    if i==2:
        v0 = []
        v1 = []
        vef = []
        
        v0.append(intensidades[0]*np.cos(math.radians(fases[0])))
        v0.append(intensidades[0]*np.cos(math.radians(abs(fases[0]-90))))
        
        v1.append(intensidades[1]*np.cos(math.radians(fases[1])))
        v1.append(intensidades[1]*np.cos(math.radians(abs(fases[1]-90))))
    
        vef.append(v1[0]-v0[0])
        vef.append(v1[1]-v0[1])
        
        fase = math.degrees(math.asin(math.sin(abs(fases[0]-fases[1]))*intensidades[1]/magnitude(vef)))
        fase = round(fase, 0)
        MT = 2 #Gramas
        MC = intensidades[0] * MT/magnitude(vef)
        print("Massa de Correção:", MC, "gramas")
        print("Fase:", fase, "°")
    i=i+1
    


