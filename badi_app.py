import streamlit as st
from datetime import datetime, date, timedelta
import json
import os

# Configuración de la página
st.set_page_config(
    page_title="Badí' App - Calendario Bahá'í",
    page_icon="☀️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #f59e0b, #ea580c);
        padding: 20px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .date-card {
        background: linear-gradient(135deg, #f59e0b, #ea580c);
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
    }
    .activity-card {
        background: white;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .holy-day-card {
        background: linear-gradient(135deg, #fef3c7, #fed7aa);
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
    }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #f59e0b, #ea580c);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 10px 24px;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #d97706, #c2410c);
    }
    .chat-user {
        background: #f59e0b;
        color: white;
        padding: 15px;
        border-radius: 15px 15px 5px 15px;
        margin: 10px 0;
        margin-left: 40px;
    }
    .chat-ai {
        background: #f1f5f9;
        color: #1e293b;
        padding: 15px;
        border-radius: 15px 15px 15px 5px;
        margin: 10px 0;
        margin-right: 40px;
    }
</style>
""", unsafe_allow_html=True)

# Los 19 meses del calendario Bahá'í
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

# Los 11 Días Sagrados
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

# Tipos de actividades
TIPOS_ACTIVIDADES = [
    "🎉 Fiesta de 19 Días",
    "⭐ Día Sagrado",
    "🏠 Visita a Hogares",
    "👶 Clase de Niños",
    "teen Grupos Prejuveniles",
    "📚 Círculo de Estudio",
    "🙏 Reunión Devocional",
    "📢 Enseñanza",
    "🤝 Servicio",
    "📝 Otro"
]

# ============== FUNCIONES ==============

def calcular_fecha_bhai(fecha):
    """Calcula la fecha Bahá'í"""
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

def generar_respuesta_ia(pregunta):
    """Genera respuestas detalladas sobre la Fe Bahá'í"""
    p = pregunta.lower()
    
    # PRINCIPIOS BAHÁ'ÍS
    if "principio" in p or "enseñanza" in p or "creencia" in p:
        return """## 🌟 Los Principios Fundamentales de la Fe Bahá'í

La Fe Bahá'í enseña que existe un solo Dios y que todas las religiones del mundo provienen de la misma Fuente divina. Bahá'u'lláh, el Profeta-Fundador, reveló enseñanzas para la construcción de una civilización mundial unificada.

### Principios Sociales:

**1. Unidad de la Humanidad**
> "La tierra es un solo país y la humanidad sus ciudadanos." - Bahá'u'lláh

Todos los seres humanos forman una sola familia. Las diferencias de raza, nacionalidad o cultura son enrichcedoras, no divisorias.

**2. Igualdad de Mujeres y Hombres**
> "El mundo de la humanidad posee dos alas: el hombre y la mujer. Si las dos alas no están igualmente desarrolladas, el ave no puede volar." - 'Abdu'l-Bahá

La igualdad de género es esencial para el progreso de la civilización.

**3. Armonía de Ciencia y Religión**
La ciencia y la religión son compatibles y necesarias. La religión sin ciencia puede caer en la superstición; la ciencia sin religión puede volverse materialista.

**4. Eliminación de Todos los Prejuicios**
Los prejuicios de raza, religión, clase económica, nacionalidad o género deben ser abandonados.

**5. Educación Universal**
Cada persona debe tener acceso a la educación, que es fundamental para el progreso individual y colectivo.

**6. Lenguaje Auxiliar Universal**
Se propone la adopción de un idioma auxiliar mundial, además del idioma nativo de cada pueblo.

**7. Paz Mundial**
El establecimiento de una federación mundial de naciones que garantice la paz y seguridad colectivas.

### Principios Espirituales:

- **Investigación independiente de la verdad**: Cada persona debe buscar la verdad por sí misma.
- **Oración y meditación diarias**: La comunicación con Dios es esencial para el alma.
- **Servicio a la humanidad**: El servicio desinteresado es una forma de adoración.
- **Virtudes morales**: Honestidad, confianza en Dios, paciencia, generosidad.

¿Te gustaría profundizar en algún principio específico? 🌺"""

    # ORACIONES
    elif "oración" in p or "oracion" in p or "plegaria" in p:
        return """## 🙏 Oraciones Bahá'ís

Aquí te comparto oraciones de los escritos sagrados de Bahá'u'lláh, el Báb y 'Abdu'l-Bahá:

### Oración para la Mañana

> *"¡Oh Dios, mi Dios! Tú me has despertado de mi sueño y me has hecho salir de mi lecho para celebrar Tu alabanza y adorar Tu belleza. Me has dotado de ojos para contemplar las maravillas de Tu Revelación, y de oídos para escuchar las melodías de Tu Palabra.*
> 
> *Te suplico, oh Tú, Bienamado de los corazones y Deseo de las almas, que por Tu misericordia me ayudes a consagrar mis pensamientos a Tu recuerdo, mis ojos a la contemplación de Tus signos y mi lengua a la mención de Tu Nombre."*
> 
> — Bahá'u'lláh

---

### Oración para la Noche

> *"¡Oh mi Dios! ¡Oh mi Dios! Te pido por Tu Nombre, el Más Santificado, el Todopoderoso, el Incomparable, que pases la noche conmigo en el reino de Tu gloria y me acerques a Ti.*"
> 
> — El Báb

---

### Oración para Dificultades

> *"¡Oh Dios, mi Dios! Soy tu siervo y el hijo de tu siervo. Me he levantado a esta hora para adorarte, en el alba de la mañana, mientras las glorias de la aurora se manifiestan en todo su esplendor.*
> 
> *Te suplico, oh Tú que eres el Deseo del mundo, que me ayudes a hacer lo que tú has ordenado en tu Libro, y me concedas lo que es tuyo por derecho.*"
> 
> — 'Abdu'l-Bahá

---

### Oración Corta para Protección

> *"¡Oh Señor! Protégeme de todo lo que es contrario a Tu voluntad, y purifícame de todo mal."*

¿Quieres una oración para alguna necesidad específica? 🌙"""

    # RIDVÁN
    elif "ridván" in p:
        return """## 🌷 La Fiesta de Ridván

### Significado

**Ridván** (en árabe: رضوان) significa "Paraíso" y es la festividad más sagrada del calendario Bahá'í. Conmemora los 12 días que Bahá'u'lláh pasó en el Jardín de Ridván en Bagdad, del 21 de abril al 2 de mayo de 1863.

---

### Contexto Histórico

En 1863, Bahá'u'lláh fue exiliado de Bagdad hacia Constantinopla (hoy Estambul). Antes de partir, se detuvo en el Jardín de Ridván, donde durante 12 días recibió a numerosos visitantes y declaró públicamente que Él era aquel cuya venida había sido prometida por el Báb.

> "El Jardín de Ridván es el lugar donde Él ha hecho manantar sobre toda la humanidad los esplendores de Su nombre, el Todopoderoso." — Bahá'u'lláh

---

### Los Tres Días Sagrados

| Día | Fecha | Significado |
|-----|-------|-------------|
| **1er día** | 21 de abril | Día de la Declaración - Se suspende el trabajo |
| **9no día** | 29 de abril | Llegada de la familia - Se suspende el trabajo |
| **12vo día** | 2 de mayo | Partida hacia Constantinopla - Se suspende el trabajo |

---

### Cómo se Celebra

1. **Reuniones comunitarias** con oraciones y lecturas sagradas
2. **Elección de Asambleas Espirituales Locales y Nacional** durante este período
3. **Alegría y celebración** - se decoran los espacios con flores
4. **Reflexión** sobre el significado de la declaracion de Bahá'u'lláh

---

### Enseñanzas Clave de Ridván

Durante Ridván, Bahá'u'lláh proclamó principios fundamentales:

- Que no habría más guerras santas
- Que todas las religiones provienen del mismo Dios
- El inicio de una nueva era espiritual para la humanidad

¿Te gustaría saber más sobre la historia de Bahá'u'lláh? 🌸"""

    # MEDITACIÓN
    elif "meditacion" in p or "meditación" in p or "reflexion" in p:
        return """## 🧘 La Meditación Bahá'í

### Enseñanzas sobre la Meditación

La meditación en la Fe Bahá'í se centra en la **reflexión profunda de los escritos sagrados** y la comunión con Dios a través del silencio y la oración.

> *"Medid en vuestros corazones lo que os ha sido revelado."* — Bahá'u'lláh

> *"Cada mañana y cada noche, medita en las palabras de Dios, y extrae de ellas la luz de la guía."* — 'Abdu'l-Bahá

---

### Práctica Sencilla de Meditación

**1. Preparación (5 minutos)**
- Encuentra un lugar tranquilo
- El mejor momento es al **amanecer** o **atardecer**
- Siéntate cómodamente, con la espalda recta

**2. Lectura Sagrada (5-10 minutos)**
- Lee un pasaje de los escritos de Bahá'u'lláh
- Puedes comenzar con oraciones cortas

**3. Reflexión Silenciosa (10-15 minutos)**
- Cierra los ojos
- Repite mentalmente una frase sagrada
- Reflexiona: ¿Qué significa esto para mi vida?

**4. Oración (5 minutos)**
- Eleva tu corazón a Dios
- Expresa gratitud
- Pide guía para tu día

**5. Aplicación Práctica**
- Piensa: ¿Cómo puedo aplicar esta enseñanza hoy?
- Haz un compromiso concreto

---

### Frases para Meditar

Algunas frases de los escritos Bahá'ís para repetir en meditación:

- *"¡Oh Tú mi Dios! No permitas que me aparte de Ti."*
- *"Dios es el Más Grande."* (Alláh-u-Abhá)
- *"Tú me has creado, oh mi Dios, para conocerte y adorarte."*

---

### Beneficios de la Meditación Diaria

| Beneficio | Descripción |
|-----------|-------------|
| **Paz interior** | Calma la mente y el corazón |
| **Claridad** | Mejora la toma de decisiones |
| **Conexión espiritual** | Fortalece la relación con Dios |
| **Virtudes** | Desarrolla paciencia, humildad y sabiduría |

¿Quieres que te guíe en una meditación específica? 🌟"""

    # EL BÁB
    elif "báb" in p or "bab" in p or "babi" in p:
        return """## 🌟 El Báb - La Puerta

### ¿Quién fue el Báb?

**Siyyid 'Alí Muhammad** (1819-1850), conocido como el **Báb** (que significa "La Puerta" en árabe), fue el Profeta-Herald de la Fe Bahá'í. Declaró su misión en 1844 en Shiraz, Irán.

---

### Misión del Báb

El Báb anunció que venía a preparar el camino para otro Mensajero de Dios que vendría pronto:

> *"Yo soy la Puerta que conduce al Prometido. Él vendrá después de mí y será más grande que yo."* — El Báb

---

### Vida del Báb

| Año | Evento |
|-----|--------|
| **1819** | Nace en Shiraz, Irán |
| **1844** | Declara su misión (23 de mayo) |
| **1848** | Conferencia de Badasht |
| **1850** | Martirio en Tabriz (9 de julio) |

---

### El Martirio del Báb

El 9 de julio de 1850, el Báb fue ejecutado públicamente en Tabriz. Antes de morir, dijo:

> *"Hasta que no hayáis alcanzado la edad de treinta años, no os hablaré más, aunque me lo pidáis."*

Un evento milagroso ocurrió: la primera descarga de fusilamiento no lo mató y las cuerdas se rompieron. Fue encontrado de vuelta en su celda, terminando su conversación con su secretario.

---

### Escritos del Báb

- **Bayán Persa**: El libro sagrado más importante del Babismo
- **Bayán Árabe**: Versión árabe del Bayán
- **Oraciones y epístolas**: Numerosos escritos espirituales

---

### Enseñanzas Principales

1. La inminente aparición de "Aquel whom Dios manifestará" (Bahá'u'lláh)
2. Abolición de leyes y tradiciones anticuadas
3. Elevación del estatus de la mujer
4. Educación universal
5. Uso del calendario Badí' (19 meses de 19 días)

¿Quieres saber más sobre su conexión con Bahá'u'lláh? 🌺"""

    # BAHÁ'U'LLÁH
    elif "bahá'u'lláh" in p or "bahaullah" in p or "fundador" in p:
        return """## ☀️ Bahá'u'lláh - La Gloria de Dios

### ¿Quién fue Bahá'u'lláh?

**Mirzá Husayn-'Alí** (1817-1892), conocido como **Bahá'u'lláh** (que significa "La Gloria de Dios" en árabe), es el Profeta-Fundador de la Fe Bahá'í.

---

### Vida de Bahá'u'lláh

| Período | Evento |
|---------|--------|
| **1817** | Nace en Teherán, Irán (12 de noviembre) |
| **1844** | Acepta la fe del Báb |
| **1852** | Encarcelado en el "Pozo Negro" - recibe revelación |
| **1853** | Exiliado a Bagdad |
| **1863** | Declaración en el Jardín de Ridván |
| **1868** | Exiliado a 'Akká (Palestina) |
| **1892** | Fallece en Bahjí (29 de mayo) |

---

### Su Revelación

En el calabozo del "Pozo Negro" en Teherán, Bahá'u'lláh recibió la revelación de su misión divina:

> *"Durante los días que estuve en la prisión de Teherán, aunque la pena y el sufrimiento me rodeaban, recibí señales y promesas de una victoria inminente."* — Bahá'u'lláh

---

### Principales Escritos

- **Kitáb-i-Aqdas** (El Libro Más Sagrado): El libro de leyes fundamental
- **Kitáb-i-Íqán** (El Libro de la Certeza): Sobre la naturaleza de la revelación divina
- **Palabras Ocultas**: Colección de dichos éticos y espirituales
- **Las Siete Valles**: Tratado místico sobre el viaje del alma

---

### Enseñanzas Principales

1. **Unidad de Dios**: Un solo Creador para toda la humanidad
2. **Unidad de las Religiones**: Todas las religiones provienen del mismo Dios
3. **Unidad de la Humanidad**: Todos los humanos son iguales
4. **Educación Universal**: Obligatoria para todos
5. **Igualdad de Géneros**: Hombres y mujeres son iguales
6. **Paz Mundial**: Meta suprema de la civilización

---

### Citas Memorables

> *"La tierra es un solo país y la humanidad sus ciudadanos."*

> *"El mejor de los hombres es aquel que prefiere a los demás antes que a sí mismo."*

> *"No os gloriéis en vuestras obras, ni os vanagloriéis de vuestros actos."*

¿Te gustaría conocer más sobre sus escritos sagrados? 🌸"""

    # 'ABDU'L-BAHÁ
    elif "abdu'l-bahá" in p or "abdul" in p or "maestro" in p:
        return """## 🌺 'Abdu'l-Bahá - El Siervo de la Gloria

### ¿Quién fue 'Abdu'l-Bahá?

**'Abbás Effendi** (1844-1921), conocido como **'Abdu'l-Bahá** ("El Siervo de Bahá"), fue el hijo mayor de Bahá'u'lláh y el intérprete autorizado de sus enseñanzas.

---

### Su Papel Único

Bahá'u'lláh designó a 'Abdu'l-Bahá como:

- El **Centro del Convenio** - punto de unidad para los bahá'ís
- El **Intérprete Autorizado** de los escritos sagrados
- El **Ejemplo Perfecto** de vida bahá'í

---

### Viaje a Occidente (1911-1913)

A sus 67 años, 'Abdu'l-Bahá viajó a Europa y América:

| Año | Lugares visitados |
|-----|-------------------|
| **1911** | Egipto, Londres, París |
| **1912** | Nueva York, Chicago, San Francisco, Montreal |
| **1913** | Londres, París, Stuttgart, Budapest, Viena |

---

### Enseñanzas Destacadas

**Sobre la Unidad:**
> *"¿No ves que la luz del sol ilumina por igual a todos? De la misma manera, la luz de la verdad debe brillar sobre todos."*

**Sobre la Igualdad de la Mujer:**
> *"La humanidad es como un pájaro con dos alas: el hombre y la mujer. A menos que ambas alas estén igualmente desarrolladas, el pájaro no puede volar."*

**Sobre el Servicio:**
> *"El servicio a la humanidad es servicio a Dios."*

---

### Obras Importantes

- **Respuestas a Algunas Preguntas**: Explicaciones sobre temas espirituales y filosóficos
- **Tablas del Plan Divino**: Cartas sobre la expansión de la Fe
- **El Tratado Secreto**: Sobre la filosofía de la civilización
- **La Promulgación de la Paz Universal**: Discursos en América

---

### Su Testamento

En su testamento, 'Abdu'l-Bahá estableció el **Convenio** que garantiza la unidad de la Fe Bahá'í, designando a su nieto Shoghi Effendi como el primer Guardián.

¿Quieres saber más sobre el Convenio Bahá'í? 🌟"""

    # FIESTA DE 19 DÍAS
    elif "fiesta" in p or "19 dias" in p or "diecinueve" in p:
        return """## 🎉 La Fiesta de Diecinueve Días

### ¿Qué es?

La **Fiesta de Diecinueve Días** es la reunión comunitaria fundamental de la comunidad Bahá'í. Se celebra el **primer día de cada mes Bahá'í**.

---

### Los 19 Meses

El calendario Badí' tiene **19 meses de 19 días cada uno** (361 días), más los días intercalares de Ayyám-i-Há.

| # | Mes | Significado |
|---|-----|-------------|
| 1 | Bahá | Esplendor |
| 2 | Jalál | Gloria |
| 3 | Jamál | Belleza |
| 4 | 'Azamat | Grandeza |
| 5 | Núr | Luz |
| 6 | Rahmat | Misericordia |
| 7 | Kalimát | Palabras |
| 8 | Kamál | Perfección |
| 9 | Asmá' | Nombres |
| 10 | 'Izzat | Fuerza |
| 11 | Mashíyyat | Voluntad |
| 12 | 'Ilm | Conocimiento |
| 13 | Qudrat | Poder |
| 14 | Qawl | Discurso |
| 15 | Masá'il | Preguntas |
| 16 | Sharaf | Honor |
| 17 | Sultán | Soberanía |
| 18 | Mulk | Dominio |
| 19 | 'Alá | Sublimidad |

---

### Tres Partes de la Fiesta

**1. Parte Devocional** 🙏
- Lectura de escritos sagrados
- Oraciones
- Música espiritual

**2. Parte Administrativa** 📋
- Consulta comunitaria
- Informes y noticias
- Planificación de actividades

**3. Parte Social** 🍽️
- Compartir alimentos
- Fraternidad
- Celebración

---

### Propósito

> *"La Fiesta de Diecinueve Días fue instituida por Bahá'u'lláh para unir a los amigos en la amorosa comunión del uno con el otro."* — 'Abdu'l-Bahá

---

### Importancia

- Fortalece la **unidad comunitaria**
- Permite la **consulta y participación**
- Crea **lazos de amistad**
- Integra lo **espiritual y lo práctico**

¿Te gustaría saber cómo organizar una Fiesta? 🌸"""

    # AYYÁM-I-HÁ
    elif "ayyam" in p or "intercalar" in p:
        return """## 🎊 Ayyám-i-Há - Días Intercalares

### ¿Qué son?

Los **Ayyám-i-Há** (en árabe: "Días de Há") son los días intercalares del calendario Bahá'í. Se ubican entre el mes 18 (Mulk) y el mes 19 ('Alá), justo antes del ayuno.

---

### Duración

| Tipo de año | Días de Ayyám-i-Há |
|-------------|-------------------|
| Año normal | 4 días (26 feb - 1 mar) |
| Año bisiesto | 5 días (26 feb - 2 mar) |

---

### Significado Espiritual

- El "Há" representa la **esencia de Dios**
- Son días de **celebración, generosidad y hospitalidad**
- Tiempo de **preparación espiritual** antes del ayuno

---

### Cómo se Celebran

**1. Regalos y Generosidad** 🎁
- Intercambio de regalos
- Ayuda a los necesitados
- Actos de caridad

**2. Reuniones Festivas** 🎉
- Fiestas comunitarias
- Compartir comidas
- Celebraciones familiares

**3. Preparación Espiritual** 🙏
- Reflexión
- Oración
- Purificación del corazón

---

### Escritos sobre Ayyám-i-Há

> *"Estos días se han otorgado para que el pueblo de Bahá pueda proveerse de las provisiones necesarias para el viaje del ayuno."* — Bahá'u'lláh

---

### Tradiciones

- Dar regalos a niños y necesitados
- Fiestas especiales
- Decoración de hogares
- Visitas a amigos y familia
- Actos de servicio

¿Tienes alguna pregunta sobre cómo celebrarlos? 🌟"""

    # AYUNO
    elif "ayuno" in p or "ayunar" in p:
        return """## 🌙 El Ayuno Bahá'í

### ¿Qué es?

El **Ayuno de Diecinueve Días** es un período de ayuno obligatorio para los bahá'ís entre los **15 y 70 años**. Se realiza durante el mes de 'Alá (Sublimidad), el último mes del calendario Bahá'í.

---

### Período del Ayuno

| Detalle | Información |
|---------|-------------|
| **Mes** | 'Alá (Sublimidad) |
| **Duración** | 19 días |
| **Fechas aproximadas** | 2-20 de marzo |
| **Horario** | Desde el amanecer hasta el atardecer |

---

### Quiénes Ayunan

**Están obligados:**
- Personas entre **15 y 70 años**
- En buena salud

**Están exentos:**
- Menores de 15 años
- Mayores de 70 años
- Mujeres embarazadas o lactando
- Personas enfermas
- Viajeros
- Personas realizando trabajo físico pesado

---

### Propósito Espiritual

> *"Es un tiempo para la purificación del corazón, la renovación del alma y la reflexión espiritual."* — Bahá'u'lláh

El ayuno no es solo físico, sino un acto de devoción que incluye:
- Abstinencia de comida y bebida durante el día
- Oración y meditación
- Reflexión sobre la vida espiritual
- Control de los deseos materiales

---

### Beneficios

| Tipo | Beneficio |
|------|-----------|
| **Espiritual** | Cercanía a Dios, purificación del alma |
| **Físico** | Descanso del sistema digestivo |
| **Social** | Solidaridad con los necesitados |
| **Mental** | Disciplina, autocontrol |

---

### Después del Ayuno: Naw-Rúz

El último día del ayuno marca el fin del año Bahá'í, y al día siguiente se celebra **Naw-Rúz**, el Año Nuevo Bahá'í (21 de marzo).

---

### Oración para el Ayuno

> *"¡Oh mi Dios! Te suplico que me otorgues tu gracia durante estos días benditos, y que aceptes mi ayuno como un acto de adoración a Ti."*

¿Tienes alguna pregunta sobre el ayuno? 🌙"""

    # CALENDARIO BADÍ'
    elif "calendario" in p or "badi" in p or "badí" in p:
        return """## 📅 El Calendario Badí'

### Historia

El **Calendario Badí'** (que significa "Maravilloso") fue instituido por el Báb y confirmado por Bahá'u'lláh. Es el calendario oficial de la Fe Bahá'í.

---

### Características Principales

| Elemento | Descripción |
|----------|-------------|
| **Año** | Solar, comienza en Naw-Rúz (21 marzo) |
| **Meses** | 19 meses |
| **Días por mes** | 19 días |
| **Días totales** | 361 días |
| **Días intercalares** | 4-5 días (Ayyám-i-Há) |
| **Era** | B.E. (Bahá'í Era) desde 1844 |

---

### Los 19 Meses

| # | Nombre | Significado | Inicio aprox. |
|---|--------|-------------|---------------|
| 1 | Bahá | Esplendor | 21 marzo |
| 2 | Jalál | Gloria | 9 abril |
| 3 | Jamál | Belleza | 28 abril |
| 4 | 'Azamat | Grandeza | 17 mayo |
| 5 | Núr | Luz | 5 junio |
| 6 | Rahmat | Misericordia | 24 junio |
| 7 | Kalimát | Palabras | 13 julio |
| 8 | Kamál | Perfección | 1 agosto |
| 9 | Asmá' | Nombres | 20 agosto |
| 10 | 'Izzat | Fuerza | 8 sept |
| 11 | Mashíyyat | Voluntad | 27 sept |
| 12 | 'Ilm | Conocimiento | 16 oct |
| 13 | Qudrat | Poder | 4 nov |
| 14 | Qawl | Discurso | 23 nov |
| 15 | Masá'il | Preguntas | 12 dic |
| 16 | Sharaf | Honor | 31 dic |
| 17 | Sultán | Soberanía | 19 ene |
| 18 | Mulk | Dominio | 7 feb |
| 19 | 'Alá | Sublimidad | 2 marzo |

---

### Días de la Semana

| # | Día | Español |
|---|-----|---------|
| 1 | Jalál | Sábado |
| 2 | Jamál | Domingo |
| 3 | Kamál | Lunes |
| 4 | Fidál | Martes |
| 5 | 'Idál | Miércoles |
| 6 | Istijlál | Jueves |
| 7 | Istiqlál | Viernes |

---

### Cálculo del Año Bahá'í

El año 1 B.E. comenzó en 1844 (declaración del Báb).

Para calcular: **Año actual - 1844 = Año B.E.**

Ejemplo: 2024 - 1844 = 180 B.E. (aproximadamente)

¿Quieres saber cómo calcular fechas específicas? 🌟"""

    # SALUDO
    elif "hola" in p or "saludo" in p or "buenas" in p:
        return """## ☀️ ¡Hola! Bienvenido/a a Badí' App

¡Alláh-u-Abhá! (Dios es el Más Grande)

Soy **Badí'**, tu asistente espiritual Bahá'í. Estoy aquí para ayudarte en tu camino espiritual.

---

### ¿En qué puedo ayudarte?

Puedes preguntarme sobre:

📖 **Escritos Sagrados**
- Kitáb-i-Aqdas, Palabras Ocultas, Kitáb-i-Íqán

🌟 **Enseñanzas**
- Principios, virtudes, leyes espirituales

📅 **Calendario**
- Los 19 meses, días sagrados, Ayyám-i-Há

🙏 **Oraciones y Meditación**
- Oraciones para cada ocasión, prácticas espirituales

📚 **Historia**
- Vida de Bahá'u'lláh, el Báb, 'Abdu'l-Bahá

---

### Para comenzar, escribe:

- "¿Cuáles son los principios Bahá'ís?"
- "Comparte una oración para la mañana"
- "¿Qué es Ridván?"
- "¿Cómo meditar?"

¡Estoy aquí para servirte! 🌺"""

    # RESPUESTA POR DEFECTO
    else:
        return f"""Gracias por tu pregunta sobre: "{pregunta}"

## 🌺 Soy Badí', tu asistente espiritual Bahá'í

Puedo ayudarte con temas como:

### 📖 Escritos Sagrados
- Kitáb-i-Aqdas (El Libro Más Sagrado)
- Palabras Ocultas
- Kitáb-i-Íqán (El Libro de la Certeza)

### 🌟 Enseñanzas y Principios
- Unidad de la humanidad
- Igualdad de géneros
- Armonía de ciencia y religión
- Eliminación de prejuicios

### 📅 Calendario y Festividades
- Los 19 meses del año Bahá'í
- Los 11 días sagrados
- Ayyám-i-Há
- Naw-Rúz

### 🙏 Vida Espiritual
- Oraciones para cada ocasión
- Meditación y reflexión
- El ayuno de 19 días

### 👥 Figuras Centrales
- Bahá'u'lláh (el Fundador)
- El Báb (el Herald)
- 'Abdu'l-Bahá (el Intérprete)

---

**Intenta preguntar:**
- "¿Quién fue Bahá'u'lláh?"
- "¿Cuáles son los principios?"
- "¿Qué es la Fiesta de 19 Días?"
- "¿Cómo se celebra Ridván?"

¡Estoy aquí para ayudarte! ✨"""

# ============== FUNCIONES DE ACTIVIDADES ==============

def cargar_actividades():
    """Carga las actividades guardadas"""
    if "actividades" not in st.session_state:
        st.session_state.actividades = []
    return st.session_state.actividades

def guardar_actividad(actividad):
    """Guarda una nueva actividad"""
    actividades = cargar_actividades()
    actividades.append(actividad)
    st.session_state.actividades = actividades

def eliminar_actividad(indice):
    """Elimina una actividad"""
    actividades = cargar_actividades()
    if 0 <= indice < len(actividades):
        actividades.pop(indice)
    st.session_state.actividades = actividades

# ============== INTERFAZ PRINCIPAL ==============

# Inicializar session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.markdown("""
<div class="main-header">
    <h1>☀️ Badí' App</h1>
    <p>Calendario Bahá'í con IA Espiritual</p>
</div>
""", unsafe_allow_html=True)

# Navegación
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Inicio", "📅 Conversor", "⭐ Sagrados", "📖 Meses", "🤖 IA", "📋 Actividades"
])

# ============ TAB 1: INICIO ============
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
    
    # Próximas actividades
    st.markdown("### 📋 Próximas Actividades")
    actividades = cargar_actividades()
    
    if actividades:
        actividades_ordenadas = sorted(actividades, key=lambda x: x["fecha"])
        proximas = [a for a in actividades_ordenadas if a["fecha"] >= str(date.today())][:3]
        
        if proximas:
            for act in proximas:
                st.markdown(f"""
                <div class="activity-card">
                    <strong>{act['tipo']}</strong><br>
                    📅 {act['fecha']} | 👥 {act['participantes']} participantes<br>
                    📍 {act['lugar']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay actividades próximas programadas")
    else:
        st.info("No hay actividades registradas. Ve a la pestaña 'Actividades' para agregar.")

# ============ TAB 2: CONVERSOR ============
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

# ============ TAB 3: DÍAS SAGRADOS ============
with tab3:
    st.markdown("### ⭐ Días Sagrados")
    
    for ds in DIAS_SAGRADOS:
        color = "#fbbf24" if "Suspende" in ds["t"] else "#94a3b8"
        st.markdown(f"""
        <div class="holy-day-card">
            <h4 style="margin: 0;">{ds['n']}</h4>
            <p style="color: #ea580c; font-weight: bold; margin: 5px 0;">{ds['d']}</p>
            <span style="background: #e2e8f0; padding: 5px 10px; border-radius: 8px; font-size: 12px;">{ds['s']}</span>
            <span style="background: {color}; color: white; padding: 5px 10px; border-radius: 8px; font-size: 12px; margin-left: 5px;">{ds['t']}</span>
        </div>
        """, unsafe_allow_html=True)

# ============ TAB 4: LOS 19 MESES ============
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
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fef3c7, #fed7aa); padding: 20px; border-radius: 15px; margin-top: 15px;">
        <h4>🎉 Ayyám-i-Há - Días Intercalares</h4>
        <p style="color: #ea580c; margin: 0;">4-5 días antes del mes de 'Alá</p>
    </div>
    """, unsafe_allow_html=True)

# ============ TAB 5: IA ESPIRITUAL ============
with tab5:
    st.markdown("### 🤖 IA Espiritual")
    st.write("Conversa con Badí', tu asistente Bahá'í")
    
    # Mostrar historial
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-ai">{msg["content"]}</div>', unsafe_allow_html=True)
    
    # Preguntas sugeridas
    if len(st.session_state.messages) == 0:
        st.markdown("**Sugerencias:**")
        cols = st.columns(2)
        sugerencias = [
            "¿Cuáles son los principios Bahá'ís?",
            "¿Quién fue Bahá'u'lláh?",
            "¿Qué es Ridván?",
            "¿Cómo meditar?"
        ]
        for i, sug in enumerate(sugerencias):
            with cols[i % 2]:
                if st.button(sug, key=f"sug_{i}"):
                    st.session_state.messages.append({"role": "user", "content": sug})
                    respuesta = generar_respuesta_ia(sug)
                    st.session_state.messages.append({"role": "assistant", "content": respuesta})
                    st.rerun()
    
    # Input
    col_input, col_send = st.columns([4, 1])
    with col_input:
        pregunta = st.text_input("Escribe tu pregunta:", key="chat_input", label_visibility="collapsed")
    with col_send:
        if st.button("Enviar"):
            if pregunta:
                st.session_state.messages.append({"role": "user", "content": pregunta})
                respuesta = generar_respuesta_ia(pregunta)
                st.session_state.messages.append({"role": "assistant", "content": respuesta})
                st.rerun()
    
    # Limpiar chat
    if st.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.rerun()

# ============ TAB 6: REGISTRO DE ACTIVIDADES ============
with tab6:
    st.markdown("### 📋 Registro de Actividades")
    st.write("Lleva el control de tu agrupación Bahá'í")
    
    # Sub-tabs para actividades
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["➕ Nueva Actividad", "📅 Ver Actividades", "📊 Estadísticas"])
    
    # --- NUEVA ACTIVIDAD ---
    with sub_tab1:
        st.markdown("#### Registrar Nueva Actividad")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tipo = st.selectbox("Tipo de actividad", TIPOS_ACTIVIDADES)
            fecha_act = st.date_input("Fecha")
        
        with col2:
            lugar = st.text_input("Lugar")
            participantes = st.number_input("Participantes", min_value=0, value=0)
        
        notas = st.text_area("Notas adicionales")
        
        if st.button("💾 Guardar Actividad", type="primary"):
            if lugar:
                nueva_actividad = {
                    "tipo": tipo,
                    "fecha": str(fecha_act),
                    "lugar": lugar,
                    "participantes": participantes,
                    "notas": notas
                }
                guardar_actividad(nueva_actividad)
                st.success("✅ Actividad guardada correctamente")
                st.rerun()
            else:
                st.error("Por favor indica el lugar")
    
    # --- VER ACTIVIDADES ---
    with sub_tab2:
        st.markdown("#### Actividades Registradas")
        
        actividades = cargar_actividades()
        
        if actividades:
            # Filtros
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filtro_tipo = st.selectbox("Filtrar por tipo", ["Todos"] + TIPOS_ACTIVIDADES)
            with col_f2:
                filtro_fecha = st.date_input("Desde fecha", value=None)
            
            # Aplicar filtros
            actividades_filtradas = actividades
            if filtro_tipo != "Todos":
                actividades_filtradas = [a for a in actividades_filtradas if a["tipo"] == filtro_tipo]
            if filtro_fecha:
                actividades_filtradas = [a for a in actividades_filtradas if a["fecha"] >= str(filtro_fecha)]
            
            # Ordenar por fecha
            actividades_filtradas = sorted(actividades_filtradas, key=lambda x: x["fecha"], reverse=True)
            
            st.markdown(f"**Mostrando {len(actividades_filtradas)} actividades**")
            
            for i, act in enumerate(actividades_filtradas):
                with st.expander(f"{act['tipo']} - {act['fecha']}"):
                    col_info, col_del = st.columns([4, 1])
                    with col_info:
                        st.write(f"**Lugar:** {act['lugar']}")
                        st.write(f"**Participantes:** {act['participantes']}")
                        if act['notas']:
                            st.write(f"**Notas:** {act['notas']}")
                    with col_del:
                        if st.button("🗑️", key=f"del_{i}"):
                            eliminar_actividad(actividades.index(act))
                            st.rerun()
        else:
            st.info("No hay actividades registradas aún. Ve a 'Nueva Actividad' para agregar.")
    
    # --- ESTADÍSTICAS ---
    with sub_tab3:
        st.markdown("#### 📊 Estadísticas de la Agrupación")
        
        actividades = cargar_actividades()
        
        if actividades:
            # Total de actividades
            col_s1, col_s2, col_s3 = st.columns(3)
            
            with col_s1:
                st.metric("Total Actividades", len(actividades))
            
            with col_s2:
                total_participantes = sum(a["participantes"] for a in actividades)
                st.metric("Total Participantes", total_participantes)
            
            with col_s3:
                promedio = total_participantes / len(actividades) if actividades else 0
                st.metric("Promedio por Actividad", f"{promedio:.1f}")
            
            st.markdown("---")
            
            # Actividades por tipo
            st.markdown("##### Actividades por Tipo")
            conteo_tipos = {}
            for a in actividades:
                tipo = a["tipo"]
                conteo_tipos[tipo] = conteo_tipos.get(tipo, 0) + 1
            
            for tipo, cantidad in sorted(conteo_tipos.items(), key=lambda x: x[1], reverse=True):
                barra = "█" * cantidad
                st.markdown(f"{tipo}: {barra} {cantidad}")
            
            st.markdown("---")
            
            # Participantes por tipo
            st.markdown("##### Participantes por Tipo")
            participantes_tipo = {}
            for a in actividades:
                tipo = a["tipo"]
                participantes_tipo[tipo] = participantes_tipo.get(tipo, 0) + a["participantes"]
            
            for tipo, total in sorted(participantes_tipo.items(), key=lambda x: x[1], reverse=True):
                st.markdown(f"{tipo}: **{total}** participantes")
        
        else:
            st.info("Registra actividades para ver estadísticas")

# Footer
st.markdown("""
<div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 12px;">
    <p>☀️ Badí' App - Calendario Bahá'í con IA Espiritual</p>
    <p>Hecho con ❤️ para la comunidad Bahá'í</p>
</div>
""", unsafe_allow_html=True)

