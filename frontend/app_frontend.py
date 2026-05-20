import os

import streamlit as st
import requests

def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

# 1. ICONO DE PESTAÑA REAL (Una Pokéball de verdad)
st.set_page_config(
    page_title="Poké-Tasador IA", 
    page_icon="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png", 
    layout="centered"
)
load_css("assets/style.css")

# --- 2. LA NUEVA PORTADA GUAY ---
# Usamos columnas para alinear una imagen chula con el título
col_img, col_texto = st.columns([1, 4])

with col_img:
    # Metemos a Charizard de mascota oficial
    st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png", width=120)

with col_texto:
    st.markdown("<h1 style='color: #EE1515; margin-bottom: 0px;'>Poké-Tasador IA</h1>", unsafe_allow_html=True)
    st.markdown("<b>La primera Inteligencia Artificial que tasa tus cartas TCG en segundos.</b>", unsafe_allow_html=True)

st.write("Sube una foto de tu carta y nuestra red neuronal evaluará su estado (Mint, Played o Damaged) para calcular su valor real de mercado.")

st.markdown("---")

# --- 3. MEMORIA DEL BUSCADOR ---
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "card_selected" not in st.session_state:
    st.session_state.card_selected = None

# --- 4. PASO 1: IDENTIFICACIÓN CON ESTILO ---
st.markdown("### 🔍 1. Identifica tu carta")
col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input("Nombre del Pokémon", placeholder="Ej: Pikachu, Charizard, Lugia...")
with col2:
    st.write("") # Espaciador
    st.write("")
    if st.button("Buscar Cartas"):
        if search_query:
            with st.spinner("Llamando a la Pokédex mundial..."):
                res = requests.get(f"https://api.pokemontcg.io/v2/cards?q=name:\"{search_query}\"&pageSize=15")
                if res.status_code == 200:
                    data = res.json().get("data", [])
                    if data:
                        st.session_state.search_results = [
                            {"id": c["id"], "label": f"{c['name']} - {c['set']['name']} ({c['id']})"} 
                            for c in data
                        ]
                    else:
                        st.warning("No se encontraron cartas con ese nombre.")
                        st.session_state.search_results = []

# --- 5. PASO 2: DESPLEGABLE Y FOTO ---
if st.session_state.search_results:
    opciones = {c["label"]: c["id"] for c in st.session_state.search_results}
    seleccion_label = st.selectbox("Selecciona tu edición exacta:", list(opciones.keys()))
    card_id = opciones[seleccion_label]
    
    st.markdown("---")
    
    st.markdown("### 📸 2. Sube la foto y Tasa")
    uploaded_file = st.file_uploader("Arrastra aquí la foto de tu carta (JPG/PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        col_pic, col_btn = st.columns([1, 2])
        with col_pic:
            st.image(uploaded_file, caption="Tu carta", use_container_width=True)
            
        with col_btn:
            st.write("")
            st.write("")
            # Botón principal enorme
            if st.button("🔴 TASAR CON IA AHORA", use_container_width=True):
                with st.spinner("Analizando micro-roturas y estado de los bordes..."):
                    try:
                        # Conectar con el backend configurado por variable de entorno.
                        api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
                        url_appraise = f"{api_base_url}/api/v1/appraise"
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        data = {"card_id": card_id}
                        
                        response = requests.post(url_appraise, files=files, data=data, timeout=60)
                        
                        if response.status_code == 200:
                            resultado = response.json()
                            st.success("¡Análisis completado con éxito!")
                            
                            # Cajas de resultados
                            col_a, col_b, col_c = st.columns(3)
                            col_a.metric("Estado Detectado", str(resultado['predicted_condition']).upper())
                            col_b.metric("Precio Base (Mint)", f"{resultado['market_price']} €")
                            
                            delta = round(resultado['adjusted_price'] - resultado['market_price'], 2)
                            col_c.metric("Precio Tasado", f"{resultado['adjusted_price']} €", f"{delta} €")
                            
                            st.caption(f"🤖 Confianza de la red neuronal: {round(resultado['ai_confidence'] * 100, 2)}%")
                        else:
                            try:
                                error_msg = response.json().get('detail', 'Desconocido')
                            except Exception:
                                error_msg = response.text  # Si no es JSON, saca el texto crudo
                            st.error(f"Error del servidor (Código {response.status_code}): {error_msg}")
                            
                    except requests.exceptions.ConnectionError:
                        st.error("🚨 Error crítico: No se puede conectar con el servidor en AWS. ¿Está encendido?")