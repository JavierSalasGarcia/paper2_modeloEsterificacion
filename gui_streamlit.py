#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interfaz Gráfica para Casos de Modelado de Biodiesel
Sistema web basado en Streamlit para usuarios no técnicos

Autores: J. Salas-García et al.
Fecha: 2025-11-23
"""

import streamlit as st
import os
import sys
import json
import subprocess
import time
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Modelado de Biodiesel",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de casos
CASOS = {
    1: {
        'nombre': 'Procesamiento GC-FID',
        'descripcion': 'Procesa datos de cromatografía de gases con detector de ionización de llama',
        'carpeta': 'Casos/caso1_procesamiento_gc',
        'json': 'config_caso1.json',
        'modo': 'process_gc',
        'emoji': '📊',
        'args_extra': ['--input', 'datos/experimento_60C.csv', '--c-tg0', '0.5']
    },
    2: {
        'nombre': 'Ajuste de Parámetros Cinéticos',
        'descripcion': 'Calibra parámetros del modelo mediante regresión no lineal',
        'carpeta': 'Casos/caso2_ajuste_parametros',
        'json': 'config_caso2.json',
        'modo': 'fit_params',
        'emoji': '🔧',
        'args_extra': ['--input', 'datos/datos_kouzu_4temps.json']
    },
    3: {
        'nombre': 'Optimización Multi-Objetivo',
        'descripcion': 'Encuentra condiciones operacionales óptimas para maximizar conversión',
        'carpeta': 'Casos/caso3_optimizacion',
        'json': 'config_caso3.json',
        'modo': 'optimize',
        'emoji': '🎯',
        'args_extra': ['--t-reaction', '90']
    },
    4: {
        'nombre': 'Comparación de Modelos',
        'descripcion': 'Compara modelo cinético de 1-paso versus 3-pasos',
        'carpeta': 'Casos/caso4_comparacion_modelos',
        'json': 'config_caso4.json',
        'modo': 'compare',
        'emoji': '⚖️',
        'args_extra': []
    },
    5: {
        'nombre': 'Análisis de Sensibilidad Global',
        'descripcion': 'Identifica variables operacionales más críticas mediante diseño factorial',
        'carpeta': 'Casos/caso5_analisis_sensibilidad',
        'json': 'config_caso5.json',
        'modo': 'sensitivity',
        'emoji': '📈',
        'args_extra': []
    },
    6: {
        'nombre': 'Escalado de Reactores',
        'descripcion': 'Diseña reactor piloto desde condiciones de laboratorio',
        'carpeta': 'Casos/caso6_escalado_reactores',
        'json': 'config_caso6.json',
        'modo': 'scaleup',
        'emoji': '🏭',
        'args_extra': []
    }
}


def verificar_requisitos():
    """Verifica que los requisitos básicos estén cumplidos"""
    if not os.path.exists('main.py'):
        st.error("❌ Error: No se encuentra el archivo main.py")
        st.warning("💡 Asegúrese de ejecutar esta aplicación desde la carpeta raíz del proyecto")
        return False

    if not os.path.exists('Casos'):
        st.error("❌ Error: No se encuentra la carpeta 'Casos'")
        st.warning("💡 Asegúrese de ejecutar esta aplicación desde la carpeta raíz del proyecto")
        return False

    return True


def leer_json(ruta):
    """Lee y retorna el contenido de un archivo JSON"""
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"❌ Error: No se encuentra el archivo {ruta}")
        return None
    except json.JSONDecodeError:
        st.error(f"❌ Error: El archivo {ruta} no es un JSON válido")
        return None
    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        return None


def guardar_json(ruta, datos):
    """Guarda datos en un archivo JSON"""
    try:
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"❌ Error al guardar el archivo: {str(e)}")
        return False


def ejecutar_caso(caso_info):
    """Ejecuta el caso seleccionado llamando a main.py con los argumentos apropiados"""
    carpeta_caso = caso_info['carpeta']
    output_dir = os.path.join(carpeta_caso, 'resultados')

    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)

    # Construir comando para ejecutar main.py
    cmd = [
        sys.executable,
        'main.py',
        '--mode', caso_info['modo'],
        '--output', output_dir
    ]

    # Agregar argumentos adicionales específicos del caso
    cmd.extend(caso_info['args_extra'])

    # Mostrar comando
    st.info(f"🔧 Comando: `{' '.join(cmd)}`")

    # Contenedor para el progreso
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Registrar tiempo de inicio
    tiempo_inicio = time.time()

    try:
        # Actualizar barra de progreso
        progress_bar.progress(25)
        status_text.text("⏳ Ejecutando caso...")

        # Ejecutar el comando
        resultado = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        # Calcular tiempo transcurrido
        tiempo_fin = time.time()
        tiempo_total = tiempo_fin - tiempo_inicio

        # Actualizar barra de progreso
        progress_bar.progress(100)

        # Verificar si la ejecución fue exitosa
        if resultado.returncode == 0:
            status_text.text("✅ ¡Ejecución completada!")
            st.success(f"✅ {caso_info['nombre']} completado exitosamente!")
            st.info(f"⏱️ Tiempo de ejecución: {tiempo_total:.1f} segundos")
            st.success(f"📁 Los resultados se guardaron en:\n`{os.path.abspath(output_dir)}`")

            # Mostrar output si existe
            if resultado.stdout:
                with st.expander("📄 Ver salida del programa"):
                    st.code(resultado.stdout, language="text")

            return True
        else:
            status_text.text("❌ Error durante la ejecución")
            st.error(f"❌ Error durante la ejecución del caso (código: {resultado.returncode})")

            # Mostrar error
            if resultado.stderr:
                with st.expander("⚠️ Ver detalles del error"):
                    st.code(resultado.stderr, language="text")

            st.warning("💡 Sugerencia: Verifique que los archivos de entrada existan y sean válidos")
            return False

    except FileNotFoundError:
        status_text.text("❌ Error: main.py no encontrado")
        st.error("❌ Error: No se encuentra el archivo main.py")
        st.warning("💡 Asegúrese de ejecutar esta aplicación desde la carpeta raíz del proyecto")
        return False
    except Exception as e:
        status_text.text(f"❌ Error inesperado")
        st.error(f"❌ Error inesperado: {str(e)}")
        return False


def main():
    """Función principal de la aplicación Streamlit"""

    # Título principal
    st.title("🧪 Modelado Cinético de Biodiesel")
    st.markdown("### Sistema Unificado Open-Source en Python")
    st.markdown("---")

    # Verificar requisitos
    if not verificar_requisitos():
        st.stop()

    # Sidebar para selección de caso
    with st.sidebar:
        st.header("📋 Selección de Caso")
        st.markdown("---")

        # Selector de caso
        caso_seleccionado = st.selectbox(
            "Seleccione un caso:",
            options=list(CASOS.keys()),
            format_func=lambda x: f"{CASOS[x]['emoji']} {CASOS[x]['nombre']}",
            key="caso_selector"
        )

        st.markdown("---")

        # Mostrar descripción del caso seleccionado
        caso = CASOS[caso_seleccionado]
        st.markdown(f"### {caso['emoji']} {caso['nombre']}")
        st.markdown(f"**Descripción:**")
        st.markdown(caso['descripcion'])

        st.markdown("---")

        # Información adicional
        st.markdown("### 📚 Información")
        st.markdown("""
        **Autores:** J. Salas-García et al.

        **Modo de uso:**
        1. Seleccione un caso
        2. Edite la configuración JSON
        3. Presione 'Ejecutar Caso'
        """)

    # Área principal
    if caso_seleccionado:
        caso = CASOS[caso_seleccionado]

        # Tabs para organizar contenido
        tab1, tab2, tab3 = st.tabs(["⚙️ Configuración", "▶️ Ejecutar", "📊 Resultados"])

        with tab1:
            st.header("⚙️ Configuración del Caso")

            # Construir ruta completa al archivo JSON
            ruta_json = os.path.join(caso['carpeta'], caso['json'])

            # Mostrar ubicación del archivo
            st.info(f"📂 Archivo de configuración: `{os.path.abspath(ruta_json)}`")

            # Leer el contenido del JSON
            datos_json = leer_json(ruta_json)

            if datos_json is not None:
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.subheader("📄 Vista JSON Actual")
                    st.json(datos_json)

                with col2:
                    st.subheader("✏️ Editor de Configuración")

                    # Editor de texto para JSON
                    json_editado = st.text_area(
                        "Edite el JSON aquí:",
                        value=json.dumps(datos_json, indent=2, ensure_ascii=False),
                        height=400,
                        key="json_editor"
                    )

                    # Botón para guardar cambios
                    col_btn1, col_btn2 = st.columns(2)

                    with col_btn1:
                        if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
                            try:
                                # Intentar parsear el JSON editado
                                datos_nuevos = json.loads(json_editado)

                                # Guardar en el archivo
                                if guardar_json(ruta_json, datos_nuevos):
                                    st.success("✅ Configuración guardada exitosamente!")
                                    st.rerun()

                            except json.JSONDecodeError as e:
                                st.error(f"❌ Error: El JSON no es válido\n\n{str(e)}")

                    with col_btn2:
                        if st.button("🔄 Recargar Original", use_container_width=True):
                            st.rerun()

        with tab2:
            st.header("▶️ Ejecutar Caso")

            # Leer configuración actual
            ruta_json = os.path.join(caso['carpeta'], caso['json'])
            datos_json = leer_json(ruta_json)

            if datos_json is not None:
                # Mostrar resumen de la configuración
                st.subheader("📋 Resumen de Configuración Actual")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**🎯 Caso:** {caso['nombre']}")
                    st.markdown(f"**🔧 Modo:** `{caso['modo']}`")
                    st.markdown(f"**📁 Carpeta:** `{caso['carpeta']}`")

                with col2:
                    st.markdown(f"**📄 Archivo JSON:** `{caso['json']}`")
                    if caso['args_extra']:
                        st.markdown(f"**⚡ Args extra:** `{' '.join(caso['args_extra'])}`")

                st.markdown("---")

                # Mostrar configuración en formato compacto
                with st.expander("🔍 Ver configuración completa", expanded=False):
                    st.json(datos_json)

                st.markdown("---")

                # Botón de ejecución
                st.subheader("🚀 Ejecución")

                col_exec1, col_exec2, col_exec3 = st.columns([1, 2, 1])

                with col_exec2:
                    if st.button(
                        f"▶️ Ejecutar {caso['nombre']}",
                        type="primary",
                        use_container_width=True,
                        key="btn_ejecutar"
                    ):
                        st.markdown("---")
                        ejecutar_caso(caso)

        with tab3:
            st.header("📊 Resultados")

            # Directorio de resultados
            carpeta_resultados = os.path.join(caso['carpeta'], 'resultados')

            if os.path.exists(carpeta_resultados):
                st.success(f"📁 Carpeta de resultados: `{os.path.abspath(carpeta_resultados)}`")

                # Listar archivos en la carpeta de resultados
                archivos = sorted(Path(carpeta_resultados).glob('*'))

                if archivos:
                    st.subheader("📄 Archivos generados:")

                    for archivo in archivos:
                        if archivo.is_file():
                            # Información del archivo
                            tamaño = archivo.stat().st_size / 1024  # KB
                            st.markdown(f"- 📄 `{archivo.name}` ({tamaño:.1f} KB)")

                            # Botón para ver contenido si es texto
                            if archivo.suffix in ['.txt', '.log', '.csv', '.json']:
                                with st.expander(f"👁️ Ver contenido de {archivo.name}"):
                                    try:
                                        with open(archivo, 'r', encoding='utf-8') as f:
                                            contenido = f.read()
                                        st.code(contenido, language="text")
                                    except Exception as e:
                                        st.error(f"No se pudo leer el archivo: {str(e)}")
                else:
                    st.info("ℹ️ La carpeta de resultados está vacía. Ejecute el caso primero.")
            else:
                st.warning("⚠️ La carpeta de resultados no existe aún. Ejecute el caso primero.")

                if st.button("📁 Crear carpeta de resultados"):
                    os.makedirs(carpeta_resultados, exist_ok=True)
                    st.success(f"✅ Carpeta creada: `{os.path.abspath(carpeta_resultados)}`")
                    st.rerun()


if __name__ == "__main__":
    main()
