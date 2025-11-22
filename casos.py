#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Asistente Interactivo para Casos de Modelado de Biodiesel
Simplifica la ejecución de casos para usuarios no técnicos en programación

Autores: J. Salas-García et al.
Fecha: 2025-11-22
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

# Intentar importar colorama para colores en terminal
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORES_DISPONIBLES = True
except ImportError:
    COLORES_DISPONIBLES = False
    # Fallback sin colores si colorama no está instalado
    class Fore:
        GREEN = RED = YELLOW = CYAN = MAGENTA = BLUE = WHITE = RESET = ''
    class Style:
        BRIGHT = RESET_ALL = ''

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


def limpiar_pantalla():
    """Limpia la pantalla de la terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


def mostrar_banner():
    """Muestra el banner inicial del asistente"""
    print()
    print(Fore.CYAN + Style.BRIGHT + "=" * 70)
    print(Fore.CYAN + Style.BRIGHT + "   ASISTENTE DE CASOS - MODELADO CINÉTICO DE BIODIESEL")
    print(Fore.CYAN + Style.BRIGHT + "   Sistema Unificado Open-Source en Python")
    print(Fore.CYAN + Style.BRIGHT + "=" * 70)
    print()


def mostrar_menu():
    """Muestra el menú principal con los 6 casos disponibles"""
    print(Fore.YELLOW + Style.BRIGHT + "Seleccione un caso para ejecutar:\n")

    for num, caso in CASOS.items():
        print(f"{Fore.GREEN}{caso['emoji']}  {num}. {Style.BRIGHT}{caso['nombre']}")
        print(f"      {Fore.WHITE}{caso['descripcion']}\n")

    print(f"{Fore.RED}❌ 0. Salir del asistente\n")
    print(Fore.CYAN + "-" * 70)


def leer_json(ruta):
    """
    Lee y retorna el contenido de un archivo JSON

    Args:
        ruta (str): Ruta al archivo JSON

    Returns:
        dict: Contenido del JSON o None si hay error
    """
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(Fore.RED + f"\n❌ Error: No se encuentra el archivo {ruta}")
        return None
    except json.JSONDecodeError:
        print(Fore.RED + f"\n❌ Error: El archivo {ruta} no es un JSON válido")
        return None
    except Exception as e:
        print(Fore.RED + f"\n❌ Error inesperado: {str(e)}")
        return None


def mostrar_json_formateado(datos):
    """
    Muestra el contenido del JSON de manera legible y formateada

    Args:
        datos (dict): Datos del JSON a mostrar
    """
    print(Fore.CYAN + Style.BRIGHT + "\n📄 Contenido del archivo de configuración:")
    print(Fore.CYAN + "─" * 70)
    print(Fore.WHITE + json.dumps(datos, indent=2, ensure_ascii=False))
    print(Fore.CYAN + "─" * 70 + "\n")


def obtener_respuesta_si_no(pregunta):
    """
    Solicita una respuesta sí/no del usuario

    Args:
        pregunta (str): Pregunta a mostrar al usuario

    Returns:
        bool: True si la respuesta es 's', False si es 'n'
    """
    while True:
        respuesta = input(Fore.YELLOW + pregunta + " (s/n): ").lower().strip()
        if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            return True
        elif respuesta in ['n', 'no']:
            return False
        else:
            print(Fore.RED + "❌ Por favor responda 's' para sí o 'n' para no")


def ejecutar_caso(caso_info):
    """
    Ejecuta el caso seleccionado llamando a main.py con los argumentos apropiados

    Args:
        caso_info (dict): Información del caso a ejecutar

    Returns:
        bool: True si la ejecución fue exitosa, False en caso contrario
    """
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

    print(Fore.CYAN + Style.BRIGHT + f"\n⏳ Ejecutando {caso_info['nombre']}...")
    print(Fore.CYAN + f"   Comando: {' '.join(cmd)}\n")
    print(Fore.YELLOW + "─" * 70)

    # Registrar tiempo de inicio
    tiempo_inicio = time.time()

    try:
        # Ejecutar el comando
        resultado = subprocess.run(
            cmd,
            capture_output=False,  # Mostrar output en tiempo real
            text=True,
            check=False
        )

        # Calcular tiempo transcurrido
        tiempo_fin = time.time()
        tiempo_total = tiempo_fin - tiempo_inicio

        print(Fore.YELLOW + "─" * 70)

        # Verificar si la ejecución fue exitosa
        if resultado.returncode == 0:
            print(Fore.GREEN + Style.BRIGHT + f"\n✅ {caso_info['nombre']} completado exitosamente!")
            print(Fore.GREEN + f"⏱️  Tiempo de ejecución: {tiempo_total:.1f} segundos")
            print(Fore.GREEN + f"\n📁 Los resultados se guardaron en:")
            print(Fore.WHITE + f"   {os.path.abspath(output_dir)}")
            print()
            return True
        else:
            print(Fore.RED + Style.BRIGHT + f"\n❌ Error durante la ejecución del caso")
            print(Fore.RED + f"   Código de salida: {resultado.returncode}")
            print(Fore.YELLOW + "\n💡 Sugerencia: Verifique que los archivos de entrada existan y sean válidos")
            print()
            return False

    except FileNotFoundError:
        print(Fore.RED + Style.BRIGHT + "\n❌ Error: No se encuentra el archivo main.py")
        print(Fore.YELLOW + "💡 Asegúrese de ejecutar este asistente desde la carpeta raíz del proyecto")
        return False
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"\n❌ Error inesperado: {str(e)}")
        return False


def procesar_caso(caso_info):
    """
    Procesa el caso seleccionado: muestra JSON, pregunta si ejecutar o editar

    Args:
        caso_info (dict): Información del caso seleccionado
    """
    print(Fore.CYAN + Style.BRIGHT + f"\n{caso_info['emoji']}  {caso_info['nombre'].upper()}")
    print(Fore.CYAN + "=" * 70)
    print(Fore.WHITE + caso_info['descripcion'])
    print()

    # Construir ruta completa al archivo JSON
    ruta_json = os.path.join(caso_info['carpeta'], caso_info['json'])

    # Mostrar ubicación del archivo de configuración
    print(Fore.MAGENTA + Style.BRIGHT + "📂 Archivo de configuración:")
    print(Fore.WHITE + f"   {os.path.abspath(ruta_json)}\n")

    # Leer y mostrar el contenido del JSON
    datos_json = leer_json(ruta_json)
    if datos_json is None:
        print(Fore.RED + "\n❌ No se puede continuar sin el archivo de configuración")
        input(Fore.YELLOW + "\nPresione Enter para volver al menú...")
        return

    mostrar_json_formateado(datos_json)

    # Preguntar si desea ejecutar el caso
    if obtener_respuesta_si_no("¿Desea ejecutar este caso ahora?"):
        ejecutar_caso(caso_info)
    else:
        # Preguntar si desea editar el archivo primero
        if obtener_respuesta_si_no("\n¿Desea editar el archivo de configuración antes de ejecutar?"):
            print(Fore.CYAN + Style.BRIGHT + "\n📝 Para editar el archivo de configuración:")
            print(Fore.WHITE + f"   1. Abra el archivo: {Fore.YELLOW}{os.path.abspath(ruta_json)}")
            print(Fore.WHITE + f"   2. Realice los cambios necesarios")
            print(Fore.WHITE + f"   3. Guarde el archivo")
            print(Fore.WHITE + f"   4. Presione Enter en esta ventana para continuar\n")
            input(Fore.YELLOW + "Presione Enter cuando haya terminado de editar...")

            # Preguntar nuevamente si desea ejecutar después de editar
            if obtener_respuesta_si_no("\n¿Desea ejecutar el caso ahora?"):
                ejecutar_caso(caso_info)
            else:
                print(Fore.CYAN + "\nOperación cancelada. Volviendo al menú principal...")
        else:
            print(Fore.CYAN + "\nOperación cancelada. Volviendo al menú principal...")


def verificar_requisitos():
    """
    Verifica que los requisitos básicos estén cumplidos

    Returns:
        bool: True si todo está OK, False si falta algo
    """
    # Verificar que main.py existe
    if not os.path.exists('main.py'):
        print(Fore.RED + Style.BRIGHT + "\n❌ Error: No se encuentra el archivo main.py")
        print(Fore.YELLOW + "💡 Asegúrese de ejecutar este asistente desde la carpeta raíz del proyecto\n")
        return False

    # Verificar que la carpeta Casos existe
    if not os.path.exists('Casos'):
        print(Fore.RED + Style.BRIGHT + "\n❌ Error: No se encuentra la carpeta 'Casos'")
        print(Fore.YELLOW + "💡 Asegúrese de ejecutar este asistente desde la carpeta raíz del proyecto\n")
        return False

    # Advertencia si colorama no está instalado
    if not COLORES_DISPONIBLES:
        print(Fore.YELLOW + "\n⚠️  Nota: Para mejor visualización, instale colorama:")
        print(Fore.WHITE + "   pip install colorama\n")

    return True


def main():
    """Función principal del asistente"""
    limpiar_pantalla()
    mostrar_banner()

    # Verificar requisitos
    if not verificar_requisitos():
        sys.exit(1)

    # Mostrar menú
    mostrar_menu()

    # Loop principal
    while True:
        try:
            seleccion = input(Fore.YELLOW + Style.BRIGHT + "Ingrese el número del caso (0-6): ").strip()

            # Validar que sea un número
            try:
                seleccion = int(seleccion)
            except ValueError:
                print(Fore.RED + "❌ Por favor ingrese un número válido entre 0 y 6\n")
                continue

            # Opción 0: Salir
            if seleccion == 0:
                print(Fore.CYAN + Style.BRIGHT + "\n¡Gracias por usar el asistente de casos!")
                print(Fore.CYAN + "Hasta luego. 👋\n")
                sys.exit(0)

            # Validar que el caso existe
            if seleccion not in CASOS:
                print(Fore.RED + f"❌ Opción inválida. Por favor seleccione un número entre 0 y 6\n")
                continue

            # Procesar el caso seleccionado
            caso = CASOS[seleccion]
            procesar_caso(caso)

            # Después de ejecutar (o cancelar), salir del programa
            print(Fore.CYAN + "\n" + "=" * 70)
            print(Fore.CYAN + Style.BRIGHT + "Fin de la sesión del asistente")
            print(Fore.CYAN + "=" * 70 + "\n")
            break

        except KeyboardInterrupt:
            print(Fore.CYAN + Style.BRIGHT + "\n\n¡Operación cancelada por el usuario!")
            print(Fore.CYAN + "Hasta luego. 👋\n")
            sys.exit(0)
        except Exception as e:
            print(Fore.RED + Style.BRIGHT + f"\n❌ Error inesperado: {str(e)}")
            print(Fore.YELLOW + "Por favor intente nuevamente o contacte al administrador\n")
            continue


if __name__ == "__main__":
    main()
