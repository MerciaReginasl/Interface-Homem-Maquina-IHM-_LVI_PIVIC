import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="Analisador Modular - IHM Remota",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado
st.markdown("""
<style>
    .status-connected {
        background-color: #28a745;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
    }
    .status-disconnected {
        background-color: #dc3545;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .warning-text {
        color: #ffc107;
        font-weight: bold;
    }
    .danger-text {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização do estado da sessão
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'simulation_mode' not in st.session_state:
    st.session_state.simulation_mode = True
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'vibration_data' not in st.session_state:
    # Gerar dados simulados iniciais
    t = np.linspace(0, 1, 1000)
    signal = np.sin(2 * np.pi * 50 * t) + 0.5 * np.sin(2 * np.pi * 120 * t) + 0.3 * np.random.randn(len(t))
    st.session_state.vibration_data = {'time': t, 'signal': signal}
if 'temperature_history' not in st.session_state:
    st.session_state.temperature_history = [45 + np.random.randn() * 2 for _ in range(60)]
if 'rpm' not in st.session_state:
    st.session_state.rpm = 1750

# Funções auxiliares
def calculate_fft(signal, fs=1000):
    """Calcula a FFT do sinal"""
    n = len(signal)
    fft_vals = np.fft.fft(signal)
    fft_freq = np.fft.fftfreq(n, 1/fs)
    magnitude = np.abs(fft_vals[:n//2]) * 2/n
    freq = fft_freq[:n//2]
    return freq, magnitude

def detect_faults(frequencies, magnitudes, rpm=1750):
    """Detecta possíveis falhas em rolamentos baseado nas frequências"""
    faults = []
    # Frequências características típicas (exemplo para rolamento 6204)
    bpfi = rpm/60 * 4.95  # Ball Pass Frequency Inner
    bpfo = rpm/60 * 3.05  # Ball Pass Frequency Outer
    bsf = rpm/60 * 2.02   # Ball Spin Frequency
    
    for i, freq in enumerate(frequencies):
        if magnitudes[i] > 0.5:  # Limiar de detecção
            if abs(freq - bpfi) < 10:
                faults.append(f"⚠️ Possível falha na pista interna ({freq:.1f} Hz)")
            elif abs(freq - bpfo) < 10:
                faults.append(f"⚠️ Possível falha na pista externa ({freq:.1f} Hz)")
            elif abs(freq - bsf) < 10:
                faults.append(f"⚠️ Possível falha nos elementos rolantes ({freq:.1f} Hz)")
    
    return list(set(faults))  # Remove duplicatas

# Barra lateral
with st.sidebar:
    st.title("🔧 Analisador Modular")
    st.markdown("---")
    
    # Status de conexão
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.connected:
            st.markdown('<div class="status-connected">✅ Conectado</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-disconnected">❌ Desconectado</div>', unsafe_allow_html=True)
    
    with col2:
        if st.session_state.simulation_mode:
            st.info("🎮 Modo Simulação")
        else:
            st.success("📡 Hardware Real")
    
    # Botão de conexão
    if st.button("🔌 Conectar ao Analisador", type="primary", use_container_width=True):
        st.session_state.connected = not st.session_state.connected
        if st.session_state.connected:
            st.toast("✅ Conectado ao analisador com sucesso!", icon="✅")
        else:
            st.toast("❌ Desconectado do analisador", icon="❌")
        st.rerun()
    
    st.markdown("---")
    
    # Seleção do módulo
    modulo = st.radio(
        "📂 Módulos do Sistema",
        ["📊 Vibração", "🌡️ Temperatura", "⚙️ Velocidade", "⚖️ Balanceamento", "📈 Histórico", "🤖 IA (Experimental)"],
        index=0
    )
    
    st.markdown("---")
    st.caption(f"🕒 Última atualização: {st.session_state.last_update.strftime('%H:%M:%S')}")
    
    if st.button("🔄 Atualizar dados", use_container_width=True):
        st.session_state.last_update = datetime.now()
        st.rerun()

# Área principal
st.title("📊 Sistema de Diagnóstico em Manutenção Preditiva")
st.markdown("---")

# Simulação de dados em tempo real (se conectado)
if st.session_state.connected:
    placeholder = st.empty()
    with placeholder.container():
        st.info("🟢 Recebendo dados em tempo real...")
        time.sleep(0.5)
        placeholder.empty()

# Conteúdo dinâmico baseado no módulo selecionado
if modulo == "📊 Vibração":
    st.header("📈 Análise de Vibração")
    
    # Obter dados atuais
    t = st.session_state.vibration_data['time']
    signal = st.session_state.vibration_data['signal']
    fs = 1000
    
    # Calcular FFT
    frequencies, magnitudes = calculate_fft(signal, fs)
    
    # Detectar falhas
    faults = detect_faults(frequencies, magnitudes, st.session_state.rpm)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gráfico de sinal no domínio do tempo
        fig_time = go.Figure()
        fig_time.add_trace(go.Scatter(
            x=t[:500], 
            y=signal[:500],
            mode='lines',
            name='Sinal de Vibração',
            line=dict(color='#0066cc', width=1.5)
        ))
        fig_time.update_layout(
            title="Sinal Bruto - Domínio do Tempo",
            xaxis_title="Tempo (s)",
            yaxis_title="Aceleração (g)",
            height=400,
            template="plotly_white"
        )
        st.plotly_chart(fig_time, use_container_width=True)
        
        # Gráfico FFT
        fig_fft = go.Figure()
        fig_fft.add_trace(go.Scatter(
            x=frequencies[:200],
            y=magnitudes[:200],
            mode='lines',
            name='FFT',
            line=dict(color='#ff6600', width=1.5)
        ))
        fig_fft.update_layout(
            title="Espectro de Frequência (FFT)",
            xaxis_title="Frequência (Hz)",
            yaxis_title="Magnitude",
            height=400,
            template="plotly_white"
        )
        st.plotly_chart(fig_fft, use_container_width=True)
    
    with col2:
        st.markdown("### 🔍 Indicadores")
        
        # Valor RMS
        rms = np.sqrt(np.mean(signal**2))
        st.metric("Valor RMS", f"{rms:.3f} g")
        
        # Pico máximo
        peak = np.max(np.abs(signal))
        st.metric("Pico Máximo", f"{peak:.3f} g")
        
        # Frequência dominante
        dominant_freq_idx = np.argmax(magnitudes[:200])
        dominant_freq = frequencies[dominant_freq_idx]
        st.metric("Frequência Dominante", f"{dominant_freq:.1f} Hz")
        
        st.markdown("---")
        st.markdown("### ⚠️ Alertas")
        
        if faults:
            for fault in faults:
                st.warning(fault)
        else:
            st.success("✅ Nenhuma falha detectada")
        
        st.markdown("---")
        st.markdown("### 📤 Exportar")
        if st.button("📥 Exportar dados (CSV)", use_container_width=True):
            df = pd.DataFrame({'Tempo (s)': t, 'Sinal (g)': signal})
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", csv, "vibration_data.csv", "text/csv", use_container_width=True)

elif modulo == "🌡️ Temperatura":
    st.header("🌡️ Monitoramento de Temperatura")
    
    # Simular nova leitura
    if st.session_state.connected:
        new_temp = 45 + np.random.randn() * 2
        st.session_state.temperature_history.append(new_temp)
        if len(st.session_state.temperature_history) > 60:
            st.session_state.temperature_history.pop(0)
    
    current_temp = st.session_state.temperature_history[-1]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Indicador circular
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current_temp,
            title={'text': "Temperatura Atual"},
            delta={'reference': 40, 'increasing': {'color': "red"}},
            gauge={
                'axis': {'range': [None, 80]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 40], 'color': "lightgreen"},
                    {'range': [40, 60], 'color': "yellow"},
                    {'range': [60, 80], 'color': "red"}
                ],
                'threshold': {
                    'value': 60,
                    'line': {'color': "red", 'width': 4},
                    'title': {'text': "Alerta"}
                }
            }
        ))
        fig_gauge.update_layout(height=400)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        # Gráfico de tendência
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            y=st.session_state.temperature_history,
            mode='lines+markers',
            name='Temperatura',
            line=dict(color='#ff6600', width=2),
            marker=dict(size=4)
        ))
        fig_trend.update_layout(
            title="Histórico de Temperatura (últimos 60 pontos)",
            xaxis_title="Leitura",
            yaxis_title="Temperatura (°C)",
            height=400,
            template="plotly_white"
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # Alertas de temperatura
    if current_temp > 60:
        st.error(f"🚨 ALERTA CRÍTICO: Temperatura muito alta ({current_temp:.1f}°C)! Verificar sistema de refrigeração.")
    elif current_temp > 50:
        st.warning(f"⚠️ ATENÇÃO: Temperatura elevada ({current_temp:.1f}°C). Monitorar de perto.")
    else:
        st.success(f"✅ Temperatura normal ({current_temp:.1f}°C)")

elif modulo == "⚙️ Velocidade":
    st.header("⚙️ Monitoramento de Velocidade de Rotação")
    
    # Simular variação de RPM
    if st.session_state.connected:
        st.session_state.rpm += np.random.randn() * 10
        st.session_state.rpm = np.clip(st.session_state.rpm, 1650, 1850)
    
    rpm = st.session_state.rpm
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Rotação Atual", f"{rpm:.0f} RPM", 
                  delta=f"{rpm - 1750:.0f}" if rpm != 1750 else None)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Frequência", f"{rpm/60:.1f} Hz")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Faixa Segura", "1700 - 1800 RPM")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Velocímetro analógico
    fig_speed = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rpm,
        title={'text': "Velocímetro"},
        gauge={
            'axis': {'range': [1500, 2000]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [1500, 1700], 'color': "lightgray"},
                {'range': [1700, 1800], 'color': "lightgreen"},
                {'range': [1800, 1900], 'color': "yellow"},
                {'range': [1900, 2000], 'color': "red"}
            ],
            'threshold': {
                'value': 1800,
                'line': {'color': "red", 'width': 4},
                'title': {'text': "Limite Superior"}
            }
        }
    ))
    fig_speed.update_layout(height=400)
    st.plotly_chart(fig_speed, use_container_width=True)
    
    if rpm > 1800:
        st.warning("⚠️ Velocidade acima do recomendado. Reduza a rotação para evitar desgaste excessivo.")
    elif rpm < 1700:
        st.info("ℹ️ Velocidade abaixo do ideal. Considere aumentar a rotação para melhor desempenho.")

elif modulo == "⚖️ Balanceamento":
    st.header("⚖️ Análise de Balanceamento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Fase e Amplitude")
        
        # Dados simulados de desbalanceamento
        fase = np.random.uniform(0, 360)
        amplitude = np.random.uniform(0.1, 0.5)
        
        st.metric("Fase da Vibração", f"{fase:.1f}°")
        st.metric("Amplitude de Desbalanceamento", f"{amplitude:.3f} mm/s")
        
        st.markdown("---")
        st.markdown("### 🔧 Sugestão de Correção")
        
        if amplitude > 0.3:
            massa_corretiva = amplitude * 5
            st.info(f"**Massa corretiva sugerida:** {massa_corretiva:.2f} g")
            st.info(f"**Ângulo de aplicação:** {fase + 180:.1f}° (oposto à fase medida)")
        else:
            st.success("✅ Sistema dentro da faixa de balanceamento aceitável")
    
    with col2:
        # Diagrama polar
        theta = np.linspace(0, 2*np.pi, 100)
        r = np.ones_like(theta)
        
        fig_polar = go.Figure()
        fig_polar.add_trace(go.Scatterpolar(
            r=[0, amplitude],
            theta=[0, fase],
            mode='lines+markers',
            name='Vetor desbalanceamento',
            line=dict(color='red', width=3),
            marker=dict(size=10)
        ))
        fig_polar.update_layout(
            polar=dict(
                radialaxis=dict(range=[0, 1], tickangle=0),
                angularaxis=dict(direction="clockwise")
            ),
            title="Diagrama Polar - Análise de Fase",
            height=450
        )
        st.plotly_chart(fig_polar, use_container_width=True)

elif modulo == "📈 Histórico":
    st.header("📈 Histórico de Falhas e Eventos")
    
    # Dados históricos simulados
    historico = pd.DataFrame({
        'Data/Hora': pd.date_range(start='2026-03-20 08:00', periods=10, freq='6h'),
        'Evento': [
            'Vibração elevada detectada',
            'Temperatura acima do normal',
            'Pico espectral em 50Hz',
            'Rotação instável',
            'Falha em rolamento - Pista interna',
            'Temperatura normalizada',
            'Manutenção preventiva',
            'Vibração em nível crítico',
            'Balanceamento realizado',
            'Sistema estabilizado'
        ],
        'Severidade': ['Alta', 'Média', 'Baixa', 'Média', 'Crítica', 'Info', 'Info', 'Crítica', 'Média', 'Baixa'],
        'Status': ['Resolvido', 'Resolvido', 'Resolvido', 'Monitorando', 'Resolvido', 'Ok', 'Concluído', 'Resolvido', 'Concluído', 'Ok']
    })
    
    st.dataframe(historico, use_container_width=True, hide_index=True)
    
    # Gráfico de evolução
    st.markdown("### 📊 Evolução da Vibração RMS")
    dias = pd.date_range(start='2026-03-20', periods=30, freq='D')
    rms_historico = 0.15 + 0.1 * np.sin(np.linspace(0, 4*np.pi, 30)) + 0.05 * np.random.randn(30)
    
    fig_evo = go.Figure()
    fig_evo.add_trace(go.Scatter(
        x=dias,
        y=rms_historico,
        mode='lines+markers',
        name='RMS (g)',
        line=dict(color='#0066cc', width=2),
        marker=dict(size=6)
    ))
    fig_evo.add_hline(y=0.25, line_dash="dash", line_color="orange", annotation_text="Alerta")
    fig_evo.add_hline(y=0.35, line_dash="dash", line_color="red", annotation_text="Crítico")
    fig_evo.update_layout(
        title="Evolução Temporal da Vibração RMS",
        xaxis_title="Data",
        yaxis_title="RMS (g)",
        height=400,
        template="plotly_white"
    )
    st.plotly_chart(fig_evo, use_container_width=True)

elif modulo == "🤖 IA (Experimental)":
    st.header("🧠 Inteligência Artificial - Redução de Ruído")
    st.warning("🔬 Módulo em desenvolvimento - Resultados preliminares")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Sinal Original")
        t = np.linspace(0, 1, 1000)
        sinal_original = np.sin(2 * np.pi * 50 * t) + 0.3 * np.random.randn(len(t))
        
        fig_orig = go.Figure()
        fig_orig.add_trace(go.Scatter(x=t[:300], y=sinal_original[:300], mode='lines', name='Sinal ruidoso'))
        fig_orig.update_layout(title="Sinal com Ruído", height=300, template="plotly_white")
        st.plotly_chart(fig_orig, use_container_width=True)
    
    with col2:
        st.markdown("### Sinal Filtrado (Autoencoder)")
        # Simular filtragem (média móvel simples para demonstração)
        kernel = np.ones(10)/10
        sinal_filtrado = np.convolve(sinal_original, kernel, mode='same')
        
        fig_filt = go.Figure()
        fig_filt.add_trace(go.Scatter(x=t[:300], y=sinal_filtrado[:300], mode='lines', name='Sinal filtrado', line=dict(color='green')))
        fig_filt.update_layout(title="Sinal com Redução de Ruído", height=300, template="plotly_white")
        st.plotly_chart(fig_filt, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📊 Métricas de Desempenho (Simulação)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("SNR (Original)", "8.2 dB")
        st.metric("SNR (Filtrado)", "15.7 dB", delta="+7.5 dB")
    with col2:
        st.metric("RMSE (Original)", "0.087")
        st.metric("RMSE (Filtrado)", "0.042", delta="-0.045")
    with col3:
        st.metric("Preservação de picos", "92%")
        st.info("🧪 Técnicas: Autoencoders, CNN 1D, ICA, Random Forest")
    
    st.info("📌 **Nota:** Resultados baseados em simulações. Implementação em hardware real depende de novo microprocessador.")

# Rodapé
st.markdown("---")
st.caption("🏥 **Sistema de Diagnóstico em Manutenção Preditiva** | Desenvolvido com Streamlit | Dados em tempo real via WebSocket")
st.caption("🔧 **Analisador Modular de Baixo Custo** - Projeto PVCT955-2025 | Orientador: Richard Senko")



# 🚀 Como executar

# 1. Instale as dependências (no terminal):

pip install streamlit pandas numpy plotly

# 2. Execute o aplicativo:

streamlit run analisador_interface.py

# 3. Acesse no navegador: 

http://localhost:8501

# 🔧 Adaptação para hardware real
# Quando tiver o novo microprocessador, substitua as simulações por chamadas à API ou leitura serial:

# Exemplo para dados reais via serial
import serial
ser = serial.Serial('/dev/ttyUSB0', 115200)
dado_real = ser.readline().decode().strip()

#A interface já está pronta para receber dados reais - basta substituir as funções de simulação pelas leituras do hardware!
