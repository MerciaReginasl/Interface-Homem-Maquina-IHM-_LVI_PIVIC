# Nome do arquivo: analisador_vib.py

import sys
import matplotlib
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLineEdit, QSizePolicy, QFileDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Importa a função de coleta do outro arquivo
from MPU6050 import *

# --- MODIFICAÇÃO 1: Função de Salvamento Simplificada para .txt ---
def save_to_txt(filename, data_vector):
    """Salva um vetor de dados (uma lista ou array) em um arquivo de texto,
    com um valor por linha."""
    try:
        with open(filename, 'w') as f:
            for item in data_vector:
                f.write(f"{item}\n")
        print(f"Dados de amplitude salvos com sucesso em {filename}")
    except Exception as e:
        print(f"Ocorreu um erro ao salvar o arquivo de texto: {e}")

# --- Thread para Coleta de Dados (sem alterações) ---
class PlotThread(QThread):
    """Thread que executa a coleta de dados para não travar a interface."""
    plot_done = pyqtSignal(object)

    def __init__(self, time):
        super().__init__()
        self.time = time
        self.abort_flag = False

    def run(self):
        try:
            IniciaMPU()
            t, Z_em_g, Xf, Yf, _ = coletaMPU(self.time)

            if not self.abort_flag:
                collected_data = {
                    "time": t, "amplitude": Z_em_g,
                    "frequency": Xf, "fft_amplitude": Yf
                }
                self.plot_done.emit(collected_data)

        except Exception as e:
            print("\n!!! OCORREU UM ERRO DENTRO DA THREAD !!!")
            print(f"--- Erro: {e} ---")
            import traceback
            traceback.print_exc()
            self.plot_done.emit({}) 

    def abort(self):
        self.abort_flag = True

# --- Widget de Gráfico Matplotlib (sem alterações) ---
class GraphWidget(QWidget):
    """Widget que contém a figura e o canvas do Matplotlib."""
    def __init__(self):
        super().__init__()
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def clear(self):
        self.figure.clear()
        self.canvas.draw()

    def plot(self, data):
        """Função centralizada para plotar os dados recebidos."""
        self.figure.clear()
        ax1 = self.figure.add_subplot(211)
        ax1.plot(data["time"], data["amplitude"])
        ax1.set_title("Sinal no Domínio do Tempo")
        ax1.set_xlabel("Tempo [s]")
        ax1.set_ylabel("Amplitude [g]")
        ax1.grid(True)
        ax2 = self.figure.add_subplot(212)
        ax2.plot(data["frequency"][1:], data["fft_amplitude"][1:])
        ax2.set_title("Sinal no Domínio da Frequência (FFT)")
        ax2.set_xlabel("Frequência [Hz]")
        ax2.set_ylabel("Amplitude [g]")
        ax2.grid(True)
        self.figure.tight_layout()
        self.canvas.draw()

# --- Janela Principal da Aplicação ---
class GraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analisador de Vibrações")
        self.setGeometry(100, 100, 800, 600)
        self.last_collected_data = None
        self.plot_thread = None
        
        self.graph_widget = GraphWidget()
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Tempo total da coleta [s]")
        self.start_button = QPushButton("Iniciar Coleta", self)
        self.abort_button = QPushButton("Abortar", self)
        self.save_button = QPushButton("Salvar Dados", self)
        
        self.abort_button.setEnabled(False)
        self.save_button.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.abort_button)
        button_layout.addWidget(self.save_button)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.graph_widget)
        main_layout.addWidget(self.input_field)
        main_layout.addLayout(button_layout)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.start_button.clicked.connect(self.start_plotting)
        self.abort_button.clicked.connect(self.abort_plotting)
        self.save_button.clicked.connect(self.save_data)

    def start_plotting(self):
        try:
            time = float(self.input_field.text())
            if time <= 0:
                print("Por favor, insira um tempo positivo.")
                return
            self.graph_widget.clear()
            self.start_button.setEnabled(False)
            self.abort_button.setEnabled(True)
            self.save_button.setEnabled(False)
            self.last_collected_data = None
            self.plot_thread = PlotThread(time)
            self.plot_thread.plot_done.connect(self.plot_finished)
            self.plot_thread.start()
        except ValueError:
            print("Valor inválido para o tempo. Por favor, insira um número.")

    def abort_plotting(self):
        if self.plot_thread and self.plot_thread.isRunning():
            self.plot_thread.abort()
            self.start_button.setEnabled(True)
            self.abort_button.setEnabled(False)
            self.save_button.setEnabled(False)

    # --- MODIFICAÇÃO 2: Método save_data ajustado para usar a nova função ---
    def save_data(self):
        """Abre o diálogo para salvar e chama a função que grava o arquivo .txt."""
        if self.last_collected_data:
            # Abre o diálogo de salvamento, agora sugerindo o formato .txt
            filename, _ = QFileDialog.getSaveFileName(self, "Salvar Amplitude em TXT", "", "Arquivo de Texto (*.txt)")
            
            # Procede apenas se o usuário selecionou um nome e clicou em "Salvar"
            if filename:
                # Chama a nova função, passando apenas o vetor de amplitude
                save_to_txt(filename, self.last_collected_data["amplitude"])
        else:
            print("Nenhum dado coletado para salvar.")
        # O programa continua em execução normalmente após salvar.

    def plot_finished(self, data):
        """Este método é chamado quando a thread termina."""
        if data:
            self.last_collected_data = data
            self.graph_widget.plot(data)
            self.save_button.setEnabled(True)
        else:
            print("A coleta de dados falhou ou foi abortada. Nenhum gráfico para exibir.")
            self.save_button.setEnabled(False)
        self.start_button.setEnabled(True)
        self.abort_button.setEnabled(False)

# --- Ponto de Entrada da Aplicação ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphWindow()
    window.show()
    sys.exit(app.exec_())
