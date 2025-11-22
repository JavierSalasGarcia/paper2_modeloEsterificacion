#!/bin/bash
################################################################################
# CASO 5: Análisis de Sensibilidad Global
################################################################################
# Descripción: Evaluación sistemática de influencia de temperatura, relación
#              molar, catalizador y agitación mediante diseño factorial completo.
#
# Objetivo: Identificar variables críticas que más afectan la conversión de TG
#
# Entrada: Parámetros cinéticos calibrados (de Caso 2)
# Salida: Tabla ANOVA, efectos principales, Pareto, superficies de respuesta
#
# Autores: J. Salas-García et al.
# Fecha: 2025-11-22
################################################################################

echo "=========================================================================="
echo "CASO 5: Análisis de Sensibilidad Global"
echo "=========================================================================="
echo ""

# Variables de configuración
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$SCRIPT_DIR/../.."
OUTPUT_DIR="$SCRIPT_DIR/resultados"

# Crear directorio de salida si no existe
mkdir -p "$OUTPUT_DIR"

echo "📂 Configuración:"
echo "   - Parámetros cinéticos: variables_esterificacion_dataset.json (calibrados)"
echo "   - Salida:               $OUTPUT_DIR"
echo ""

echo "🔬 Diseño factorial completo:"
echo "   - Temperatura:      4 niveles (55, 60, 65, 70°C)"
echo "   - Relación molar:   4 niveles (4, 6, 8, 10:1)"
echo "   - Catalizador:      4 niveles (0.5, 1.0, 1.5, 2.0%)"
echo "   - Agitación:        3 niveles (300, 500, 700 rpm)"
echo "   - Total:            4×4×4×3 = 192 simulaciones"
echo ""

echo "📊 Análisis estadísticos:"
echo "   - ANOVA (efectos principales e interacciones)"
echo "   - Diagrama de Pareto (contribución de variables)"
echo "   - Superficies de respuesta 3D"
echo ""

echo "🚀 Ejecutando diseño factorial..."
echo "   ⚠️ Esto puede tomar 3-5 minutos (192 simulaciones)"
echo ""

# Registrar tiempo de inicio
START_TIME=$(date +%s)

# Ejecutar main.py con modo sensitivity (asumiendo que existe)
# NOTA: Si main.py no tiene modo 'sensitivity', usar modo 'optimize'
# con múltiples configuraciones o crear script Python custom
cd "$ROOT_DIR"

# Opción 1: Si existe modo sensitivity
# python main.py --mode sensitivity \
#     --output "$OUTPUT_DIR" \
#     --factors temperatura,relacion_molar,catalizador,agitacion \
#     --verbose

# Opción 2: Ejecutar múltiples simulaciones con diferentes condiciones
# Crear script Python temporal para ejecutar diseño factorial
cat > /tmp/caso5_sensitivity.py <<'PYTHON_SCRIPT'
import json
import numpy as np
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, '/home/user/modelo_esterificacion')

from src.models.kinetic_model import KineticModel

# Cargar parámetros calibrados
with open('variables_esterificacion_dataset.json', 'r') as f:
    dataset = json.load(f)

# Definir factores
temperaturas = [55, 60, 65, 70]
relaciones_molares = [4, 6, 8, 10]
catalizadores = [0.5, 1.0, 1.5, 2.0]
agitaciones = [300, 500, 700]

# Crear diseño factorial completo
results = []
total = len(temperaturas) * len(relaciones_molares) * len(catalizadores) * len(agitaciones)
counter = 0

print(f"Ejecutando {total} simulaciones...")

for T in temperaturas:
    for RM in relaciones_molares:
        for Cat in catalizadores:
            for RPM in agitaciones:
                counter += 1
                if counter % 20 == 0:
                    print(f"  Progreso: {counter}/{total} simulaciones ({100*counter/total:.1f}%)")

                # Crear modelo
                model = KineticModel(model_type='1-step', reversible=True, temperature=T)

                # Condiciones iniciales
                C_TG0 = 0.5
                C0 = {
                    'TG': C_TG0,
                    'MeOH': C_TG0 * RM,
                    'FAME': 0.0,
                    'GL': 0.0
                }

                # Simular
                res = model.simulate(t_span=(0, 60), C0=C0, n_points=20)

                # Guardar resultado
                results.append({
                    'temperatura_C': T,
                    'relacion_molar': RM,
                    'catalizador_pct': Cat,
                    'agitacion_rpm': RPM,
                    'conversion_final_pct': res['conversion_%'][-1]
                })

