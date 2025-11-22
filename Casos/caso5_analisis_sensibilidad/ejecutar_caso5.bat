@echo off
REM ##############################################################################
REM CASO 5: Análisis de Sensibilidad Global
REM ##############################################################################
REM Descripción: Evaluación de influencia de parámetros operacionales mediante
REM              diseño factorial completo 4×4×4×3 = 192 simulaciones.
REM
REM Objetivo: Identificar variables críticas y cuantificar contribución mediante
REM           ANOVA y diagrama de Pareto
REM
REM Entrada: Parámetros cinéticos calibrados, niveles de factores definidos
REM Salida: Tabla ANOVA, gráficas (Pareto, efectos, superficies), análisis físico
REM
REM Autores: J. Salas-García et al.
REM Fecha: 2025-11-22
REM ##############################################################################

echo ==========================================================================
echo CASO 5: Análisis de Sensibilidad Global
echo ==========================================================================
echo.

REM Variables de configuración
set SCRIPT_DIR=%~dp0
set ROOT_DIR=%SCRIPT_DIR%..\..\\
set OUTPUT_DIR=%SCRIPT_DIR%resultados

REM Crear directorio de salida si no existe
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo 📂 Configuración:
echo    - Parámetros cinéticos: variables_esterificacion_dataset.json (calibrados^)
echo    - Salida:               %OUTPUT_DIR%
echo.

echo 🔬 Diseño Factorial Completo:
echo.
echo    Factores y niveles:
echo    - Temperatura:      4 niveles (55, 60, 65, 70°C^)
echo    - Relación Molar:   4 niveles (4, 6, 8, 10:1^)
echo    - Catalizador:      4 niveles (0.5, 1.0, 1.5, 2.0%% másico^)
echo    - Agitación:        3 niveles (300, 500, 700 RPM^)
echo.
echo    Total de simulaciones: 4 × 4 × 4 × 3 = 192
echo    Tiempo estimado: ~3-5 minutos
echo.

echo 📊 Análisis Estadísticos:
echo    - ANOVA (suma de cuadrados, F-estadístico, p-values^)
echo    - Contribución porcentual de cada factor
echo    - Identificación de variables críticas (Top 3^)
echo    - Validación física de resultados
echo.

echo 🎯 Ejecutando análisis de sensibilidad...
echo.

REM Registrar tiempo de inicio
set START_TIME=%TIME%

REM Ejecutar main.py con modo sensitivity
cd /d "%ROOT_DIR%"
python main.py --mode sensitivity --output "%OUTPUT_DIR%" --verbose

REM Capturar código de salida
set EXIT_CODE=%ERRORLEVEL%

REM Registrar tiempo de finalización
set END_TIME=%TIME%

echo.
echo ==========================================================================
if %EXIT_CODE% EQU 0 (
    echo ✅ CASO 5 COMPLETADO EXITOSAMENTE
    echo ⏱️  Inicio: %START_TIME%
    echo ⏱️  Fin:    %END_TIME%
    echo.
    echo 📊 Resultados generados en: %OUTPUT_DIR%
    echo.
    echo Archivos esperados:
    echo    - tabla_anova.xlsx                    (Tabla ANOVA + 192 resultados^)
    echo    - diagrama_pareto.png                 (Contribución de factores^)
    echo    - efectos_principales.png             (4 paneles: T, RM, Cat, RPM^)
    echo    - superficie_respuesta_3D.png         (Superficie T vs RM^)
    echo    - interacciones_T_vs_RM.png           (Interacción T×RM^)
    echo    - sensitivity_analysis_summary.json   (Resumen completo^)
    echo.
    echo 📈 Resultados esperados:
    echo    - Variables críticas identificadas (contribución ^> 10%%^)
    echo    - Temperatura: Factor más significativo (~40-60%% contribución^)
    echo    - Relación Molar: Factor secundario (~20-30%% contribución^)
    echo    - p-values ^< 0.05 para factores significativos
    echo.
    echo 💡 Interpretación:
    echo    - Factores con contribución ^> 10%%: Variables críticas a optimizar
    echo    - Factores con contribución ^< 10%%: Pueden fijarse por economía
    echo    - Resultados validados físicamente (Arrhenius, equilibrio^)
    echo.
    echo 🔍 Validación Física:
    echo    ✓ Temperatura debe aumentar conversión (comportamiento Arrhenius^)
    echo    ✓ Relación molar debe desplazar equilibrio hacia productos
    echo    ✓ Catalizador debe acelerar sin cambiar equilibrio
    echo    ✓ RPM tiene efecto mínimo (modelo pseudo-homogéneo^)
) else (
    echo ❌ ERROR: El análisis falló con código %EXIT_CODE%
    echo ⏱️  Inicio: %START_TIME%
    echo ⏱️  Error:  %END_TIME%
)
echo ==========================================================================
echo.

REM Retornar al directorio del caso
cd /d "%SCRIPT_DIR%"

exit /b %EXIT_CODE%
