import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from MLX90614 import MLX90614
from smbus2 import SMBus

# Função externa que retorna um valor para ser exibido na tela
def obter_valor():
    hw = MLX90614
    bus = SMBus(1)
    sensor = hw(bus, address=0x5A)
    return round(sensor.get_amb_temp(), 1)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configurando a janela
        self.setWindowTitle("Termômetro")
        self.setGeometry(300, 300, 250, 100)

        # Criando um rótulo para exibir o valor atualizado
        self.label = QLabel(self)
        self.label.setText("°C: ")
        self.label.move(20, 20)

        # Criando o botão "Iniciar"
        self.button = QPushButton("Iniciar", self)
        self.button.move(20, 50)
        self.button.clicked.connect(self.atualizar_valor)

    def atualizar_valor(self):
        # Chamando a função externa para obter o valor atualizado
        valor = MLX90614(SMBus(1), address=0x5A).get_object()
        #valor = "100"
        # Atualizando o rótulo com o novo valor
        self.label.setText("°C: " + str(valor))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
