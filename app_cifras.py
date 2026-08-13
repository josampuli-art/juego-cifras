import streamlit as st
import random

# --- 1. LÓGICA MATEMÁTICA: GENERADORES ---
def generar_partida_clasica():
    fichas_disponibles = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 25, 50, 75, 100]
    return random.sample(fichas_disponibles, 6)

def generar_partida_mas():
    return [random.randint(1, 100) for _ in range(6)]

def construir_partida_con_fichas(fichas_iniciales):
    fichas_trabajo = fichas_iniciales.copy()
    max_ficha = max(fichas_iniciales)
    
    b = random.randint(3, 5)
    operaciones_restantes = b
    
    historial_pasos = []
    resultado_exacto = 0
    
    while operaciones_restantes > 0 and len(fichas_trabajo) >= 2:
        idx1, idx2 = random.sample(range(len(fichas_trabajo)), 2)
        n1 = fichas_trabajo[idx1]
        n2 = fichas_trabajo[idx2]
        
        a = random.randint(1, 4)
        operacion_valida = False
        
        if a == 1:
            resultado = n1 + n2
            paso_str = f"{n1} + {n2} = {resultado}"
            operacion_valida = True
        elif a == 2:
            if n1 != n2:
                mayor, menor = max(n1, n2), min(n1, n2)
                resultado = mayor - menor
                paso_str = f"{mayor} - {menor} = {resultado}"
                operacion_valida = True
        elif a == 3:
            resultado = n1 * n2
            paso_str = f"{n1} * {n2} = {resultado}"
            operacion_valida = True
        elif a == 4:
            mayor, menor = max(n1, n2), min(n1, n2)
            if menor > 1 and mayor % menor == 0:
                resultado = mayor // menor
                paso_str = f"{mayor} / {menor} = {resultado}"
                operacion_valida = True
        
        if operacion_valida:
            for idx in sorted([idx1, idx2], reverse=True):
                fichas_trabajo.pop(idx)
            fichas_trabajo.append(resultado)
            historial_pasos.append(paso_str)
            operaciones_restantes -= 1
            resultado_exacto = resultado

    if historial_pasos:
        valores_c = list(range(-15, 16))
        pesos = [0.05 / 30 if v != 0 else 0.95 for v in valores_c]
        c = random.choices(valores_c, weights=pesos)[0]
        objetivo_final = resultado_exacto + c
        
        if objetivo_final > max_ficha:
            return fichas_iniciales, objetivo_final, historial_pasos, c, resultado_exacto
    
    return None

def generar_partida_cifras(modo="clasico"):
    while True:
        if modo == "clasico":
            fichas_iniciales = generar_partida_clasica()
        else:
            fichas_iniciales = generar_partida_mas()
            
        resultado = construir_partida_con_fichas(fichas_iniciales)
        if resultado is not None:
            return resultado

