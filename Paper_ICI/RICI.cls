    \ProvidesClass{RICI}[2024/12/10 Custom class for specific document formatting]
    
    
    \LoadClass[12pt, letterpaper, twoside]{article}
    
    % Paquetes necesarios
    \RequirePackage[utf8]{inputenc}
    \RequirePackage[spanish]{babel}
    \RequirePackage[T1]{fontenc}
    \RequirePackage{times}
    \RequirePackage{graphicx}
    \RequirePackage{anyfontsize}
    \RequirePackage{lipsum}
    \RequirePackage{setspace}
    \RequirePackage{multicol}
    \RequirePackage{float}
    \RequirePackage{fancyhdr}
    \RequirePackage{xcolor}
    \RequirePackage{eso-pic}
    \RequirePackage{tikz}
    \RequirePackage{tikzpagenodes}
    \RequirePackage{cite}
    \RequirePackage{hyperref}

    % Configuración de hyperref para enlaces en azul sin recuadros
    \hypersetup{
        colorlinks=true,
        linkcolor=blue,
        citecolor=blue,
        filecolor=blue,
        urlcolor=blue,
        linktoc=all
    }

    \RequirePackage{needspace}
    \RequirePackage{longtable}
    \RequirePackage{array}
    \RequirePackage{booktabs}
    \RequirePackage{amsmath}
    \RequirePackage{ltablex}
    \RequirePackage{orcidlink}
    \RequirePackage{titlesec}
    \RequirePackage{caption}
    \RequirePackage{multicol}
    \RequirePackage{titlesec}
    \RequirePackage{fancyhdr}
    \RequirePackage{atbegshi}
    %\RequirePackage{footmisc}
    \RequirePackage{atveryend}[2019/12/05]
    \RequirePackage{uniquecounter}[2009/12/18]
    \usetikzlibrary{calc}
    \usepackage{ifthen}
    
    
    % Agregar imagen de fondo solo en la primera página
    \newcommand{\paginicial}{1} % Define la página inicial
    \newcommand{\corrAuthor}{*}
    
    
    \AddToShipoutPictureBG*{%
    \ifnum\value{page}=\paginicial % Solo en la primera página
    \AtPageLowerLeft{\includegraphics[width=\paperwidth,keepaspectratio]{imagenes/encabezado1.eps}}%
   
    \else
    \AtPageUpperLeft{}
    \fi
    }
    

    % Comando para imprimir el título con formato grande
    \newcommand{\printTitleSpa}{%
        \color{colorencabezados}\fontsize{22}{18}\selectfont\textbf{\@title}
    }
    

    
    
    % Definir el comando titleEng
    \newcommand{\titleEng}[1]{\gdef\@titleEng{\color{colorencabezados}#1}}
    
    
    
    % Configuración de caption
    \DeclareCaptionLabelFormat{boldandupper}{\textbf{#1~#2}}
    \DeclareCaptionFont{bold}{\textbf{#1}}
    \captionsetup{
        labelsep=period,
        labelformat=boldandupper,
        font=bold
    }
    
    %Configuración de caption para figuras
    \addto\captionsspanish{
        \renewcommand{\figurename}{\textbf{FIGURA}}
    }
    
    % Configuración de caption específica para tablas
    \captionsetup[table]{
      name=Tabla
    }
    
    
    % Definición de colores
    \definecolor{colorencabezados}{HTML}{3C90A8}
    
    % Nuevos entornos para Resumen y Abstract
    \newenvironment{resumen}
      {%
     % \vspace{-1em}
        \section*{\textbf{\textsc{Resumen}}} % Agrega un título no numerado
        \begin{multicols}{2}%
        %\setlength{\parindent}{0.5cm}%
      }
      {%
        \end{multicols}%
        %\vspace{-0.2cm}%
      }
    
    \renewenvironment{abstract}
      {%
        \section*{\textbf{\textsc{Abstract}}} % Agrega un título no numerado
        \begin{multicols}{2}%
       % \setlength{\parindent}{0.5cm}%
      }
      {%
        \end{multicols}%
       % \vspace{-0.2cm}%
      }
    
    % Comandos para Palabras Clave
    \newcommand{\palabrasclave}[1]{
      \noindent\textbf{\textit{Palabras clave:}} \emph{#1}
    }
    
    \newcommand{\keywords}[1]{
      \noindent\textbf{\textit{Keywords:}} \emph{#1}
    }
    
    % Redefinición del comando \large para ajustar el tamaño de fuente de los encabezados
    \renewcommand{\large}{\fontsize{13}{13}\selectfont}
    
    % Configuración de los comandos de sección y subsección
    \titleformat{\section}
     % {\needspace{3cm}\normalfont\large\bfseries\color{colorencabezados}}
      {\normalfont\large\bfseries\color{colorencabezados}}
      {} % Sin prefijo
      {0pt} % Sin espacio antes del título
      {\textsc} % Aplicar "small caps" al texto del título
      [\vspace{-0.5em}] % Espacio después del título
    
    \titlespacing*{\section}
      {0pt}   % Sangría izquierda
      {0pt}   % Espaciado antes del título (ajustado a cero para eliminar el salto)
      {0.5em} % Espaciado después del título 
    
    \titleformat{\subsection}[hang]
      %{\needspace{3cm}\normalfont\large\itshape}
      {\normalfont\large\itshape}
      {}
      {0pt}
      {\noindent}
      [\vspace{-0.5em}] % Espacio después del título
    
    \titlespacing*{\subsection}
      {0pt}   % Sangría izquierda
      {0pt}   % Espaciado antes del título (ajustado a cero para eliminar el salto)
      {0.5em} % Espaciado después del título
      
      
    % Documento específico
    \usepackage{indentfirst}
    \renewcommand{\baselinestretch}{1.2} %para mas espaciado entre lineas
    \setlength{\parindent}{0.5cm}
    
    % Configuración de página
    \RequirePackage{geometry}
    \geometry{
    letterpaper,
    left=2.0cm,
    right=2.0cm,
    top=3.0 cm,
    bottom=2.5cm,
    headheight=68pt,
    includefoot
    }
    
    
    
    % Redefinir footnotemark para aceptar índices personalizados
    \renewcommand{\footnotemark}[1][]{%
      \ifx#1\empty\relax
        \stepcounter{footnote}\xdef\@thefnmark{\thefootnote}%
      \else
        \xdef\@thefnmark{#1}%
      \fi
      \@footnotemark
    }
    
    % Comando para agregar notas al pie en el título con números
    \newcommand{\authornote}[1]{\footnotemark[#1] } % Genera una marca de pie de página con número
    \newcommand{\authoraddress}[2]{\footnotetext[#1]{\scriptsize #2}  } % Asocia la dirección a la nota al pie
    
    
    % Definir la macro para el correo electrónico
    \newcommand{\emailCorr}[1]{%
        \gdef\@correspondingemail{#1} % Almacenar el correo en una macro interna
    }
    
    % Comando para mostrar el correo electrónico del autor correspondiente
    \newcommand{\showemailCorr}{%
        \ifdefined\@correspondingemail % Verificar si el correo ha sido definido
            
            (*{\@correspondingemail})
        \else
            \textbf{Correo de correspondencia no definido.} % Mensaje por defecto si no se define
        \fi
    }
    
    
    \newcommand{\fecharec}[1]{\gdef\@fecharec{#1}} %fecha de envio
    \newcommand{\fechaace}[1]{\gdef\@fechaace{#1}} % fecha de aceptado
    
    \let\oldAuthor\author % Guardar la definición original de \author
    \renewcommand{\author}[1]{\gdef\@author{#1}}
    \hyphenpenalty=10000
    
    \renewcommand{\maketitle}{
  
      \begingroup % Iniciar un grupo local para los cambios de estilo
        \centering % Centrar todo el contenido del encabezado
      
       \vspace*{2em} % Añadir espacio adicional antes del título
        % Título en español
        \ifdefined\@title
       
          { \printTitleSpa} % Aplicar formato al título en español
          
          \vspace{2.5em} % Espacio entre los elementos
        \fi
    
        % Título en inglés
        \ifdefined\@titleEng
         
         {\fontsize{16}{14}\selectfont\textbf{\@titleEng}}
         
        \fi
    
        % Autores
        \ifdefined\@author
          {\fontsize{10}{12}\selectfont \@author} % Aplicar formato a los autores
          
        \fi
    
        % Correo electrónico del autor correspondiente
        \ifdefined\@correspondingemail
        \vspace{-0.3cm}
          {\fontsize{10}{12}\selectfont \centering \showemailCorr \\}
          {  \vspace{0.4cm}
    	\fontsize{10}{12}\selectfont Recibido: \@fecharec \quad Aceptado: \@fechaace}
        
        \fi
       
      
      \endgroup
    }
    
    
    
    \newcommand{\numpaginajsg}{
        \begin{tikzpicture}[remember picture,overlay]
            \node[draw=none, text width=3cm, align=center, font=\small, text=colorencabezados] at ($(current page.south east) + (-2cm, 2cm)$) {pág. \thepage};
        \end{tikzpicture}
    }
    
    % Ajustar el espaciado entre párrafos
    \setlength{\parskip}{0.2cm}
    
    \pagestyle{fancy}
    \fancyhf{} % Limpia el encabezado y pie de página para todas las páginas
    %\fancyfoot[C]{\thepage} % Coloca el número de página al centro del pie de página para todas las páginas
    \renewcommand{\headrulewidth}{0pt}
    \renewcommand{\footrulewidth}{0pt}
    
    \fancypagestyle{firstpage}{
        \fancyhf{} % Limpiar todos los encabezados y pies de página
        \fancyfoot{} % Asegurarse de que el pie de página está vacío
        \renewcommand{\footrulewidth}{0pt}
        \renewcommand{\headrulewidth}{0pt} % Sin línea en el encabezado
        \renewcommand{\footrulewidth}{0pt}
         \fancyfoot[LE,RO]{ \color{colorencabezados} \bottombox}  
         \fancyfootoffset{1cm}

    }
    
    \AtBeginDocument{
        \thispagestyle{firstpage} % Aplica el estilo de la primera página automáticamente
       %\AtBeginShipoutFirst{\bottombox}
    }
    
    \newcommand{\autencabez}[1]{\gdef\@autencabez{#1}}
    
    
    % Definiciones de las macros
    \newcommand{\VolR}[1]{\gdef\@VolR{#1}}
    \newcommand{\NumR}[1]{\gdef\@NumR{#1}}
    \newcommand{\meses}[1]{\gdef\@meses {#1}}
    \newcommand{\pagfinal}[1]{\gdef\@pagfinal{#1}}
    \newcommand{\encabA}{Ideas en Ciencias de la Ingeniería Vol. \@VolR, Núm. \@NumR}
    \newcommand{\encabB}{\@meses\ " " ISSN: 2992-7447  págs. \paginicial- \@pagfinal}
    
    \newcommand{\numerorevista}{ISSN: 2992-7447 Vol. \@VolR, Núm. \@NumR " " \@meses " " págs. \paginicial- \@pagfinal}
    
    % Define the formatted title command
    % Define another command that uses formatted title and applies additional formatting
    \newcommand{\encabezadoimpar}{
    \begin{flushright}
    {\fontfamily{ptm}\fontsize{8}{8}\selectfont \@autencabez}\\
    \color{colorencabezados} \fontsize{8}{8}\selectfont \textsc{\@title}
    \end{flushright}
    }
    
    
    \newcommand{\encabezadopar}{
    	\color{colorencabezados}
    	\begin{flushright}
    		{\fontfamily{ptm}\fontsize{8}{8}\selectfont \textsc{\encabA}}\\
    		\color{colorencabezados}
    		{\fontfamily{ptm}\fontsize{8}{8}\selectfont \encabB}
    	\end{flushright}
    }
    
    \newcommand{\bottombox}{
        \begin{tikzpicture}[remember picture,overlay]
            \node[align=center,font=\fontsize{8}{10}\selectfont] at ($(current page.south)+(0,1 cm)$) {\numerorevista};
        \end{tikzpicture}
    }
    
    %encabezados
    \fancypagestyle{mystyle}{
        \fancyhf{}  % Limpiar todos los encabezados y pies de página existentes
        \fancyfoot{}  % Eliminar contenido previo del pie de página
        \fancyhead[RE]{\encabezadopar}  % Encabezado para páginas pares
        \fancyhead[LO]{\encabezadoimpar}  % Encabezado para páginas impares
        \fancyfoot[LE,RO]{\numpaginajsg}  % Usar el nuevo comando para el pie de página en las páginas izquierdas y derechas
         \renewcommand{\headrulewidth}{0pt} % Esto elimina la línea del encabezado
         
    
     }
     

    % Aplicar el estilo de página por defecto
    \pagestyle{mystyle}
    
    
    
    \endinput
