import google.generativeai as genai
import sys
import streamlit as st
from streamlit_option_menu import option_menu
import locale
import os
from pathlib import Path

from datetime import datetime
from tempfile import NamedTemporaryFile
from pydub import AudioSegment

import logging  # biblioteca para não mostrar log de mensagens na tela

# para não mostrar log de mensagens na tela
for name, l in logging.root.manager.loggerDict.items():
    if "streamlit" in name:
        l.disabled = True

def html_table_format():
    # Get current datetime
    current_datetime = datetime.now()
    # Convert to string and format
    datetime_string = current_datetime.strftime('%d-%m-%Y')
    # Define the html table format
    out = f"""
        <body>
            <table style="width:100%; border-collapse: collapse;">
                <tr style="background-color:#99ff99;">
                    <th colspan="2" align="center">HORAS OPERADORES</th>
                </tr>
                <tr>
                    <th colspan="2" align="center">Data: {datetime_string}</th>
                </tr>
                <tr>
                    <th colspan="2" style="padding: 0.5em 0 0.5em 0; text-align: center; border: none;">Local: </th>
                </tr>
                <tr style="background-color: #99ff99; border: none;">
                    <td style="text-align: center; border: none;">Operador</th>
                    <td style="text-align: center; border: none;">Horas</th>
                </tr>
                <tr>
                    <th style="text-align: center; border: none;">Nome_operador</th>
                    <th style="text-align: center; border: none;">Horas_operador</th>
                </tr>
            </table>
        </body>
        """
    return out


def process_audio(value, name_of_model, description):
    # Define Gemini AI instructions according to selected language
    system_instruction = (f"Based on what you understand from the audio file, give the answer in the language {lang}. "
                          f"Do the job with no verbosity, I don't want to display your comments. "
                          f"If the date is not mentioned in the audio use the date {TODAY}. "
                          f"Always give it in the format day first or '%d-%m-%Y'")

    model = genai.GenerativeModel(model_name=name_of_model, system_instruction=system_instruction)

    if value:
        with st.spinner("Working..."):
            # audio_file = st.audio(audio_value, format='audio/wav')
            with NamedTemporaryFile(dir='.', suffix='.wav', delete=True) as f:  #delete=False mantém o arquivo
                f.write(value.getbuffer())
                # file_name = os.path.splitext(f.name)[0]
                file_name = f.name
                # print('\n ==================')
                # print('Temp file_name:', file_name)
                audio = AudioSegment.from_file(file_name)
                new_file = os.path.splitext(f.name)[0] +'.mp3'
                # audio.export(new_file, bitrate='128k', format='mp3')
                # print(f'===== audio file: \n {new_file}')

            audio_file = genai.upload_file(new_file)
            # audio_file = genai.upload_file(file_name)
            # time.sleep(2)

            # get result from AI model
            # print(f'===== Giving the response using Google Generative AI model: {name_of_model}')
            result = model.generate_content([audio_file, description])
            st.html(result.text)
            # for chunk in result:
            #     st.markdown(chunk.text, unsafe_allow_html=True)


sys.path.append(str(Path(__file__).resolve().parents[1]))

# --- GOOGLE API initialization
# print('Configuring apikey...')
# os.environ['GEMINI_API_KEY'] = apikey
# Read Gemini API-Key credentials stored in secrets.toml file
apikey = st.secrets.google_api["apikey"]
genai.configure(api_key=apikey)

# --- LOCAL configurations
# set the locale to Spanish (Spain)
locale.setlocale(locale.LC_NUMERIC, 'es_ES.UTF-8')
# get today date
TODAY = datetime.strptime(datetime.now().strftime("%d-%m-%Y"), "%d-%m-%Y")
LANG = ["Português-BR", "Español-ES"]
# SOURCE = ["Áudio", "Arquivo de Voz"]
output_format = html_table_format()
DESC = (f"Create an html table the output format {output_format}."
        f"Always sum the total worked hours and put it in the last row of the table in bold")
        # f"Separate every person's name and hours in a python dictionary called 'horas_trabalhadas")

# Choosing the Gemini model
# model_name = "gemini-1.5-flash"
model_name = "gemini-2.0-flash"
# model_name = "gemini-2.0-flash-Lite"

# --- starting STREAMLIT
st.set_page_config(layout="wide")
st.header('Eléctrica Industrial EL SHADDAI')
st.subheader('HORAS DE TRABAJO')
st.text(f'- powered by Google Gemini AI model {model_name}')
st.divider()

st.sidebar.markdown("# Menu")
# Define language to be used
lang = st.sidebar.selectbox("Select language:", LANG)

# Tabs
TAB_0 = 'Falar'
TAB_1 = 'Carregar arquivo'

tab = option_menu(
    menu_title='',
    options=['Falar', 'Carregar arquivo'],
    icons=['bi bi-mic-fill','bi-filetype-mp3'],
    menu_icon='cast',
    orientation='horizontal',
    default_index=0
)

if tab == TAB_0:
    # Enter the audio
    audio_value = st.audio_input("Clique no ícone do microfone para começar a falar e clique novamente para finalizar:")
    process_audio(audio_value, model_name, DESC)

if tab == TAB_1:
    # Select the audio file
    audio_value = st.file_uploader(label='Selecione o arquivo:', type=['mp3', 'm4a', 'wav'])
    process_audio(audio_value, model_name, DESC)
