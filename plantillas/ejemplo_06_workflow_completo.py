#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplo 6: Workflow Completo de Análisis
=========================================

Este script ejecuta el flujo completo de análisis:
1. Procesar datos GC-FID
2. Ajustar parámetros cinéticos
3. Optimizar condiciones
4. Generar reportes y gráficas

Autor: Sistema de Modelado de Esterificación
Fecha: 2025-01-15
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_processing.gc_processor import GCProcessor
from models.parameter_fitting import ParameterFitter
from optimization.optimizer import OperationalOptimizer
from models.kinetic_model import KineticModel
from visualization.plotter import ResultsPlotter
from visualization.exporter import ResultsExporter
import pandas as pd

# =============================================================================
# CONFIGURACIÓN GLOBAL
# =============================================================================

# Experimentos
EXPERIMENTOS = [
    {'file': 'data/raw/exp_55C.csv', 'T': 55.0},
    {'file': 'data/raw/exp_65C.csv', 'T': 65.0},
    {'file': 'data/raw/exp_75C.csv', 'T': 75.0},
]

# Condiciones iniciales
C0 = {
    'TG': 0.5,
    'MeOH': 4.5,
    'FAME': 0.0,
    'GL': 0.0
}

# Configuración
CONFIG = {
    'model_type': '1-step',
    'reversible': True,
    'tiempo_reaccion_min': 120,
    'output_dir': f'results/workflow_{datetime.now().strftime("%Y%m%d_%H%M%S")}/'
}

# =============================================================================
# WORKFLOW COMPLETO
# =============================================================================

def paso_1_procesar_gc(experimentos):
    """Paso 1: Procesar datos GC-FID"""
    print("\n" + "="*80)
    print("PASO 1/4: PROCESAMIENTO DE DATOS GC-FID")
    print("="*80)

    processor = GCProcessor()
    resultados_procesados = []

    for i, exp in enumerate(experimentos, 1):
        print(f"\n[{i}/{len(experimentos)}] Procesando: {exp['file']}")

        try:
            data = pd.read_csv(exp['file'])
            results = processor.process_time_series(data, C_TG0=C0['TG'])

            resultados_procesados.append({
                'temperatura': exp['T'],
                'tiempo': results['time'],
                'conversion_%': results['conversion_%'],
                'C_TG': results['C_TG'],
                'C_FAME': results['C_FAME']
            })

            stats = processor.summary_statistics(results)
            print(f"   ✓ Conversión final: {stats['conversion']['final']:.2f}%")

        except FileNotFoundError:
            print(f"   ✗ ERROR: No se encontró {exp['file']}")
            print(f"   ℹ Usa la plantilla: plantillas/plantilla_datos_gc.csv")
            return None

    print(f"\n✓ PASO 1 COMPLETADO: {len(resultados_procesados)} experimentos procesados")
    return resultados_procesados

def paso_2_ajustar_parametros(resultados_procesados):
    """Paso 2: Ajustar parámetros cinéticos"""
    print("\n" + "="*80)
    print("PASO 2/4: AJUSTE DE PARÁMETROS CINÉTICOS")
    print("="*80)

    fitter = ParameterFitter(
        model_type=CONFIG['model_type'],
        reversible=CONFIG['reversible']
    )

    # Agregar experimentos
    for i, res in enumerate(resultados_procesados, 1):
        print(f"\n[{i}/{len(resultados_procesados)}] Agregando experimento T={res['temperatura']}°C")
        fitter.add_experiment(
            t_exp=res['tiempo'],
            y_exp=res['conversion_%'],
            T=res['temperatura'],
            C0=C0,
            exp_id=f'Exp_{int(res["temperatura"])}C'
        )

    # Ajustar
    print(f"\n🔄 Ejecutando ajuste de parámetros...")
    results = fitter.fit(method='leastsq', max_nfev=1000, verbose=True)

    params = results['params']
    metrics = results['metrics']

    print(f"\n📊 PARÁMETROS AJUSTADOS:")
    print(f"   A_forward  = {params['A_forward']:.4e} min⁻¹")
    print(f"   Ea_forward = {params['Ea_forward']:.2f} kJ/mol")
    print(f"   R²         = {metrics['R_squared']:.4f}")

    print(f"\n✓ PASO 2 COMPLETADO")
    return params, metrics, fitter

