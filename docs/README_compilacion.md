# Compilación de Documentos LaTeX

## Tutorial de Uso del Sistema

### Archivo Principal

**Archivo**: `tutorial_uso_sistema.tex`

**Descripción**: Tutorial paso a paso completo para usar el sistema, desde la preparación de archivos hasta la ejecución de todos los módulos.

**Páginas**: ~60-70 páginas

**Contenido**:
1. Introducción y requisitos
2. Instalación y configuración
3. Preparación de archivos de datos
4. Ejecución de módulos principales
5. Interpretación de resultados
6. Casos de uso avanzados
7. Troubleshooting
8. Apéndices

### Cómo Compilar

#### En Linux/Mac

```bash
cd docs

# Primera compilación
pdflatex tutorial_uso_sistema.tex

# Si hay referencias o índices (opcional)
pdflatex tutorial_uso_sistema.tex

# El PDF generado es: tutorial_uso_sistema.pdf
```

#### En Windows

Usar MiKTeX o TeX Live:

```cmd
cd docs
pdflatex tutorial_uso_sistema.tex
```

#### En Overleaf

1. Subir `tutorial_uso_sistema.tex` a Overleaf
2. Compilar automáticamente (botón "Recompile")
3. Descargar PDF

### Requisitos de LaTeX

Paquetes necesarios (incluidos en distribuciones completas de TeX):
- inputenc
- babel (español)
- geometry
- graphicx
- amsmath, amssymb
- listings
- xcolor
- hyperref
- fancyhdr
- tcolorbox
- enumitem
- booktabs
- longtable

### Instalación de LaTeX

#### Ubuntu/Debian

```bash
sudo apt install texlive-full
```

#### Mac

```bash
brew install --cask mactex
```

#### Windows

Descargar e instalar MiKTeX: https://miktex.org/download

### Problemas Comunes

**Error: "File `logo.png' not found"**

Solución: Comentar línea con `\includegraphics[width=0.3\textwidth]{logo.png}` o crear un logo ficticio.

**Error: "Package XXX not found"**

Solución: Instalar paquete faltante:
```bash
# Ubuntu/Debian
sudo apt install texlive-latex-extra texlive-lang-spanish

# Mac
sudo tlmgr install <package-name>

# Windows (MiKTeX)
# Se instalan automáticamente al compilar
```

## Documento Académico Principal

**Archivo**: `documento_latex.tex` (creado anteriormente)

**Compilación**:
```bash
cd docs
pdflatex documento_latex.tex
bibtex documento_latex
pdflatex documento_latex.tex
pdflatex documento_latex.tex
```

(Se compila 3 veces para resolver referencias cruzadas y bibliografía)

## Notas

- Los archivos PDF generados NO se incluyen en el repositorio Git (muy pesados)
- Cada usuario debe compilar su propia versión
- Los archivos .tex son texto plano y se versionan correctamente en Git
