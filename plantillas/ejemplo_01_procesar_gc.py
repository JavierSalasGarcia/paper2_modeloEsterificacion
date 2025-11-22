#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplo 1: Procesamiento de Datos GC-FID
==========================================

Este script muestra cómo procesar datos crudos de cromatografía GC-FID
para obtener concentraciones, conversiones y rendimientos.

Autor: Sistema de Modelado de Esterificación
Fecha: 2025-01-15
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_processing.gc_processor import GCProcessor
import matplotlib.pyplot as plt
import pandas as pd

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# Rutas de archivos
INPUT_FILE = 'data/raw/experimento_01.csv'  # Modificar con tu archivo
OUTPUT_DIR = 'data/processed/'
FIGURES_DIR = 'results/figures/'

# Parámetros experimentales
C_TG_INICIAL = 0.5  # mol/L - Concentración inicial de triglicéridos
TEMPERATURA = 65.0  # °C
TIEMPO_REACCION = 120  # minutos

# Estándar interno
CONCENTRACION_IS = 2.0  # mg/mL
MW_IS = 226.4  # g/mol

# =============================================================================
# PROCESAMIENTO
# =============================================================================

def main():
    """Función principal"""

    print("="*80)
    print("PROCESAMIENTO DE DATOS GC-FID")
    print("="*80)

    # 1. Crear procesador GC
    print("\n[1/5] Inicializando procesador GC-FID...")
    processor = GCProcessor(
        is_concentration=CONCENTRACION_IS,
        is_mw=MW_IS
    )

    # 2. Cargar datos crudos
    print(f"\n[2/5] Cargando datos desde: {INPUT_FILE}")
    try:
        data = pd.read_csv(INPUT_FILE)
        print(f"   ✓ Datos cargados: {len(data)} filas")
        print(f"   ✓ Columnas: {list(data.columns)}")
    except FileNotFoundError:
        print(f"   ✗ ERROR: No se encontró el archivo {INPUT_FILE}")
        print(f"   ℹ Usa la plantilla: plantillas/plantilla_datos_gc.csv")
        return

    # 3. Procesar serie temporal
    print(f"\n[3/5] Procesando serie temporal...")
    results = processor.process_time_series(data, C_TG0=C_TG_INICIAL)

    print(f"   ✓ Procesado completo")
    print(f"   ✓ Puntos temporales: {len(results['time'])}")

    # 4. Calcular estadísticas
    print(f"\n[4/5] Calculando estadísticas...")
    stats = processor.summary_statistics(results)

    print(f"\n   RESULTADOS:")
    print(f"   {'-'*60}")
    print(f"   Conversión inicial:  {stats['conversion']['initial']:6.2f} %")
    print(f"   Conversión final:    {stats['conversion']['final']:6.2f} %")
    print(f"   Máxima conversión:   {stats['conversion']['max']:6.2f} %")
    print(f"   {'-'*60}")
    print(f"   Rendimiento FAME:    {stats['FAME_yield']['final']:6.2f} %")
    print(f"   Selectividad:        {stats['selectivity']['final']:6.2f} %")
    print(f"   {'-'*60}")

    # 5. Exportar resultados
    print(f"\n[5/5] Exportando resultados...")

    # Crear DataFrame con resultados
    results_df = pd.DataFrame({
        'Tiempo_min': results['time'],
        'C_TG_mol/L': results['C_TG'],
        'C_MeOH_mol/L': results['C_MeOH'],
        'C_FAME_mol/L': results['C_FAME'],
        'C_GL_mol/L': results['C_GL'],
        'Conversion_%': results['conversion_%'],
        'Rendimiento_FAME_%': results['FAME_yield_%']
    })

    # Guardar CSV
    output_file = Path(OUTPUT_DIR) / 'resultados_gc_procesados.csv'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_file, index=False)
    print(f"   ✓ CSV guardado en: {output_file}")

    # 6. Generar gráficas
    print(f"\n[6/6] Generando gráficas...")

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Gráfica 1: Conversión vs Tiempo
    axes[0, 0].plot(results['time'], results['conversion_%'], 'o-', linewidth=2)
    axes[0, 0].set_xlabel('Tiempo (min)')
    axes[0, 0].set_ylabel('Conversión (%)')
    axes[0, 0].set_title('Conversión de Triglicéridos')
    axes[0, 0].grid(True)

    # Gráfica 2: Concentraciones
    axes[0, 1].plot(results['time'], results['C_TG'], 'o-', label='TG')
    axes[0, 1].plot(results['time'], results['C_FAME'], 's-', label='FAME')
    axes[0, 1].plot(results['time'], results['C_GL'], '^-', label='GL')
    axes[0, 1].set_xlabel('Tiempo (min)')
    axes[0, 1].set_ylabel('Concentración (mol/L)')
    axes[0, 1].set_title('Perfiles de Concentración')
    axes[0, 1].legend()
    axes[0, 1].grid(True)

    # Gráfica 3: Rendimiento FAME
    axes[1, 0].plot(results['time'], results['FAME_yield_%'], 'o-',
                    color='green', linewidth=2)
    axes[1, 0].set_xlabel('Tiempo (min)')
    axes[1, 0].set_ylabel('Rendimiento FAME (%)')
    axes[1, 0].set_title('Rendimiento de FAME')
    axes[1, 0].grid(True)

    # Gráfica 4: Balance de masa
    axes[1, 1].plot(results['time'], results['C_TG'], 'o-', label='TG')
    axes[1, 1].plot(results['time'], results['C_MeOH'], 's-', label='MeOH')
    axes[1, 1].set_xlabel('Tiempo (min)')
    axes[1, 1].set_ylabel('Concentración (mol/L)')
    axes[1, 1].set_title('Reactivos')
    axes[1, 1].legend()
    axes[1, 1].grid(True)

    plt.tight_layout()

    # Guardar figura
    fig_file = Path(FIGURES_DIR) / 'procesamiento_gc.png'
    fig_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(fig_file, dpi=300, bbox_inches='tight')
    print(f"   ✓ Gráfica guardada en: {fig_file}")

    plt.show()

    print("\n" + "="*80)
    print("PROCESAMIENTO COMPLETADO EXITOSAMENTE")
    print("="*80)
    print(f"\nArchivos generados:")
    print(f"  - Datos procesados: {output_file}")
    print(f"  - Gráfica: {fig_file}")
    print(f"\nConversión final alcanzada: {stats['conversion']['final']:.2f}%")
    print("="*80)

if __name__ == '__main__':
    main()
