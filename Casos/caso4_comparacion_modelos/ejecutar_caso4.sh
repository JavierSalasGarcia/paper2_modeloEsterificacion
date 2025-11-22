#!/bin/bash
################################################################################
# CASO 4: Comparación de Modelos Mecanísticos
################################################################################
# Descripción: Compara modelo simplificado (1-paso) con modelo completo
#              (3-pasos) para evaluar trade-off precisión vs complejidad.
#
# Objetivo: Demostrar capacidades analíticas del sistema y guiar selección
#           de modelo según caso de uso
#
# Entrada: Parámetros cinéticos calibrados, condiciones de reacción idénticas
# Salida: Tabla comparativa, gráficas de perfiles, análisis de intermediarios
#
# Autores: J. Salas-García et al.
# Fecha: 2025-11-22
################################################################################

echo "=========================================================================="
echo "CASO 4: Comparación de Modelos Mecanísticos"
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

echo "⚖️  Modelos a comparar:"
echo ""
echo "   📘 Modelo 1-paso (simplificado):"
echo "      TG + 3 MeOH ⇌ 3 FAME + GL"
echo "      - Especies: 4 (TG, MeOH, FAME, GL)"
echo "      - Parámetros: 2 (A, Ea)"
echo "      - Ventajas: Rápido, fácil calibración"
echo ""
echo "   📗 Modelo 3-pasos (mecanístico):"
echo "      TG + MeOH ⇌ DG + FAME"
echo "      DG + MeOH ⇌ MG + FAME"
echo "      MG + MeOH ⇌ GL + FAME"
echo "      - Especies: 6 (TG, DG, MG, MeOH, FAME, GL)"
echo "      - Parámetros: 6 (A1-3, Ea1-3)"
echo "      - Ventajas: Detalle mecanístico, captura intermediarios"
echo ""

echo "🔬 Ejecutando comparación..."
echo ""

# Registrar tiempo de inicio
START_TIME=$(date +%s)

# Ejecutar main.py con modo compare
cd "$ROOT_DIR"
python main.py \
    --mode compare \
    --output "$OUTPUT_DIR" \
    --verbose

# Capturar código de salida
EXIT_CODE=$?

# Registrar tiempo de finalización
END_TIME=$(date +%s)
ELAPSED_TIME=$((END_TIME - START_TIME))

echo ""
echo "=========================================================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ CASO 4 COMPLETADO EXITOSAMENTE"
    echo "⏱️  Tiempo de ejecución: ${ELAPSED_TIME} segundos"
    echo ""
    echo "📊 Resultados generados en: $OUTPUT_DIR"
    echo ""
    echo "Archivos esperados:"
    echo "   - tabla_comparacion.xlsx           (Métricas comparativas)"
    echo "   - perfiles_1paso_vs_3pasos.png     (Superposición de perfiles)"
    echo "   - conversion_1paso_vs_3pasos.png   (Curvas de conversión)"
    echo "   - intermediarios_DG_MG.png         (Solo modelo 3-pasos)"
    echo "   - benchmark_tiempo.json            (Tiempos de cómputo)"
    echo ""
    echo "📈 Resultados esperados:"
    echo "   - Diferencia en conversión final: < 2%"
    echo "   - Tiempo modelo 1-paso:  ~0.5 s"
    echo "   - Tiempo modelo 3-pasos: ~1.5 s (3x más lento)"
    echo ""
    echo "💡 Interpretación:"
    echo "   - Si diferencia < 2%: Modelo 1-paso suficiente para diseño"
    echo "   - Modelo 3-pasos: Útil para análisis de intermediarios (DG, MG)"
    echo "   - Trade-off: Precisión similar, complejidad 3x mayor"
else
    echo "❌ ERROR: La comparación falló con código $EXIT_CODE"
    echo "⏱️  Tiempo antes del error: ${ELAPSED_TIME} segundos"
fi
echo "=========================================================================="
echo ""

# Retornar al directorio del caso
cd "$SCRIPT_DIR"

exit $EXIT_CODE
