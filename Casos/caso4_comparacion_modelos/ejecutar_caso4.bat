@echo off
REM ##############################################################################
REM CASO 4: Comparación de Modelos Mecanísticos
REM ##############################################################################
REM Descripción: Compara modelo simplificado (1-paso) con modelo completo
REM              (3-pasos) para evaluar trade-off precisión vs complejidad.
REM
REM Objetivo: Demostrar capacidades analíticas del sistema y guiar selección
REM           de modelo según caso de uso
REM
REM Entrada: Parámetros cinéticos calibrados, condiciones de reacción idénticas
REM Salida: Tabla comparativa, gráficas de perfiles, análisis de intermediarios
REM
REM Autores: J. Salas-García et al.
REM Fecha: 2025-11-22
REM ##############################################################################

echo ==========================================================================
echo CASO 4: Comparación de Modelos Mecanísticos
echo ==========================================================================
echo.

REM Variables de configuración
set SCRIPT_DIR=%~dp0
set ROOT_DIR=%SCRIPT_DIR%..\..\
set OUTPUT_DIR=%SCRIPT_DIR%resultados

REM Crear directorio de salida si no existe
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo 📂 Configuración:
echo    - Parámetros cinéticos: variables_esterificacion_dataset.json (calibrados^)
echo    - Salida:               %OUTPUT_DIR%
echo.

echo ⚖️  Modelos a comparar:
echo.
echo    📘 Modelo 1-paso (simplificado^):
echo       TG + 3 MeOH ⇌ 3 FAME + GL
echo       - Especies: 4 (TG, MeOH, FAME, GL^)
echo       - Parámetros: 2 (A, Ea^)
echo       - Ventajas: Rápido, fácil calibración
echo.
echo    📗 Modelo 3-pasos (mecanístico^):
echo       TG + MeOH ⇌ DG + FAME
echo       DG + MeOH ⇌ MG + FAME
echo       MG + MeOH ⇌ GL + FAME
echo       - Especies: 6 (TG, DG, MG, MeOH, FAME, GL^)
echo       - Parámetros: 6 (A1-3, Ea1-3^)
echo       - Ventajas: Detalle mecanístico, captura intermediarios
echo.

echo 🔬 Ejecutando comparación...
echo.

REM Registrar tiempo de inicio
set START_TIME=%TIME%

REM Ejecutar main.py con modo compare
cd /d "%ROOT_DIR%"
python main.py --mode compare --output "%OUTPUT_DIR%" --verbose

REM Capturar código de salida
set EXIT_CODE=%ERRORLEVEL%

REM Registrar tiempo de finalización
set END_TIME=%TIME%

echo.
echo ==========================================================================
if %EXIT_CODE% EQU 0 (
    echo ✅ CASO 4 COMPLETADO EXITOSAMENTE
    echo ⏱️  Inicio: %START_TIME%
    echo ⏱️  Fin:    %END_TIME%
    echo.
    echo 📊 Resultados generados en: %OUTPUT_DIR%
    echo.
    echo Archivos esperados:
    echo    - tabla_comparacion.xlsx           (Métricas comparativas^)
    echo    - perfiles_1paso_vs_3pasos.png     (Superposición de perfiles^)
    echo    - conversion_1paso_vs_3pasos.png   (Curvas de conversión^)
    echo    - intermediarios_DG_MG.png         (Solo modelo 3-pasos^)
    echo    - benchmark_tiempo.json            (Tiempos de cómputo^)
    echo.
    echo 📈 Resultados esperados:
    echo    - Diferencia en conversión final: ^< 2%%
    echo    - Tiempo modelo 1-paso:  ~0.5 s
    echo    - Tiempo modelo 3-pasos: ~1.5 s (3x más lento^)
    echo.
    echo 💡 Interpretación:
    echo    - Si diferencia ^< 2%%: Modelo 1-paso suficiente para diseño
    echo    - Modelo 3-pasos: Útil para análisis de intermediarios (DG, MG^)
    echo    - Trade-off: Precisión similar, complejidad 3x mayor
) else (
    echo ❌ ERROR: La comparación falló con código %EXIT_CODE%
    echo ⏱️  Inicio: %START_TIME%
    echo ⏱️  Error:  %END_TIME%
)
echo ==========================================================================
echo.

REM Retornar al directorio del caso
cd /d "%SCRIPT_DIR%"

exit /b %EXIT_CODE%
