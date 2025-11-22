#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplo 2: Ajuste de Parámetros Cinéticos
==========================================

Este script muestra cómo ajustar parámetros cinéticos (A, Ea) a partir
de datos experimentales de múltiples temperaturas.

Autor: Sistema de Modelado de Esterificación
Fecha: 2025-01-15
"""

import sys
from pathlib import Path
import json

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.parameter_fitting import ParameterFitter
import matplotlib.pyplot as plt
import numpy as np

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# Archivos de experimentos (uno por temperatura)
EXPERIMENTOS = [
    {'file': 'data/processed/exp_55C.csv', 'temperatura': 55.0},
    {'file': 'data/processed/exp_65C.csv', 'temperatura': 65.0},
    {'file': 'data/processed/exp_75C.csv', 'temperatura': 75.0},
]

# Modelo cinético
MODEL_TYPE = '1-step'  # '1-step' o '3-step'
REVERSIBLE = True

# Directorio de salida
OUTPUT_DIR = 'results/parameter_fitting/'

# =============================================================================
# AJUSTE DE PARÁMETROS
# =============================================================================

def load_experiment_data(file_path):
    """Cargar datos de experimento desde CSV"""
    import pandas as pd
    df = pd.read_csv(file_path)
    return {
        'time': df['Tiempo_min'].values,
        'conversion_%': df['Conversion_%'].values,
        'C_TG': df['C_TG_mol/L'].values if 'C_TG_mol/L' in df.columns else None
    }

def main():
    """Función principal"""

    print("="*80)
    print("AJUSTE DE PARÁMETROS CINÉTICOS")
    print("="*80)

    # 1. Crear ajustador
    print(f"\n[1/4] Inicializando ajustador de parámetros...")
    print(f"   Modelo: {MODEL_TYPE}")
    print(f"   Reversible: {REVERSIBLE}")

    fitter = ParameterFitter(
        model_type=MODEL_TYPE,
        reversible=REVERSIBLE
    )

    # 2. Cargar experimentos
    print(f"\n[2/4] Cargando experimentos...")

    for i, exp_info in enumerate(EXPERIMENTOS, 1):
        file_path = exp_info['file']
        temperatura = exp_info['temperatura']

        print(f"\n   Experimento {i}: T = {temperatura}°C")
        print(f"   Archivo: {file_path}")

        try:
            exp_data = load_experiment_data(file_path)

            # Condiciones iniciales (ejemplo - ajustar según tus datos)
            C0 = {
                'TG': 0.5,
                'MeOH': 4.5,
                'FAME': 0.0,
                'GL': 0.0
            }

            fitter.add_experiment(
                t_exp=exp_data['time'],
                y_exp=exp_data['conversion_%'],
                T=temperatura,
                C0=C0,
                exp_id=f'Exp_{int(temperatura)}C'
            )

            print(f"   ✓ Cargado: {len(exp_data['time'])} puntos")

        except FileNotFoundError:
            print(f"   ✗ ERROR: No se encontró {file_path}")
            print(f"   ℹ Asegúrate de procesar los datos GC primero")
            return

    # 3. Ajustar parámetros
    print(f"\n[3/4] Ajustando parámetros cinéticos...")
    print(f"   Método: Levenberg-Marquardt")
    print(f"   Esto puede tomar 10-60 segundos...")

    results = fitter.fit(
        method='leastsq',
        max_nfev=1000,
        verbose=True
    )

    # 4. Mostrar resultados
    print(f"\n{'='*80}")
    print("RESULTADOS DEL AJUSTE")
    print('='*80)

    params = results['params']
    metrics = results['metrics']

    print(f"\n📊 PARÁMETROS AJUSTADOS:")
    print(f"   {'─'*60}")
    print(f"   A_forward  = {params['A_forward']:.4e} min⁻¹")
    print(f"   Ea_forward = {params['Ea_forward']:.2f} kJ/mol")

    if REVERSIBLE:
        print(f"   A_reverse  = {params.get('A_reverse', 'N/A'):.4e} min⁻¹")
        print(f"   Ea_reverse = {params.get('Ea_reverse', 'N/A'):.2f} kJ/mol")

    print(f"   {'─'*60}")

    print(f"\n📈 MÉTRICAS DE AJUSTE:")
    print(f"   {'─'*60}")
    print(f"   R²        = {metrics['R_squared']:.4f}")
    print(f"   RMSE      = {metrics['RMSE']:.4f}")
    print(f"   MAE       = {metrics['MAE']:.4f}")
    print(f"   {'─'*60}")

    if 'confidence_intervals' in results:
        print(f"\n📊 INTERVALOS DE CONFIANZA (95%):")
        ci = results['confidence_intervals']
        for param_name, (lower, upper) in ci.items():
            print(f"   {param_name:12s}: [{lower:.4e}, {upper:.4e}]")

    # 5. Exportar resultados
    print(f"\n[4/4] Exportando resultados...")

    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    # Guardar parámetros en JSON
    params_file = output_path / 'parametros_ajustados.json'
    with open(params_file, 'w') as f:
        json.dump({
            'modelo': MODEL_TYPE,
            'reversible': REVERSIBLE,
            'parametros': params,
            'metricas': metrics,
            'intervalos_confianza': results.get('confidence_intervals', {})
        }, f, indent=2)

    print(f"   ✓ Parámetros guardados en: {params_file}")

    # 6. Generar gráficas de ajuste
    print(f"\n[5/5] Generando gráficas de ajuste...")

    fig = fitter.plot_fit()

    fig_file = output_path / 'ajuste_parametros.png'
    fig.savefig(fig_file, dpi=300, bbox_inches='tight')
    print(f"   ✓ Gráfica guardada en: {fig_file}")

    plt.show()

    print("\n" + "="*80)
    print("AJUSTE COMPLETADO EXITOSAMENTE")
    print("="*80)
    print(f"\nArchivos generados:")
    print(f"  - Parámetros: {params_file}")
    print(f"  - Gráfica: {fig_file}")
    print(f"\nCalidad del ajuste: R² = {metrics['R_squared']:.4f}")
    print("="*80)

if __name__ == '__main__':
    main()
