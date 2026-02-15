import streamlit as st
from datetime import datetime, date

st.set_page_config(
    page_title="Badí' App - Calendario Bahá'í",
    page_icon="☀️",
    layout="centered"
)

st.markdown("""
<style>
    .date-card {
        background: linear-gradient(135deg, #f59e0b, #ea580c);
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
    }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #f59e0b, #ea580c);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 10px 24px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

MESES_BHAI = [
    {"n": "Bahá", "s": "Esplendor", "g": "21 Mar"},
    {"n": "Jalál", "s": "Gloria", "g": "9 Abr"},
    {"n": "Jamál", "s": "Belleza", "g": "28 Abr"},
    {"n": "'Azamat", "s": "Grandeza", "g": "17 May"},
    {"n": "Núr", "s": "Luz", "g": "5 Jun"},
    {"n": "Rahmat", "s": "Misericordia", "g": "24 Jun"},
    {"n": "Kalimát", "s": "Palabras", "g": "13 Jul"},
    {"n": "Kamál", "s": "Perfección", "g": "1 Ago"},
    {"n": "Asmá'", "s": "Nombres", "g": "20 Ago"},
    {"n": "'Izzat", "s": "Fuerza", "g": "8 Sep"},
    {"n": "Mashíyyat", "s": "Voluntad", "g": "27 Sep"},
    {"n": "'Ilm", "s": "Conocimiento", "g": "16 Oct"},
    {"n": "Qudrat", "s": "Poder", "g": "4 Nov"},
    {"n": "Qawl", "s": "Discurso", "g": "23 Nov"},
    {"n": "Masá'il", "s": "Preguntas", "g": "12 Dic"},
    {"n": "Sharaf", "s": "Honor", "g": "31 Dic"},
    {"n": "Sultán", "s": "Soberanía", "g": "19 Ene"},
    {"n": "Mulk", "s": "Dominio", "g": "7 Feb"},
    {"n": "'Alá", "s": "Sublimidad", "g": "2 Mar"}
]

DIAS_SAGRADOS = [
    {"n": "Naw-Rúz", "d": "21 de Marzo", "s": "Año Nuevo Bahá'í", "t": "Suspende trabajo"},
    {"n": "1er día de Ridván", "d": "21 de Abril", "s": "Fiesta de Ridván", "t": "Suspende trabajo"},
    {"n": "9no día de Ridván", "d": "29 de Abril", "s": "Fiesta de Ridván", "t": "Suspende trabajo"},
    {"n": "12vo día de Ridván", "d": "2 de Mayo", "s": "Fiesta de Ridván", "t": "Suspende trabajo"},
    {"n": "Declaración del Báb", "d": "23 de Mayo", "s": "Misión del Báb", "t": "Suspende trabajo"},
    {"n": "Ascensión de Bahá'u'lláh", "d": "29 de Mayo", "s": "Fallecimiento", "t": "Suspende trabajo"},
    {"n": "Martirio del Báb", "d": "9 de Julio", "s": "Sacrificio", "t": "Suspende trabajo"},
    {"n": "Nacimiento del Báb", "d": "Variable", "s": "Nacimiento", "t": "Suspende trabajo"},
    {"n": "Nacimiento de Bahá'u'lláh", "d": "Variable", "s": "Nacimiento", "t": "Suspende trabajo"},
    {"n": "Día del Convenio", "d": "26 de Noviembre", "s": "Convenio", "t": "No suspende"},
    {"n": "Ascensión de 'Abdu'l-Bahá", "d": "28 de Noviembre", "s": "Fallecimiento", "t": "Conmemorativo"}
]

def calcular_fecha_bhai(fecha):
    year = fecha.year
    naw_ruz = date(year, 3, 21)
    start_year = year
    
    if fecha < naw_ruz:
        start_year = year - 1
        naw_ruz = date(start_year, 3, 21)
    
    diff_days = (fecha - naw_ruz).days
    bhai_year = start_year - 1844 + 1
    
    is_leap = (start_year % 4 == 0 and start_year % 100 != 0) or (start_year % 400 == 0)
    ayyam_days = 5 if is_leap else 4
    
    if diff_days < 18 * 19:
        idx = diff_days // 19
        month = MESES_BHAI[idx]["n"]
        meaning = MESES_BHAI[idx]["s"]
        day = (diff_days % 19) + 1
    elif diff_days < 18 * 19 + ayyam_days:
        month = "Ayyám-i-Há"
        meaning = "Días Intercalares"
        day = (diff_days - 18 * 19) + 1
    else:
        month = MESES_BHAI[18]["n"]
        meaning = MESES_BHAI[18]["s"]
        day = (diff_days - (18 * 19 + ayyam_days)) + 1
    
    return {"day": day, "month": month, "meaning": meaning, "year": bhai_year}

if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("""
<div style="background: linear-gradient(135deg, #f59e0b, #ea580c); padding: 20px; border-radius: 20px; text-align: center; color: white;">
    <h1>☀️ Badí' App</h1>
    <p>Calendario Bahá'í con IA Espiritual</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Inicio", "📅 Conversor", "⭐ Sagrados", "📖 Meses", "🤖 IA"])

with tab1:
    bhai = calcular_fecha_bhai(date.today())
    hora = datetime.now().hour
    es_noche = hora >= 19 or hora < 6
    
    st.markdown(f"""
    <div class="date-card">
        <p style="font-size: 14px; opacity: 0.8;">HOY ES</p>
        <h1 style="font-size: 72px; margin: 0;">{bhai['day']}</h1>
        <h2 style="font-size: 32px;">{bhai['month']}</h2>
        <p style="font-size: 20px; font-style: italic;">"{bhai['meaning']}"</p>
        <hr style="border-color: rgba(255,255,255,0.3);">
        <p style="font-size: 14px; opacity: 0.8;">ERA BAHÁ'Í</p>
        <h2>{bhai['year']} B.E.</h2>
        <p>{'🌙 Noche' if es_noche else '☀️ Día'}</p>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("### 📅 Conversor de Fechas")
    fecha = st.date_input("Selecciona una fecha")
    bhai = calcular_fecha_bhai(fecha)
    st.markdown(f"""
    <div style="background: #1e293b; padding: 30px; border-radius: 20px; text-align: center; color: white;">
        <p style="color: #fbbf24;">FECHA BAHÁ'Í</p>
        <h1>{bhai['day']} de {bhai['month']}</h1>
        <p style="color: #fbbf24; font-style: italic;">"{bhai['meaning']}"</p>
        <p style="color: #94a3b8;">Año {bhai['year']} B.E.</p>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown("### ⭐ Días Sagrados")
    for ds in DIAS_SAGRADOS:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #fef3c7, #fed7aa); padding: 15px; border-radius: 15px; margin: 10px 0;">
            <h4 style="margin: 0;">{ds['n']}</h4>
            <p style="color: #ea580c; font-weight: bold; margin: 5px 0;">{ds['d']}</p>
            <span style="background: #e2e8f0; padding: 5px 10px; border-radius: 8px; font-size: 12px;">{ds['s']}</span>
            <span style="background: #fbbf24; color: white; padding: 5px 10px; border-radius: 8px; font-size: 12px; margin-left: 5px;">{ds['t']}</span>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.markdown("### 📖 Los 19 Meses")
    for i, mes in enumerate(MESES_BHAI):
        st.markdown(f"""
        <div style="background: white; padding: 15px; border-radius: 15px; border: 1px solid #e2e8f0; margin: 10px 0; display: flex; align-items: center;">
            <div style="background: #f1f5f9; width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: bold;">{i+1}</div>
            <div style="margin-left: 15px;">
                <h4 style="margin: 0;">{mes['n']}</h4>
                <p style="color: #ea580c; margin: 0;">{mes['s']}</p>
            </div>
            <div style="margin-left: auto; background: #f1f5f9; padding: 8px 12px; border-radius: 8px; font-size: 12px;">{mes['g']}</div>
        </div>
        """, unsafe_allow_html=True)

with tab5:
    st.markdown("### 🤖 IA Espiritual")
    st.write("Pregúntame sobre la Fe Bahá'í")
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div style="background: #f59e0b; color: white; padding: 15px; border-radius: 15px; margin: 10px 0;">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background: #f1f5f9; padding: 15px; border-radius: 15px; margin: 10px 0;">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    
    pregunta = st.text_input("Escribe tu pregunta:")
    if st.button("Enviar") and pregunta:
        st.session_state.messages.append({"role": "user", "content": pregunta})
        
        if "principio" in pregunta.lower():
            respuesta = "Los principios Bahá'ís incluyen: unidad de la humanidad, igualdad de géneros, armonía de ciencia y religión, eliminación de prejuicios, y paz mundial. 🌟"
        elif "oración" in pregunta.lower():
            respuesta = "Oración de Bahá'u'lláh: '¡Oh Dios, mi Dios! Tú me has despertado de mi sueño para celebrar Tu alabanza...' 🙏"
        elif "ridván" in pregunta.lower():
            respuesta = "Ridván es la fiesta más sagrada, conmemora cuando Bahá'u'lláh declaró su misión en 1863. Se celebra del 21 abril al 2 mayo. 🌷"
        else:
            respuesta = "Puedo ayudarte con: principios Bahá'ís, oraciones, días sagrados, y el calendario Badí'. ¿Qué te interesa? 🌺"
        
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
        st.rerun()

st.markdown("<p style='text-align: center; color: #94a3b8;'>☀️ Badí' App - Hecho con ❤️</p>", unsafe_allow_html=True)
