from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
import RPi.GPIO as GPIO
import threading
import sys


class LapCounterWindow(QMainWindow):
    def __init__(self):

        try:
            GPIO.cleanup() # Tenta limpar configurações antigas
        except:
            pass # Se não tiver nada pra limpar, segue o jogo

        GPIO.setmode(GPIO.BCM)
        super().__init__()

        self.setWindowTitle("Tacômetro")
        self.setGeometry(200, 200, 400, 200)

        self.label = QLabel(self)
        self.label.setGeometry(50, 50, 300, 100)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Arial", 20))

        self.button = QPushButton("Iniciar", self)
        self.button.setGeometry(150, 160, 100, 30)
        self.button.clicked.connect(self.toggle_counter)

        self.lap_count = 0
        self.timer = None
        self.lock = threading.Lock()
        self.is_running = False
        
        self.ir_sensor_pin = 14  # Substitua pelo pino correto do seu sensor
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ir_sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.ir_sensor_pin, GPIO.RISING, callback=self.ir_sensor_triggered, bouncetime=1)

    def toggle_counter(self):
        if not self.is_running:
            self.start_counter()
            self.button.setText("Parar")
        else:
            self.stop_counter()
            self.button.setText("Iniciar")

    def start_counter(self):
        self.lap_count = 0
        self.label.setText("")
        self.is_running = True

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_counter)
        self.timer.start(1000)  # Contagem de 1000 ms

    def update_counter(self):
        with self.lock:
            vpm = self.lap_count * 60
            self.label.setText(f"{vpm} RPM")
            self.lap_count = 0

    def ir_sensor_triggered(self, channel):
        if self.is_running:
            with self.lock:
                self.lap_count += 1

    def stop_counter(self):
        self.timer.stop()
        vpm = self.lap_count * 60
        self.label.setText(f"{vpm} RPM")
        self.is_running = False

    def closeEvent(self, event):
        GPIO.cleanup()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LapCounterWindow()
    window.show()
    sys.exit(app.exec_())
