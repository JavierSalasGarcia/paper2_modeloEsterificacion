# Plantillas para el Sistema de Modelado de Esterificación

Esta carpeta contiene plantillas listas para llenar con tus datos experimentales.

## 📄 Archivos Incluidos

### 1. `plantilla_datos_gc.csv`
Plantilla para datos de cromatografía GC-FID.

**Columnas:**
- `tiempo_min`: Tiempo de muestreo en minutos
- `compuesto`: Nombre del compuesto (TG, MeOH, FAME, GL, Estándar_Interno)
- `area_pico`: Área del pico cromatográfico
- `tiempo_retencion_min`: Tiempo de retención en minutos
- `notas`: Notas adicionales (opcional)

**Instrucciones:**
1. Reemplaza los valores de ejemplo con tus datos reales
2. Mantén el formato CSV y los nombres de columnas
3. Asegúrate de incluir todas las muestras temporales
4. El Estándar_Interno debe aparecer en cada punto de tiempo

### 2. `plantilla_experimento.json`
Plantilla completa para un experimento con todas las variables.

**Instrucciones:**
1. Copia esta plantilla para cada experimento
2. Renombra como `experimento_01.json`, `experimento_02.json`, etc.
3. Llena todos los campos con tus datos experimentales
4. Respeta el formato JSON (comillas, comas, llaves)

### 3. `plantilla_config.yaml`
Archivo de configuración para parámetros del sistema.

**Instrucciones:**
1. Ajusta los parámetros según tus necesidades
2. Guarda como `config.yaml` en la raíz del proyecto
3. El sistema leerá esta configuración automáticamente

### 4. Scripts de Ejemplo

Scripts Python listos para ejecutar cada modo de operación:
- `ejemplo_01_procesar_gc.py`: Procesamiento de datos GC-FID
- `ejemplo_02_ajustar_parametros.py`: Ajuste de parámetros cinéticos
- `ejemplo_03_optimizar.py`: Optimización de condiciones
- `ejemplo_06_workflow_completo.py`: Flujo completo de análisis

**Instrucciones:**
1. Copia el script que necesites a la raíz del proyecto
2. Ajusta las rutas de archivos según tus datos
3. Ejecuta: `python ejemplo_XX_nombre.py`

## 🚀 Inicio Rápido

### Opción 1: Usar las plantillas directamente

```bash
# 1. Copiar plantilla CSV y llenar con tus datos
cp plantillas/plantilla_datos_gc.csv data/raw/mi_experimento.csv
# Editar mi_experimento.csv con tus datos

# 2. Procesar datos
python main.py --mode process_gc --input data/raw/mi_experimento.csv --output data/processed/
```

### Opción 2: Usar plantilla JSON completa

```bash
# 1. Copiar plantilla JSON y llenar con tus datos
cp plantillas/plantilla_experimento.json mi_experimento.json
# Editar mi_experimento.json con tus datos

# 2. Ajustar parámetros
python main.py --mode fit_params --input mi_experimento.json --output results/
```

### Opción 3: Usar scripts de ejemplo

```bash
# 1. Copiar script de ejemplo
cp plantillas/ejemplo_06_workflow_completo.py .

# 2. Editar rutas en el script
# 3. Ejecutar
python ejemplo_06_workflow_completo.py
```

## 📝 Notas Importantes

- **Formato CSV**: Usa coma (,) como separador
- **Formato JSON**: Verifica que sea JSON válido (usa un validador online si es necesario)
- **Unidades**: Respeta las unidades especificadas en cada campo
- **Nombres de compuestos**: Usa los nombres exactos: TG, MeOH, FAME, GL

## 🆘 Ayuda

Si tienes problemas:
1. Verifica que el formato de archivo sea correcto
2. Consulta el tutorial completo en `docs/tutorial_uso.pdf`
3. Revisa los ejemplos en la documentación principal
