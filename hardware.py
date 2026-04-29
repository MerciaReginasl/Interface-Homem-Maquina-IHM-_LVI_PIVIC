import serial
import numpy as np

class SensorReader:

    def __init__(self, porta='/dev/ttyUSB0', baud=115200):
        try:
            self.ser = serial.Serial(porta, baud, timeout=1)
            self.simulacao = False
        except:
            self.simulacao = True

    def read_vibration(self):
        if self.simulacao:
            t = np.linspace(0,1,1000)
            signal = np.sin(2*np.pi*50*t) + 0.3*np.random.randn(len(t))
            return t, signal
        
        try:
            linha = self.ser.readline().decode().strip()
            dados = list(map(float, linha.split(",")))
            t = np.linspace(0,1,len(dados))
            return t, np.array(dados)
        except:
            return None, None

    def read_temperature(self):
        if self.simulacao:
            return 45 + np.random.randn()*2
        
        try:
            linha = self.ser.readline().decode().strip()
            return float(linha)
        except:
            return None


//# 🔧 Instalar dependência

pip install pyserial
  
//

/#🧩 2. USAR NO SEU ANALISADOR

/# No analisador.py, adicione:

from hardware import SensorReader

sensor = SensorReader()

/# 📊 Substituir vibração simulada por real

/# Troque isso:

t = st.session_state.vibration_data['time']
signal = st.session_state.vibration_data['signal']

/# Por isso:

t, signal = sensor.read_vibration()

if t is None:
    st.error("Erro ao ler sensor")
    return

/# 🌡️ Substituir temperatura

temp = sensor.read_temperature()
st.metric("Temperatura", f"{temp:.1f} °C")

/# ⚡ 3. CONTROLE GPIO (EXEMPLO REAL)

/# Se quiser ligar algo (motor, relé):

from gpiozero import LED

motor = LED(17)

if st.button("Ligar Motor"):
    motor.on()

if st.button("Desligar Motor"):
    motor.off()

/# 🎛️ 4. VISUAL INDUSTRIAL (SCADA STYLE)

/# Adicione no topo do analisador.py:

st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    .metric-card {
        background-color: #1c1f26;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

/# 🧠 Métricas estilo industrial

st.markdown('<div class="metric-card">', unsafe_allow_html=True)
st.metric("RPM", f"{rpm:.0f}")
st.markdown('</div>', unsafe_allow_html=True)

/#🔄 5. ATUALIZAÇÃO AUTOMÁTICA

/#Para simular tempo real:

import time

time.sleep(1)
st.rerun()

/# 🚀 6. INICIAR AUTOMÁTICO NO RASPBERRY

crontab -e

/# Adicione:

@reboot streamlit run /home/pi/app.py --server.address 0.0.0.0

/# ⚠️ PROBLEMAS COMUNS
/# ❌ /dev/ttyUSB0 não aparece
/# 👉 rode:

ls /dev/tty*

/# ❌ Permissão negada:

sudo chmod 666 /dev/ttyUSB0

/# ❌ GPIO não responde
/# 👉 execute como root ou configure permissões

