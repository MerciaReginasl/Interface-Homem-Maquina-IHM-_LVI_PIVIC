#mpu6050
import smbus
import time
import RPi.GPIO as gpio
import numpy as np

amostras = 0
periodo = 0
tempo_total = 0
taxa_de_amostragem = 0
z = []
Z = []
constante = 16384.0

PWR_M = 0x6B
DIV = 0x19
CONFIG = 0x1A
INT_EN = 0x38
ACCEL_X = 0x3B
ACCEL_Y = 0x3D
ACCEL_Z = 0x3F
RS = 18
EN = 23
D4 = 24
D5 = 25
D6 = 8
D7 = 7
bus = smbus.SMBus(1)
ADDRESS = 0x68

def IniciaMPU():
    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    gpio.setup(RS, gpio.OUT)
    gpio.setup(EN, gpio.OUT)
    gpio.setup(D4, gpio.OUT)
    gpio.setup(D5, gpio.OUT)
    gpio.setup(D6, gpio.OUT)
    gpio.setup(D7, gpio.OUT)
    bus.write_byte_data(ADDRESS, DIV, 7)
    bus.write_byte_data(ADDRESS, PWR_M, 1)
    bus.write_byte_data(ADDRESS, CONFIG, 0)
    bus.write_byte_data(ADDRESS, INT_EN, 1)
    time.sleep(1)

def lerMPU(addr):
    high = bus.read_byte_data(ADDRESS, addr)
    value = high << 8
    if(value > 32768):
        value = value - 65536
    return value

def gravar(tempo_total):
    global z
    del z[:]

    initial_time = time.time()
    while time.time()-initial_time <tempo_total:
        z.append(lerMPU(ACCEL_Z))
        

def plot_figure(sinal, frequencia_de_coleta, tempo_da_coleta):
    import scipy.fft as sc
    import matplotlib.pyplot as plt
    
    n = len(sinal)
    #Signal fft calculation
    fft = sc.fft(sinal)

    #Amplitude vector
    amp = abs(fft)[:n // 2] * 1 / n

    #Frequency vector
    freqs = abs(sc.fftfreq(len(fft))*frequencia_de_coleta)

    Xf = freqs[:len(amp)]
    Yf = amp

    t = np.linspace(0, tempo_da_coleta, len(sinal))
    fig, axs = plt.subplots(2)
    axs[0].plot(t, sinal)
    axs[0].set_xlabel('Tempo [s]', fontsize = 20)
    axs[0].set_ylabel('Amplitude [g]', fontsize = 20)
    axs[1].plot(Xf[1:], Yf[1:])
    axs[1].xlim(10, len(Xf))
    axs[1].set_xlabel('Frequência [Hz]', fontsize = 20)
    axs[1].set_ylabel('Amplitude [g]', fontsize = 20)
    plt.pause(0.01)
    plt.grid()
    
    
def coletaMPU(tempo_total):
    import matplotlib.pyplot as plt
    import scipy.fft as sc
    global amostras, taxa_de_amostragem, periodo, constante, Z

    del Z[:]
    
    IniciaMPU()
    gravar(tempo_total)
    amostras = len(z)
    periodo = tempo_total/amostras
    taxa_de_amostragem = 1/periodo

    for i in range(0, len(z)):
        Z.append(z[i]/constante)
    
    n = len(Z)
    #Signal fft calculation
    fft = sc.fft(Z)

    #Amplitude vector
    amp = abs(fft)[:n // 2] * 1 / n

    #Frequency vector
    freqs = abs(sc.fftfreq(len(fft))*taxa_de_amostragem)

    Xf = freqs[:len(amp)]
    Yf = amp

    t = np.linspace(0, tempo_total, len(Z))

    #plt.figure()
    plt.plot(Xf, Xf)
    plt.xlabel('Frequência [Hz]', fontsize = 20)
    plt.ylabel('Amplitude [g]', fontsize = 20)
    plt.grid()
    #plt.show()

    return t, Z, Xf, Yf, taxa_de_amostragem


