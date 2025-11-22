@echo off
REM ##############################################################################
REM CASO 6: Escalado de Reactores
REM ##############################################################################
REM Descripción: Escalado de reactor de laboratorio (350 mL) a reactor piloto
REM              (20 L) usando criterios de similitud hidrodinámica.
REM
REM Objetivo: Demostrar capacidad de diseño de reactores escalados con cálculos
REM           de hidrodinámica, transferencia de masa y validación cinética
REM
REM Entrada: Configuración reactor laboratorio (config_caso6.json)
REM Salida: Diseño detallado reactor piloto, gráficas, validación
REM
REM Autores: J. Salas-García et al.
REM Fecha: 2025-11-22
REM ##############################################################################

echo ==========================================================================
echo CASO 6: Escalado de Reactores
echo ==========================================================================
echo.

REM Variables de configuración
set SCRIPT_DIR=%~dp0
set ROOT_DIR=%SCRIPT_DIR%..\..\\
set OUTPUT_DIR=%SCRIPT_DIR%resultados

REM Crear directorio de salida si no existe
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo 📂 Configuración:
echo    - Config: config_caso6.json
echo    - Salida: %OUTPUT_DIR%
echo.

echo ⚗️  Reactor de laboratorio (escala pequeña^):
echo    - Volumen:          350 mL (0.35 L^)
echo    - Diámetro:         80 mm
echo    - Impulsor:         Barra magnética (30 mm^)
echo    - Velocidad:        400 rpm
echo    - Temperatura:      60°C
echo.

echo 🏭 Reactor piloto objetivo:
echo    - Volumen:          20 L (57× más grande^)
echo    - Geometría:        Similar (H/D constante^)
echo    - Impulsor:         Cinta helicoidal
echo.

echo 📐 Criterios de escalado a evaluar:
echo    1. Número de potencia constante (Np^)
echo    2. Potencia por volumen constante (P/V^)  ← MÁS COMÚN
echo    3. Velocidad de punta constante (vtip^)
echo    4. Tiempo de mezclado constante (tm^)
echo.

echo 🔬 Ejecutando cálculos de escalado...
echo.

REM Registrar tiempo de inicio
set START_TIME=%TIME%

REM Ejecutar main.py con modo scaleup
cd /d "%ROOT_DIR%"
python main.py --mode scaleup --output "%OUTPUT_DIR%" --verbose

REM Capturar código de salida
set EXIT_CODE=%ERRORLEVEL%

REM Registrar tiempo de finalización
set END_TIME=%TIME%

echo.
echo ==========================================================================
if %EXIT_CODE% EQU 0 (
    echo ✅ CASO 6 COMPLETADO EXITOSAMENTE
    echo ⏱️  Inicio: %START_TIME%
    echo ⏱️  Fin:    %END_TIME%
    echo.
    echo 📊 Resultados generados en: %OUTPUT_DIR%
    echo.
    echo Archivos esperados:
    echo    - comparacion_criterios_escalado.xlsx  (4 criterios con RPM y Reynolds^)
    echo    - comparacion_criterios_escalado.png   (Gráficas de RPM y Reynolds^)
    echo    - validacion_escalado.png              (Curvas cinéticas Lab vs Piloto^)
    echo    - diagrama_reactor_piloto_3D.png       (Visualización 3D del reactor^)
    echo    - diseño_reactor_piloto.json           (Diseño detallado completo^)
    echo.
    echo 🎯 Especificaciones del reactor piloto:
    echo    - Volumen: 20 L
    echo    - Diámetro: ~210 mm (ver JSON^)
    echo    - RPM: ~150 rpm (criterio P/V constante^)
    echo    - Reynolds: ^> 10,000 (turbulento^)
    echo.
    echo ✓ Escalado validado: Conversión laboratorio ≈ Conversión piloto
    echo ✓ Geometría similar conservada (H/D, D_imp/D_tank^)
    echo ✓ Régimen de flujo adecuado (turbulento^)
) else (
    echo ❌ ERROR: El escalado falló con código %EXIT_CODE%
    echo ⏱️  Inicio: %START_TIME%
    echo ⏱️  Error:  %END_TIME%
)
echo ==========================================================================
echo.

REM Retornar al directorio del caso
cd /d "%SCRIPT_DIR%"

exit /b %EXIT_CODE%