def paso_3_optimizar(parametros):
    """Paso 3: Optimizar condiciones"""
    print("\n" + "="*80)
    print("PASO 3/4: OPTIMIZACIÓN DE CONDICIONES")
    print("="*80)

    # Crear modelo con parámetros ajustados
    model = KineticModel(
        model_type=CONFIG['model_type'],
        reversible=CONFIG['reversible']
    )
    model.set_parameters(parametros)

    # Optimizar
    optimizer = OperationalOptimizer(
        model=model,
        objective_type='maximize_conversion'
    )

    print(f"\n🔄 Ejecutando optimización...")
    resultado_optimo = optimizer.optimize(
        C0=C0,
        t_reaction=CONFIG['tiempo_reaccion_min'],
        method='differential_evolution',
        maxiter=100,
        verbose=True
    )

    print(f"\n🎯 CONDICIONES ÓPTIMAS:")
    print(f"   Temperatura:  {resultado_optimo['temperature']:.2f} °C")
    print(f"   Agitación:    {resultado_optimo['rpm']:.0f} rpm")
    print(f"   Catalizador:  {resultado_optimo['catalyst_%']:.2f} %")
    print(f"   Conversión:   {resultado_optimo['conversion_%']:.2f} %")

    print(f"\n✓ PASO 3 COMPLETADO")
    return resultado_optimo, optimizer

def paso_4_generar_reportes(output_dir, parametros, metricas, resultado_optimo, fitter):
    """Paso 4: Generar reportes y gráficas"""
    print("\n" + "="*80)
    print("PASO 4/4: GENERACIÓN DE REPORTES")
    print("="*80)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 1. Guardar parámetros
    params_file = output_path / 'parametros_ajustados.json'
    with open(params_file, 'w') as f:
        json.dump({
            'parametros': parametros,
            'metricas_ajuste': metricas,
            'condiciones_optimas': resultado_optimo,
            'configuracion': CONFIG
        }, f, indent=2)
    print(f"\n   ✓ Parámetros guardados: {params_file}")

    # 2. Generar gráficas de ajuste
    print(f"\n   Generando gráficas...")
    fig_ajuste = fitter.plot_fit()
    fig_ajuste.savefig(output_path / 'ajuste_parametros.png', dpi=300, bbox_inches='tight')
    print(f"   ✓ Gráfica de ajuste guardada")

    # 3. Generar reporte Excel
    exporter = ResultsExporter(output_dir=str(output_path))
    excel_file = output_path / 'reporte_completo.xlsx'

    # Crear DataFrame con resultados
    df_params = pd.DataFrame([parametros])
    df_optimo = pd.DataFrame([resultado_optimo])

    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df_params.to_excel(writer, sheet_name='Parámetros', index=False)
        df_optimo.to_excel(writer, sheet_name='Condiciones Óptimas', index=False)

    print(f"   ✓ Excel generado: {excel_file}")

    print(f"\n✓ PASO 4 COMPLETADO")
    return output_path

def main():
    """Función principal"""

    print("="*80)
    print("WORKFLOW COMPLETO DE ANÁLISIS DE ESTERIFICACIÓN")
    print("="*80)
    print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Configuración:")
    print(f"  Modelo: {CONFIG['model_type']}")
    print(f"  Reversible: {CONFIG['reversible']}")
    print(f"  Tiempo de reacción: {CONFIG['tiempo_reaccion_min']} min")

    try:
        # PASO 1: Procesar GC
        resultados_gc = paso_1_procesar_gc(EXPERIMENTOS)
        if resultados_gc is None:
            return

        # PASO 2: Ajustar parámetros
        parametros, metricas, fitter = paso_2_ajustar_parametros(resultados_gc)

        # PASO 3: Optimizar
        resultado_optimo, optimizer = paso_3_optimizar(parametros)

        # PASO 4: Generar reportes
        output_path = paso_4_generar_reportes(
            CONFIG['output_dir'],
            parametros,
            metricas,
            resultado_optimo,
            fitter
        )

        # RESUMEN FINAL
        print("\n" + "="*80)
        print("WORKFLOW COMPLETADO EXITOSAMENTE")
        print("="*80)

        print(f"\n📊 RESUMEN DE RESULTADOS:")
        print(f"   {'─'*60}")
        print(f"   Experimentos procesados: {len(resultados_gc)}")
        print(f"   Calidad del ajuste (R²): {metricas['R_squared']:.4f}")
        print(f"   {'─'*60}")
        print(f"   Temperatura óptima:      {resultado_optimo['temperature']:.1f} °C")
        print(f"   Agitación óptima:        {resultado_optimo['rpm']:.0f} rpm")
        print(f"   Catalizador óptimo:      {resultado_optimo['catalyst_%']:.2f} %")
        print(f"   Conversión predicha:     {resultado_optimo['conversion_%']:.2f} %")
        print(f"   {'─'*60}")

        print(f"\n📁 ARCHIVOS GENERADOS:")
        print(f"   Directorio: {output_path}")
        print(f"   - parametros_ajustados.json")
        print(f"   - ajuste_parametros.png")
        print(f"   - reporte_completo.xlsx")

        print("\n" + "="*80)
        print("Análisis completado. Revisa los archivos en:")
        print(f"  {output_path}")
        print("="*80)

    except Exception as e:
        print(f"\n✗ ERROR durante el workflow: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == '__main__':
    main()