# --- 2. LÓGICA MATEMÁTICA: RESOLVEDOR (Backtracking DFS) ---
def resolver_cifras_motor(numeros_iniciales, objetivo):
    mejor_diferencia = float('inf')
    mejor_aproximacion = None
    mejor_camino = []
    soluciones_encontradas = set()
    exitos_brutos = 0  

    def dfs(numeros, camino_actual):
        nonlocal mejor_diferencia, mejor_aproximacion, mejor_camino, soluciones_encontradas, exitos_brutos

        if len(numeros) <= 1:
            return

        for i in range(len(numeros)):
            for j in range(i + 1, len(numeros)):
                n1, n2 = numeros[i], numeros[j]
                mayor, menor = max(n1, n2), min(n1, n2)
                restantes = [numeros[k] for k in range(len(numeros)) if k != i and k != j]

                operaciones = []
                operaciones.append((mayor + menor, f"{mayor} + {menor} = {mayor + menor}"))
                
                if mayor > menor:
                    operaciones.append((mayor - menor, f"{mayor} - {menor} = {mayor - menor}"))
                    
                if menor > 1:
                    operaciones.append((mayor * menor, f"{mayor} * {menor} = {mayor * menor}"))
                    
                if menor > 1 and mayor % menor == 0:
                    operaciones.append((mayor // menor, f"{mayor} / {menor} = {mayor // menor}"))

                for resultado, paso_str in operaciones:
                    nuevo_camino = camino_actual + [paso_str]
                    diferencia = abs(resultado - objetivo)

                    if diferencia < mejor_diferencia:
                        mejor_diferencia = diferencia
                        mejor_aproximacion = resultado
                        mejor_camino = nuevo_camino

                    if diferencia == 0:
                        exitos_brutos += 1
                        camino_tupla = tuple(sorted(nuevo_camino))
                        if camino_tupla not in soluciones_encontradas:
                            soluciones_encontradas.add(camino_tupla)
                    else:
                        if len(restantes) + 1 >= 2:
                            dfs(restantes + [resultado], nuevo_camino)
                            
    for n in numeros_iniciales:
        diff = abs(n - objetivo)
        if diff < mejor_diferencia:
            mejor_diferencia = diff
            mejor_aproximacion = n
            mejor_camino = [f"La ficha {n} ya era el objetivo inicial."]

    if mejor_diferencia != 0:
        dfs(numeros_iniciales, [])
    
    return list(soluciones_encontradas), mejor_aproximacion, mejor_diferencia, mejor_camino, exitos_brutos


# --- 3. INTERFAZ GRÁFICA (Streamlit) ---
st.set_page_config(page_title="Juego de Cifras", page_icon="🔢", layout="centered")

st.title("🔢 El Juego de Cifras")
st.write("Generador y Resolutor con análisis combinatorio en profundidad.")

st.divider()

tab_juego, tab_resolutor = st.tabs(["🎮 Modo Juego (Generador)", "🧠 Resolutor Manual"])

# ==========================================
# PESTAÑA 1: MODO JUEGO
# ==========================================
with tab_juego:
    if 'partida_activa' not in st.session_state:
        st.session_state.partida_activa = False

    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🎮 Modo Clásico", type="primary", use_container_width=True):
            fichas, objetivo, pasos, c, resultado_exacto = generar_partida_cifras(modo="clasico")
            st.session_state.fichas = fichas
            st.session_state.objetivo = objetivo
            st.session_state.pasos = pasos
            st.session_state.c = c
            st.session_state.resultado_exacto = resultado_exacto
            st.session_state.partida_activa = True
                
    with col_btn2:
        if st.button("🔥 Modo +", type="secondary", use_container_width=True):
            fichas, objetivo, pasos, c, resultado_exacto = generar_partida_cifras(modo="mas")
            st.session_state.fichas = fichas
            st.session_state.objetivo = objetivo
            st.session_state.pasos = pasos
            st.session_state.c = c
            st.session_state.resultado_exacto = resultado_exacto
            st.session_state.partida_activa = True

    if st.session_state.partida_activa:
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Tus 6 números:")
            st.info("  ".join([str(num) for num in st.session_state.fichas]))
            
        with col2:
            st.metric(label="🎯 Tu Meta", value=str(st.session_state.objetivo))
            
        st.divider()
        
        col_izq, col_der = st.columns(2)
        with col_izq:
            if st.button("Ver el camino original del generador"):
                st.subheader("--- Solución Original ---")
                if st.session_state.c == 0:
                    st.success(f"Existe solución exacta para llegar a {st.session_state.objetivo}.")
                else:
                    st.warning(f"Se generó partiendo del {st.session_state.resultado_exacto} (diferencia de {abs(st.session_state.c)}).")
                for i, paso in enumerate(st.session_state.pasos, 1):
                    st.code(f"Paso {i}: {paso}")

        with col_der:
            if st.button("Que la máquina calcule TODAS las soluciones 🧠", key="btn_motor_juego"):
                with st.spinner("Explorando cientos de miles de ramas combinatorias..."):
                    soluciones, mejor_aprox, mejor_diff, mejor_camino, exitos = resolver_cifras_motor(
                        st.session_state.fichas, st.session_state.objetivo
                    )
                st.subheader("📊 Análisis del motor matemático")
                if not soluciones:
                    st.warning("No existe ninguna forma matemática de llegar al número exacto.")
                    st.info(f"Mejor aproximación encontrada: {mejor_aprox} (Diferencia de {mejor_diff})")
                    for i, paso in enumerate(mejor_camino, 1):
                        st.code(f"Paso {i}: {paso}")
                else:
                    st.success(f"Se encontraron {len(soluciones)} formas únicas de operar.")
                    st.write(f"Ramas del árbol que llegaron al resultado: {exitos}")
                    max_mostrar = min(10, len(soluciones))
                    for idx, sol in enumerate(soluciones[:max_mostrar], 1):
                        with st.expander(f"Ver Opción {idx}"):
                            for paso in sol:
                                st.code(paso)
                    if len(soluciones) > 10:
                        st.caption(f"... y {len(soluciones) - 10} combinaciones más ocultas.")

# ==========================================
# PESTAÑA 2: RESOLUTOR MANUAL
# ==========================================
with tab_resolutor:
    st.subheader("Introduce tus propios números")
    st.write("Introduce 6 números naturales (enteros mayores que cero) y un número objetivo.")
    
    cols = st.columns(6)
    n1 = cols[0].number_input("Nº 1", min_value=1, step=1, value=1)
    n2 = cols[1].number_input("Nº 2", min_value=1, step=1, value=2)
    n3 = cols[2].number_input("Nº 3", min_value=1, step=1, value=3)
    n4 = cols[3].number_input("Nº 4", min_value=1, step=1, value=4)
    n5 = cols[4].number_input("Nº 5", min_value=1, step=1, value=5)
    n6 = cols[5].number_input("Nº 6", min_value=1, step=1, value=10)
    
    objetivo_manual = st.number_input("🎯 Número Objetivo", min_value=1, step=1, value=100)
    
    if st.button("Resolver combinación manual", type="primary", key="btn_manual"):
        numeros_manuales = [n1, n2, n3, n4, n5, n6]
        todos_los_numeros = numeros_manuales + [objetivo_manual]
        
        son_naturales = all(isinstance(n, int) and n > 0 for n in todos_los_numeros)
        
        if not son_naturales:
            st.error("⚠️ Error: Todos los valores deben ser números naturales (enteros positivos mayores que 0). Por favor, revisa tu entrada.")
        else:
            with st.spinner("Calculando todas las combinaciones posibles..."):
                soluciones_m, aprox_m, diff_m, camino_m, exitos_m = resolver_cifras_motor(
                    numeros_manuales, objetivo_manual
                )
                
            st.divider()
            st.subheader(f"📊 Resultados para conseguir el {objetivo_manual}")
            
            if not soluciones_m:
                st.warning("No existe ninguna forma matemática de llegar al número exacto con estas fichas.")
                st.info(f"Mejor aproximación posible: {aprox_m} (Diferencia de {diff_m})")
                st.write("Se obtiene ejecutando la siguiente secuencia:")
                for i, paso in enumerate(camino_m, 1):
                    st.code(f"Paso {i}: {paso}")
            else:
                st.success(f"¡Análisis completado! Se encontraron {len(soluciones_m)} formas matemáticas únicas de operar.")
                st.write(f"Ramas del árbol exploradas exitosamente: {exitos_m}")
                
                max_mostrar_m = min(15, len(soluciones_m))
                if max_mostrar_m > 0:
                    st.write(f"Mostrando las primeras {max_mostrar_m} soluciones:")
                    
                    for idx, sol in enumerate(soluciones_m[:max_mostrar_m], 1):
                        with st.expander(f"Ver Opción {idx}"):
                            for paso in sol:
                                st.code(paso)
                                
                    if len(soluciones_m) > 15:
                        st.caption(f"... y {len(soluciones_m) - 15} combinaciones más que se han ocultado.")