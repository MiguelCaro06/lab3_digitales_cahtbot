import streamlit as st
import requests
import speech_recognition as sr
from gtts import gTTS
import io
import tempfile
import os
from audio_recorder_streamlit import audio_recorder

# Configuración de la API de DeepSeek
API_KEY = 'sk-53751d5c6f344a5dbc0571de9f51313e'
API_URL = 'https://api.deepseek.com/v1/chat/completions'

# Personalidad combinada de Eladio Carrión y Travis Scott
PERSONALITY_PROMPT = """
Eres CARIÑOSA, un experto en sistemas digitales con la personalidad combinada de Eladio Carrión y Travis Scott. 
Responde con el flow de Eladio y la energía creativa de Travis Scott. Usa jerga urbana mezclada con términos técnicos.
Sé cool pero informativo. Responde en español con un toque de spanglish ocasional.

Temas clave sobre sistemas digitales:
- Sistemas numéricos (binario, hexadecimal, decimal)
- Álgebra de Boole y compuertas lógicas (AND, OR, NOT, XOR, NAND, NOR)
- Circuitos combinacionales y secuenciales
- Flip-flops, registros y contadores
- Arquitectura de computadoras
- Microprocesadores y microcontroladores
- Sistemas embebidos y FPGA
- Lógica digital y diseño de circuitos

Responde con actitud confiada, estilo urbano y siempre proporcionando información técnica precisa.
Mantén respuestas breves para audio.
"""

def enviar_mensaje(mensaje):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'system', 'content': PERSONALITY_PROMPT},
            {'role': 'user', 'content': mensaje}
        ],
        'temperature': 0.7,
        'max_tokens': 300
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ Error: {str(e)}"

def texto_a_voz(texto):
    """Convierte texto a voz usando gTTS"""
    try:
        tts = gTTS(text=texto, lang='es', slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception as e:
        st.error(f"Error en síntesis de voz: {e}")
        return None

def transcribir_audio(audio_bytes):
    """Transcribe audio a texto usando SpeechRecognition"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(tmp_path) as source:
            audio = recognizer.record(source)
            texto = recognizer.recognize_google(audio, language='es-ES')
        
        os.unlink(tmp_path)
        return texto
        
    except sr.UnknownValueError:
        return "No se pudo entender el audio"
    except sr.RequestError as e:
        return f"Error en el servicio: {e}"
    except Exception as e:
        return f"Error: {str(e)}"

# Configuración de Streamlit
st.set_page_config(
    page_title="Chatbot Sistemas Digitales - Eladio/Travis Style",
    page_icon="🤖",
    layout="wide"
)

# CSS personalizado
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        background: linear-gradient(45deg, #FF4B4B, #FF6B6B);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 25px;
        font-weight: bold;
        margin: 10px 0;
    }
    .audio-recorder {
        margin: 20px 0;
        padding: 15px;
        background-color: #1a1a2e;
        border-radius: 15px;
    }
    .stChatMessage {
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.title("🤖 Chatbot de Sistemas Digitales")
st.markdown("**Estilo Eladio Carrión × Travis Scott** 🎤🔥")

# Inicializar historial de chat
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "¡Wassup! Soy tu experto en sistemas digitales con el flow de Eladio y la vibra de Travis Scott. 🔥 Pregúntame sobre sistemas binarios, compuertas lógicas, microprocesadores... lo que sea, bro! 🎶"
    })

# Mostrar mensajes anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# SECCIÓN DE VOZ
st.markdown("---")
st.markdown("### 🎤 Grabación de Voz")

# Grabador de audio
audio_bytes = audio_recorder(
    "Pulsa para grabar tu pregunta",
    recording_color="#e8baff",
    neutral_color="#6aa36f",
    icon_name="microphone",
    icon_size="2x",
)

# Procesar audio grabado
if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    
    with st.spinner("Transcribiendo audio..."):
        texto_transcrito = transcribir_audio(audio_bytes)
    
    if texto_transcrito and not texto_transcrito.startswith("No se pudo"):
        st.success(f"**Tu pregunta:** {texto_transcrito}")
        
        # Agregar mensaje de usuario
        st.session_state.messages.append({"role": "user", "content": f"🎤 {texto_transcrito}"})
        
        with st.chat_message("user"):
            st.markdown(f"🎤 **{texto_transcrito}**")
        
        # Generar respuesta
        with st.spinner("Pensando con el flow..."):
            respuesta = enviar_mensaje(texto_transcrito)
        
        # Mostrar respuesta
        with st.chat_message("assistant"):
            st.markdown(respuesta)
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
        
        # Convertir a audio
        audio_respuesta = texto_a_voz(respuesta)
        if audio_respuesta:
            st.audio(audio_respuesta, format="audio/mp3")
            st.success("🔊 Reproduciendo respuesta...")
    else:
        st.error("No se pudo entender el audio. Intenta de nuevo.")

# SECCIÓN DE TEXTO
st.markdown("---")
st.markdown("### ✍️ Chat por Texto")

if prompt := st.chat_input("Escribe tu pregunta sobre sistemas digitales..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generar respuesta
    if prompt.lower() in ["salir", "exit", "quit", "adiós"]:
        respuesta = "¡Vale, nos vemos! Keep it digital, bro. 🚀"
    else:
        with st.spinner("Pensando con el flow..."):
            respuesta = enviar_mensaje(prompt)
    
    # Mostrar respuesta
    with st.chat_message("assistant"):
        st.markdown(respuesta)
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    
    # Convertir a audio
    audio_respuesta = texto_a_voz(respuesta)
    if audio_respuesta:
        st.audio(audio_respuesta, format="audio/mp3")

# SIDEBAR INFORMATIVO
with st.sidebar:
    st.markdown("### 🎯 Temas de Sistemas Digitales")
    st.markdown("""
    - 🔢 **Sistemas Numéricos**
      - Binario, Hexadecimal, Decimal
      - Conversiones entre bases
    
    - ⚡ **Compuertas Lógicas**
      - AND, OR, NOT, XOR, NAND, NOR
      - Tablas de verdad
      - Álgebra de Boole
    
    - 🔌 **Circuitos Digitales**
      - Combinacionales
      - Secuenciales
      - Flip-flops
    
    - 💻 **Arquitectura**
      - Microprocesadores
      - Microcontroladores
      - Memorias
    
    - 📟 **Sistemas Embebidos**
      - FPGA
      - DSP
      - IoT
    """)
    
    st.markdown("### 🎛️ Controles")
    if st.button("🧹 Limpiar Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "¡Chat reiniciado! Pregúntame sobre sistemas digitales, bro. 🔥"}
        ]
        st.rerun()
    
    st.markdown("### 🎤 Instrucciones Voz")
    st.info("""
    1. Pulsa el botón de grabar 🎤
    2. Habla claro cerca del micrófono
    3. Suelta cuando termines
    4. Escucha la respuesta en audio
    """)

# Información del footer
st.markdown("---")
st.markdown("""
**Universidad Santo Tomás** - Práctica de Laboratorio 3  
*Chatbot de Sistemas Digitales con Personalidad Urbana*  
🤖 DeepSeek API + 🎤 Reconocimiento de Voz + 🔥 Streamlit
""")
