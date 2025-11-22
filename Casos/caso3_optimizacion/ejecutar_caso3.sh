#!/bin/bash
################################################################################
# CASO 3: Optimización Multi-Objetivo con Lógica Difusa
################################################################################
# Descripción: Optimiza condiciones operacionales (T, relación molar,
#              catalizador, agitación) balanceando conversión vs costos
#              energéticos y de catalizador usando lógica difusa.
#
# Objetivo: Demostrar optimización multi-objetivo con pesos adaptativos
#           vía lógica difusa. Identifica dos regímenes operacionales:
#           - RÁPIDO (t<72 min): Alta agitación/catalizador
#           - ECONÓMICO (t>=72 min): Baja agitación/catalizador
#
# Entrada: Parámetros cinéticos calibrados (del Caso 2)
# Salida: Condiciones óptimas por tiempo, gráficas comparativas
#
# Autores: J. Salas-García et al.
# Fecha: 2025-11-22
################################################################################

echo "=========================================================================="
echo "CASO 3: Optimización Multi-Objetivo"
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

echo "🎯 Variables de optimización:"
echo "   - Temperatura:      50-80°C"
echo "   - Relación molar:   3:1 a 15:1"
echo "   - Catalizador:      0.5-5.0% CaO"
echo "   - Agitación:        200-800 rpm"
echo ""

echo "📊 Función objetivo:"
echo "   - MULTI-OBJETIVO: Balance conversión vs costos operacionales"
echo "   - Maximizar conversión, minimizar energía y catalizador"
echo "   - Pesos dinámicos vía Lógica Difusa (3 regímenes)"
echo ""

echo "🧮 Sistema de optimización:"
echo "   - Algoritmo: Differential Evolution (global optimizer)"
echo "   - Lógica Difusa: 3 regímenes (CORTO, MEDIO, LARGO)"
echo "   - Tiempo configurable en main.py (actualmente: 90 min)"
echo ""

echo "🔬 Ejecutando optimización..."
echo ""

# Registrar tiempo de inicio
START_TIME=$(date +%s)

# Ejecutar main.py con modo optimize
cd "$ROOT_DIR"
python main.py \
    --mode optimize \
    --output "$OUTPUT_DIR" \
    --model-type 1-step \
    --verbose

# Capturar código de salida
EXIT_CODE=$?

# Registrar tiempo de finalización
END_TIME=$(date +%s)
ELAPSED_TIME=$((END_TIME - START_TIME))

echo ""
echo "=========================================================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ CASO 3 COMPLETADO EXITOSAMENTE"
    echo "⏱️  Tiempo de optimización: ${ELAPSED_TIME} segundos"
    echo ""
    echo "📊 Resultados generados en: $OUTPUT_DIR"
    echo ""
    echo "Archivos esperados:"
    echo "   - optimization_summary.json          (Resumen comparativo multi-tiempo)"
    echo "   - optimal_conditions_XXmin.json      (Condiciones óptimas por tiempo)"
    echo "   - optimizacion_multi_tiempo.png      (Gráfica comparativa)"
    echo "   - convergencia_optimizacion.png      (Evolución del algoritmo)"
    echo ""
    echo "🎯 Regímenes operacionales esperados:"
    echo ""
    echo "   RÉGIMEN RÁPIDO (t < 72 min):"
    echo "   - Temperatura:    65°C (máxima permitida)"
    echo "   - RPM:            ~596 (alta agitación)"
    echo "   - Catalizador:    ~0.82% (moderado-alto)"
    echo "   - Conversión:     85-89%"
    echo "   - Estrategia:     Maximizar velocidad de reacción"
    echo ""
    echo "   RÉGIMEN ECONÓMICO (t >= 72 min):"
    echo "   - Temperatura:    65°C (alta conversión requiere T alta)"
    echo "   - RPM:            200 (mínimo - ahorro energético)"
    echo "   - Catalizador:    0.50% (mínimo - ahorro costo)"
    echo "   - Conversión:     89-96%"
    echo "   - Estrategia:     Balance conversión-costo"
    echo ""
    echo "⚡ Ventajas sobre software comercial:"
    echo "   - Aspen Plus:         15-20 pasos + configuración compleja"
    echo "   - Sistema propuesto:  1 comando + lógica difusa automática"
    echo "   - Tiempo:             ~5-10 segundos vs varios minutos"
else
    echo "❌ ERROR: La optimización falló con código $EXIT_CODE"
    echo "⏱️  Tiempo antes del error: ${ELAPSED_TIME} segundos"
fi
echo "=========================================================================="
echo ""

# Retornar al directorio del caso
cd "$SCRIPT_DIR"

exit $EXIT_CODE
