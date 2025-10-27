import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="INTERFACES MULTIMODALES",
    page_icon="🎤",
    layout="centered"
)

# --- ESTILOS PERSONALIZADOS ---
page_style = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');

    /* Forzar tipografía en todo */
    html, body, [class*="st-"], [data-testid="stAppViewContainer"] * {
        font-family: 'Poppins', sans-serif !important;
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #fdf2f8, #f0f4ff, #e7f9f9);
        color: #333;
    }

    h1 {
        text-align: center;
        font-weight: 800;
        background: linear-gradient(90deg, #5b5f97, #7e57c2, #64b5f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5em;
        margin-bottom: 0.4em;
    }

    h2, h3 {
        text-align: center;
        color: #5b5f97;
        font-weight: 600;
    }

    img {
        display: block;
        margin: 0 auto;
        border-radius: 20px;
        box-shadow: 0 0 15px rgba(91, 95, 151, 0.3);
    }

    p, .stMarkdown {
        text-align: center;
        font-size: 1.1em;
        color: #333;
    }

    /* Botón de voz */
    div.bk.bk-btn {
        background: linear-gradient(90deg, #7e57c2, #64b5f6);
        color: white !important;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        box-shadow: 0px 4px 10px rgba(126, 87, 194, 0.4);
        font-family: 'Poppins', sans-serif !important;
    }

    div.bk.bk-btn:hover {
        background: linear-gradient(90deg, #64b5f6, #7e57c2);
    }
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# --- CONFIGURACIÓN MQTT ---
def on_publish(client, userdata, result):
    print("El dato ha sido publicado\n")

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("GIT-HUBC")
client1.on_message = on_message

# --- INTERFAZ ---
st.title("INTERFACES MULTIMODALES")
st.subheader("CONTROL POR VOZ")

image = Image.open("voice_ctrl.jpg")
st.image(image, width=200)

st.write("🎙️ **Toca el botón y habla**")

stt_button = Button(label="🎧 Inicio", width=200)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result:
    if "GET_TEXT" in result:
        st.write(f"🗣️ **Texto detectado:** {result.get('GET_TEXT')}")
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": result.get("GET_TEXT").strip()})
        client1.publish("voice_ctrl", message)

    try:
        os.mkdir("temp")
    except:
        pass
