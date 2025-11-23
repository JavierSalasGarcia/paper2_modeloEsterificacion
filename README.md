# Sistema Unificado de Modelado Cinético de Biodiesel

Sistema open-source en Python para modelado, optimización y análisis de producción de biodiesel mediante transesterificación catalítica.

**Autores:** J. Salas-García et al.
**Licencia:** MIT
**Año:** 2025

---

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación

```bash
# Clonar el repositorio
git clone <URL_del_repositorio>
cd paper2_modeloEsterificacion

# Instalar dependencias
pip install -r requirements.txt
```

---

## 🎯 Modos de Uso

Este sistema ofrece **3 formas** de ejecutar los casos de estudio, ordenadas de más simple a más avanzada:

### 1️⃣ Interfaz Web (Recomendado para usuarios no técnicos)

La forma más sencilla de usar el sistema. Interfaz visual en el navegador.

```bash
# Instalar Streamlit (solo la primera vez)
pip install streamlit

# Ejecutar la interfaz web
streamlit run gui_streamlit.py
```

Se abrirá automáticamente en tu navegador en `http://localhost:8501`

**Características:**
- ✅ Interfaz visual amigable
- ✅ Editor de configuración JSON con validación
- ✅ Ejecución de casos con un clic
- ✅ Visualización de resultados
- ✅ No requiere conocimientos de terminal

---

### 2️⃣ Asistente Interactivo CLI (Para usuarios con terminal básica)

Asistente guiado por menú en la terminal.

```bash
python casos.py
```

**Características:**
- ✅ Menú interactivo con 6 casos
- ✅ Visualización de configuración JSON
- ✅ Opción para editar configuración
- ✅ Ejecución guiada paso a paso
- ✅ Mensajes en español con colores (requiere `colorama`)

---

### 3️⃣ Línea de Comandos Directa (Para usuarios avanzados)

Ejecución directa con `main.py` para máximo control.

```bash
python main.py --mode <modo> --output <carpeta_salida> [opciones]
```

**Ejemplo:**
```bash
python main.py --mode process_gc --input datos/experimento_60C.csv --c-tg0 0.5 --output resultados/
```

---

## 📊 Casos de Estudio Disponibles

### 📊 Caso 1: Procesamiento GC-FID
Procesa datos de cromatografía de gases con detector de ionización de llama.

**Modo:** `process_gc`
**Carpeta:** `Casos/caso1_procesamiento_gc/`

### 🔧 Caso 2: Ajuste de Parámetros Cinéticos
Calibra parámetros del modelo mediante regresión no lineal.

**Modo:** `fit_params`
**Carpeta:** `Casos/caso2_ajuste_parametros/`

### 🎯 Caso 3: Optimización Multi-Objetivo
Encuentra condiciones operacionales óptimas para maximizar conversión.

**Modo:** `optimize`
**Carpeta:** `Casos/caso3_optimizacion/`

### ⚖️ Caso 4: Comparación de Modelos
Compara modelo cinético de 1-paso versus 3-pasos.

**Modo:** `compare`
**Carpeta:** `Casos/caso4_comparacion_modelos/`

### 📈 Caso 5: Análisis de Sensibilidad Global
Identifica variables operacionales más críticas mediante diseño factorial.

**Modo:** `sensitivity`
**Carpeta:** `Casos/caso5_analisis_sensibilidad/`

### 🏭 Caso 6: Escalado de Reactores
Diseña reactor piloto desde condiciones de laboratorio.

**Modo:** `scaleup`
**Carpeta:** `Casos/caso6_escalado_reactores/`

---

## 🔧 Estructura del Proyecto

```
paper2_modeloEsterificacion/
├── main.py                    # Programa principal unificado
├── gui_streamlit.py           # Interfaz web con Streamlit
├── casos.py                   # Asistente interactivo CLI
├── Casos/                     # Casos de estudio
│   ├── caso1_procesamiento_gc/
│   ├── caso2_ajuste_parametros/
│   ├── caso3_optimizacion/
│   ├── caso4_comparacion_modelos/
│   ├── caso5_analisis_sensibilidad/
│   └── caso6_escalado_reactores/
├── src/                       # Código fuente del sistema
│   ├── kinetics/             # Modelos cinéticos
│   ├── optimization/         # Algoritmos de optimización
│   ├── sensitivity/          # Análisis de sensibilidad
│   └── utils/                # Utilidades
├── datos/                     # Datos experimentales
├── docs/                      # Documentación
└── articulo_conciso.tex       # Artículo científico (LaTeX)
```

---

## 📝 Modificar Configuraciones

Cada caso tiene un archivo de configuración JSON en su carpeta:

```
Casos/caso1_procesamiento_gc/config_caso1.json
Casos/caso2_ajuste_parametros/config_caso2.json
...
```

**Opciones para editar:**

1. **Interfaz Web:** Usar el editor visual en la pestaña "Configuración"
2. **Editor de texto:** Abrir el archivo JSON con cualquier editor de texto
3. **Asistente CLI:** El asistente indica la ubicación del archivo

---

## 📚 Documentación Adicional

- **Compilación LaTeX:** Ver `docs/README_compilacion.md`
- **Detalles de casos:** Ver `Casos/README_casos.md`
- **Algoritmos de optimización:** Ver `src/optimization/README.md`

---

## 📄 Artículo Científico

El artículo científico completo está disponible en:

- **Versión concisa (15 páginas):** `articulo_conciso.tex`
- **Versión extendida (40 páginas):** `Sistema_unificadov2.tex`

**Compilar el artículo:**

```bash
pdflatex articulo_conciso.tex
bibtex articulo_conciso
pdflatex articulo_conciso.tex
pdflatex articulo_conciso.tex
```

---

## 🐛 Solución de Problemas

### Error: "No se encuentra main.py"
**Solución:** Asegúrese de ejecutar los comandos desde la carpeta raíz del proyecto.

### Error: "ModuleNotFoundError"
**Solución:** Instale las dependencias con `pip install -r requirements.txt`

### La interfaz web no se abre
**Solución:** Verifique que Streamlit esté instalado con `pip install streamlit`

### Los colores no aparecen en casos.py
**Solución (opcional):** Instale colorama con `pip install colorama`

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haga fork del repositorio
2. Cree una rama para su feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit sus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abra un Pull Request

---

## 📧 Contacto

Para preguntas, sugerencias o reportar problemas, contacte a los autores.

---

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para detalles.

---

## 🙏 Agradecimientos

Agradecemos a la comunidad científica de código abierto por las herramientas utilizadas en este proyecto:

- NumPy, SciPy, pandas
- Cantera (modelado de reacciones químicas)
- Matplotlib, seaborn (visualización)
- Streamlit (interfaz web)
- Y muchas otras bibliotecas de Python

---

**¡Gracias por usar este sistema! 🧪**