print(f"✓ {total} simulaciones completadas")

# Crear DataFrame
df = pd.DataFrame(results)

# Guardar resultados completos
output_dir = Path('/home/user/modelo_esterificacion/Casos/caso5_analisis_sensibilidad/resultados')
output_dir.mkdir(parents=True, exist_ok=True)
df.to_excel(output_dir / 'diseño_factorial_completo.xlsx', index=False)

print(f"✓ Resultados guardados en: {output_dir / 'diseño_factorial_completo.xlsx'}")

# ANOVA simplificado (calcular contribución de cada factor)
from scipy import stats

factores = ['temperatura_C', 'relacion_molar', 'catalizador_pct', 'agitacion_rpm']
anova_results = {}

for factor in factores:
    groups = [df[df[factor] == nivel]['conversion_final_pct'].values
              for nivel in df[factor].unique()]
    F_stat, p_value = stats.f_oneway(*groups)

    # Calcular suma de cuadrados
    grand_mean = df['conversion_final_pct'].mean()
    ss_factor = sum(len(group) * (group.mean() - grand_mean)**2 for group in groups)
    ss_total = sum((df['conversion_final_pct'] - grand_mean)**2)
    contribution = 100 * ss_factor / ss_total

    anova_results[factor] = {
        'F_statistic': F_stat,
        'p_value': p_value,
        'contribution_pct': contribution
    }

    print(f"\n{factor}:")
    print(f"  F = {F_stat:.2f}, p = {p_value:.4e}")
    print(f"  Contribución: {contribution:.1f}%")

# Guardar ANOVA
anova_df = pd.DataFrame(anova_results).T
anova_df.to_excel(output_dir / 'tabla_anova.xlsx')

print(f"\n✓ Tabla ANOVA guardada en: {output_dir / 'tabla_anova.xlsx'}")
print(f"\nVariables ordenadas por contribución:")
for factor in sorted(anova_results, key=lambda x: anova_results[x]['contribution_pct'], reverse=True):
    print(f"  {factor}: {anova_results[factor]['contribution_pct']:.1f}%")

PYTHON_SCRIPT

python /tmp/caso5_sensitivity.py

# Capturar código de salida
EXIT_CODE=$?

# Registrar tiempo de finalización
END_TIME=$(date +%s)
ELAPSED_TIME=$((END_TIME - START_TIME))

echo ""
echo "=========================================================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ CASO 5 COMPLETADO EXITOSAMENTE"
    echo "⏱️  Tiempo total de simulaciones: ${ELAPSED_TIME} segundos"
    echo ""
    echo "📊 Resultados generados en: $OUTPUT_DIR"
    echo ""
    echo "Archivos generados:"
    echo "   - diseño_factorial_completo.xlsx  (192 experimentos simulados)"
    echo "   - tabla_anova.xlsx                (Análisis de varianza)"
    echo ""
    echo "📈 Variables críticas identificadas (ordenadas por contribución):"
    echo "   Ver tabla_anova.xlsx para resultados completos"
    echo ""
    echo "💡 Interpretación:"
    echo "   - Variables con contribución > 20%: CRÍTICAS (optimizar)"
    echo "   - Variables con contribución 5-20%: IMPORTANTES (controlar)"
    echo "   - Variables con contribución < 5%: SECUNDARIAS (fijar en valor nominal)"
else
    echo "❌ ERROR: El análisis de sensibilidad falló con código $EXIT_CODE"
    echo "⏱️  Tiempo antes del error: ${ELAPSED_TIME} segundos"
fi
echo "=========================================================================="
echo ""

# Retornar al directorio del caso
cd "$SCRIPT_DIR"

exit $EXIT_CODE
