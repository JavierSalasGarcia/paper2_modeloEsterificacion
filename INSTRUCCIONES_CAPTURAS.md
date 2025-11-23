# Instrucciones para Capturas de Pantalla de la Interfaz Streamlit

Para completar la sección de la interfaz en el artículo, necesitas tomar **2 capturas de pantalla** de la aplicación Streamlit.

---

## Paso 1: Ejecutar la Interfaz

```bash
cd /home/user/paper2_modeloEsterificacion
streamlit run gui_streamlit.py
```

La interfaz se abrirá en tu navegador en `http://localhost:8501`

---

## Paso 2: Tomar las Capturas de Pantalla

### 📸 Captura 1: Pestaña de Configuración
**Nombre del archivo:** `interfaz_configuracion.png`

**Qué mostrar:**
1. Selecciona cualquier caso en la barra lateral (recomendado: Caso 1 o Caso 2)
2. Ve a la pestaña **"⚙️ Configuración"**
3. Asegúrate de que se vean:
   - La barra lateral con el selector de casos
   - El panel izquierdo con la vista JSON (📄 Vista JSON Actual)
   - El panel derecho con el editor (✏️ Editor de Configuración)
   - Los botones "💾 Guardar Cambios" y "🔄 Recargar Original"

**Cómo tomar la captura:**
- Usa la herramienta de captura de tu sistema operativo
- O presiona `Ctrl+Shift+S` (Windows/Linux) o `Cmd+Shift+4` (Mac)
- Captura toda la ventana del navegador (incluyendo la barra lateral)

**Dónde guardar:**
```
/home/user/paper2_modeloEsterificacion/figuras/interfaz_configuracion.png
```

---

### 📸 Captura 2: Pestaña de Ejecución
**Nombre del archivo:** `interfaz_ejecucion.png`

**Qué mostrar:**
1. Mantén el mismo caso seleccionado
2. Ve a la pestaña **"▶️ Ejecutar"**
3. Asegúrate de que se vean:
   - El resumen de configuración (nombre del caso, modo, carpeta)
   - La sección "Ver configuración completa" (puede estar colapsada)
   - El botón grande "▶️ Ejecutar [Nombre del Caso]"

**OPCIONAL:** Si quieres mostrar la ejecución en progreso:
- Presiona el botón de ejecutar
- Toma la captura mientras se muestra la barra de progreso y los mensajes de estado

**Dónde guardar:**
```
/home/user/paper2_modeloEsterificacion/figuras/interfaz_ejecucion.png
```

---

## Paso 3: Verificar que las Imágenes Están Guardadas

Verifica que ambas capturas estén en la carpeta correcta:

```bash
ls -lh /home/user/paper2_modeloEsterificacion/figuras/interfaz_*.png
```

Deberías ver:
- `interfaz_configuracion.png`
- `interfaz_ejecucion.png`

---

## Paso 4: Incluir la Sección en el Artículo

Una vez que tengas las capturas, incluye la sección en `articulo_conciso.tex` agregando esta línea donde quieras que aparezca (recomendado: después de la sección de Resultados):

```latex
\input{seccion_interfaz}
```

Por ejemplo, podrías agregarlo antes de las Conclusiones:

```latex
\section{Resultados y Discusión}
...

% Incluir sección de interfaz gráfica
\input{seccion_interfaz}

\section{Conclusiones}
...
```

---

## Notas Importantes

1. **Formato de imagen:** PNG es recomendado para capturas de pantalla
2. **Resolución:** Usa la resolución nativa de tu pantalla (no es necesario redimensionar)
3. **Tamaño del archivo:** Si las imágenes son muy grandes (>1 MB), puedes comprimirlas con herramientas como TinyPNG
4. **Nombres exactos:** Asegúrate de usar exactamente los nombres indicados (`interfaz_configuracion.png` y `interfaz_ejecucion.png`) porque están referenciados en el archivo LaTeX

---

## Alternativa: Usar Casos Específicos

Si quieres que las capturas sean más representativas, puedes:

**Captura 1:** Mostrar **Caso 2 - Ajuste de Parámetros Cinéticos** (tiene un JSON más interesante)
**Captura 2:** Mostrar **Caso 3 - Optimización Multi-Objetivo** en ejecución

---

## Solución de Problemas

### La carpeta `figuras/` no existe
```bash
mkdir -p /home/user/paper2_modeloEsterificacion/figuras
```

### Streamlit no se instala
```bash
pip install streamlit
```

### La interfaz no se abre
Verifica que estás ejecutando desde la carpeta raíz del proyecto y que `main.py` existe.

---

**¡Listo!** Una vez que tengas las capturas, compila el artículo con pdflatex y verás las figuras integradas en la sección de la interfaz.
