<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE) -->

<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-log.png" alt="Omega-Log" width="384">
</div>

# 📜 OMEGA-LOG

**Gestor y visor de logs de servidor**

> Desarrollado por [kraynux](https://github.com/kraynux) para [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Página oficial: [OMEGA-LOG](https://kraynux.snake-mackarel.ts.net/omega-log/translation/es/) &nbsp; Vista previa: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-log/screenshots/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-Textual%20TUI-cyan.svg)](https://github.com/Textualize/textual)

🌐 Interfaz, documentación y exportaciones disponibles en **17 idiomas**.  
**Idiomas:**
<img src="https://flagcdn.com/w20/fr.png" alt="France" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-log** es la herramienta de la suite `omega-` dedicada a la gestión, la lectura y el análisis de archivos de logs de servidor en TUI — detección automática de los servicios activos y de sus logs, biblioteca central, tres modos de lectura (seguimiento simple, lectura clásica, fusión de varios archivos mediante `lnav`), tratamiento de IP, estadísticas, rotación/copia de seguridad/restauración, purga segura y exportación. Construida mediante **portabilidad y adaptación** del código ya maduro de [omega-fire](https://github.com/kraynux) y [omega-serv](https://github.com/kraynux) en lugar de reescribirla desde cero.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/es/omega-log/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/es/omega-log/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/es/omega-log/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/es/omega-log/D.png" width="24%" />
</p>

## 1. Visión y alcance

Omega-log responde a una pregunta sencilla: «¿qué está pasando en mis logs y cómo me ocupo de ellos?» — sin depender de una lista fija de rutas conocidas, sin ejecutarse nunca como root por defecto y sin perder ni corromper nunca en silencio un archivo de log real.

### Lo que hace Omega-log

- Detecta automáticamente los servicios activos en la máquina (servidores web, bases de datos, correo, DNS, seguridad, `omega-serv`...) y propone importar sus logs conocidos, uno a uno o todos a la vez — además de un escaneo manual de cualquier carpeta.
- Centraliza los logs que hay que tratar en una única Biblioteca, punto de entrada de todas las demás pantallas.
- Lee un log en uno de tres modos según la necesidad: seguimiento simple con análisis y estadísticas, lectura clásica en bruto con seguimiento en directo, o fusión de varios archivos encapsulando `lnav`.
- Guarda combinaciones de logs + visor como Favoritos, para un lanzamiento directo.
- Calcula el top 10 de IP por periodo, o busca una IP concreta, y permite eliminarlas de forma selectiva en uno o varios archivos.
- Calcula estadísticas de acceso (volumen, IP únicas, tasa de error, distribución horaria) exportables en JSON o HTML con tema.
- Hace copias de seguridad (compresión + retención automática), a mano o cada noche mediante copias programadas, restaura (fusión o sobrescritura, con copia de seguridad previa) y purga (truncado in situ o eliminación) los archivos de log, siempre con confirmación explícita.
- Controla la salud de los logs (permisos, logs mudos o dañados, espacio en disco, copias de seguridad) e indica qué hacer para cada hallazgo.
- Se adapta automáticamente a las capacidades del terminal (colores, tamaño) mediante `omega-lib`, como el resto de la suite.

### Lo que Omega-log no hace

| Función | Herramienta responsable |
|---|---|
| Cortafuegos, reglas de red, detección de intrusiones | OMEGA-FIRE |
| Servidor web, reverse proxy, WAF, Active Defense | OMEGA-SERV |
| Escaneo de puertos, identificación de servicios de red | OMEGA-CHECK |
| Observación de red, identidad digital de un objetivo | OMEGA-TRACK |

(Todavía) sin CLI con paridad completa con la TUI (el modo de línea de comandos actual solo cubre el escaneo de servicios, ver §3.2), sin agregación centralizada de varias máquinas, sin alertas en tiempo real por umbral — Omega-log sigue siendo una herramienta de inspección y mantenimiento local, no un SIEM.

### Advertencia de uso

Las acciones de mantenimiento (**Purgar**, **Rotate → Restaurar en modo Sobrescritura**) modifican o borran definitivamente el contenido real de sus archivos de log — siempre precedidas de una confirmación explícita que detalla los archivos afectados, nunca activadas automáticamente. En caso de duda, haga una copia (**Rotate → Hacer copia ahora**) antes de actuar.

## 2. Instalación

### Requisitos previos

- Python 3.10+
- Linux (probado en Arch/Manjaro, Debian/Ubuntu, RHEL/Fedora)
- `lnav` instalado en el sistema, solo para el visor de fusión de varios archivos (los otros dos visores funcionan normalmente sin él):

```bash
# Arch / Manjaro
sudo pacman -S lnav

# Debian / Ubuntu
sudo apt install lnav
```

### Instalación

```bash
[ -d omega-log ] && echo "ℹ️ Ya extraído aquí, paso omitido." || tar -xzf omega-log-1.6.0.tar.gz
cd omega-log/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Crea el entorno virtual `.venv` si aún no existe.
2. Instala las dependencias (primero `omega-lib` incluida si está presente, después `pip install -e .` — `pyproject.toml` sigue siendo la única fuente de verdad).
3. Hace ejecutables `omega-log.sh` e `install.sh`.
4. Comprueba la presencia de `lnav` (aviso informativo si falta, nunca bloqueante).
5. Añade el alias `log` a `~/.bashrc` y `~/.zshrc` (sin duplicado si ya existe).

### Dependencias

Declaradas en `pyproject.toml` (sin `requirements.txt` aparte):
- `omega-lib`: biblioteca compartida de la suite (temas TUI + exportación, detección del terminal, almacenamiento de ajustes)
- `textual`: interfaz TUI
- `jinja2`: exportación HTML con tema (estadísticas, archivos)
- `pyte`: emulación de terminal para el visor `lnav` (renderizado en un pty encapsulado)
- Dependencias de desarrollo (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `ruff`, `mypy`

## 3. Uso

### 3.1. Modo interactivo (TUI)

Recomendado para el uso diario — se lanza sin argumentos:

```bash
./omega-log.sh
```
si ha creado el alias, escriba simplemente `log` en un terminal nuevo:
```bash
log
```

Recorrido general: pantalla de inicio → menú principal (dos columnas — Registro de capacidades/Biblioteca/Ver los logs/Favoritos/Ver y tratar IP/Estadísticas (acceso) a un lado, Rotate/Purgar/Exportar/Salud de los logs/Opciones/Ayuda al otro) → pantalla de la función elegida → vuelta al menú (`Esc`). La ayuda completa (`a`) detalla cada pantalla, cada visor y los conceptos transversales (elevación sudo puntual, estados de los logs, selección por números) — ver §4 para lo esencial.

#### Atajos de teclado

| Tecla | Acción |
|---|---|
| `↑` / `↓` | Navegar entre los elementos de una pantalla |
| `Tab` / `Mayús+Tab` | Navegar entre los campos de un formulario |
| `Esc` | Volver a la pantalla anterior (confirmación de salida en la pantalla de inicio) |
| `t` | Tema siguiente (aplicado de inmediato, sin confirmación) |
| `r` | Actualizar la detección del terminal |
| `a` | Mostrar la ayuda (exhaustiva, un capítulo por pantalla) |
| `q` | Salir (con confirmación) |

### 3.2. Modo línea de comandos (CLI)                                                              

Todavía sin paridad completa con la TUI (favoritos, purga... llegarán con sus propias fases, ver `plan_omega_log.md` §12):

```bash
# Detecta los servicios activos y sus logs conocidos
python -m omega_log scan

# + escaneo manual de una carpeta adicional
python -m omega_log scan --path /var/log

# Version instalada, y comparacion con la ultima version publicada
python -m omega_log version --check

# Copias programadas que han vencido (lanzado cada noche por el timer systemd o la crontab)
python -m omega_log rotate run-automations
```

### 3.3. Variables de entorno

| Variable | Efecto |
|---|---|
| `OMEGA_LOG_VAR_DIR` | Cambia la ubicación de la carpeta de estado de la aplicación (`./var` por defecto, relativa a la carpeta de lanzamiento) |
| `OMEGA_LOG_LANG` | Fuerza el idioma de la interfaz para la sesión (p. ej. `en`, `de`, `ja`) sin cambiar el ajuste guardado |

## 4. Funcionalidades

| Pantalla | Descripción |
|---|---|
| **Registro de capacidades** | Detecta los servicios activos en la máquina y propone importar sus logs conocidos, uno a uno o todos a la vez. Escaneo manual de una carpeta como complemento. |
| **Biblioteca** | Centro que referencia todos los logs que hay que tratar — alimentado por el Registro, por importación manual, por los logs conocidos de Omega-Serv o por una copia recuperada por SSH. |
| **Ver los logs** | Selección de uno o varios logs de la Biblioteca + elección del visor (1 log → los 3 visores; 2+ logs → solo `lnav`). |
| **Favoritos** | Combinaciones de logs + visor guardadas con un nombre, para un lanzamiento directo. |
| **Ver y tratar IP** | Top 10 de IP por periodo (24h/7d/30d/todo), o búsqueda de una IP concreta (IPv4 o IPv6), y eliminación selectiva de una IP en uno o varios logs. |
| **Estadísticas (acceso)** | Volumen, IP únicas, tasa de error, top de IP, distribución horaria — exportación JSON/HTML con 5 temas. |
| **Rotate** | Copia de seguridad comprimida de un log + retención automática de los archivos sobrantes + restauración (fusión o sobrescritura, con copia de seguridad previa). **Copias programadas**: un log copiado cada día, semana o mes, ejecutado cada noche por un timer systemd o una línea de su crontab (OpenRC, runit), con su cuenta, nunca root. |
| **Purgar** | Vacía el contenido de un log (truncado in situ, seguro para un servicio que aún lo tiene abierto) o elimina por completo uno o varios archivos — siempre con confirmación. |
| **Exportar** | Exportación de la lista de archivos (Rotate) en JSON o HTML con tema. |
| **Salud de los logs** | Control de solo lectura de los logs de la Biblioteca, del disco, de las copias de seguridad y de las copias programadas: permisos, logs mudos o dañados, fechas, logrotate, días antes de que el disco se llene, con la acción que hay que realizar. Corrección de permisos demasiado abiertos (con sudo si hace falta), exportación JSON/HTML/TXT. |
| **Opciones** | Tema, perfil de renderizado, idioma de la interfaz e idioma de las exportaciones (17 idiomas), purga de las carpetas de la aplicación (exports/screenshots). |

### Los 3 visores

1. **Simple** — seguimiento en directo con análisis genérico (marca de tiempo, IP, nivel, servicio) y mini tabla de estadísticas. Para un access log HTTP reconocido, columnas adicionales Código HTTP / latencia, coloreadas por umbral.
2. **Clásico** — lectura de las últimas líneas en bruto + conmutador «Seguir en directo», sin análisis: lo más sencillo y fiable sea cual sea el formato.
3. **lnav** — fusión de varios archivos en un terminal encapsulado (pty), para un análisis cruzado. Ciclo de tema (`t`), marcado + copia al portapapeles (`Ctrl+C`, OSC 52), salida (`Ctrl+Q`) — todos interceptados antes que el propio `lnav`.

## 5. Compatibilidad de terminales

La TUI (Textual) detecta automáticamente las capacidades del terminal (emulador, tamaño) y adapta en consecuencia su hoja de estilo estructural (`complete`/`standard`/`reduced`/`mono`), sin ninguna opción manual — la misma política compartida por toda la suite `omega-` (`omega-lib`, `terminal/policies.py`). Se puede actualizar en directo con la tecla `r`.

### Perfil según el emulador detectado

| Emulador | Perfil inicial |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderno | `reduced` |
| TTY Linux, SSH antiguo | `mono` |
| Emulador no reconocido | `reduced` (alternativa por defecto) |

### Perfil según el tamaño del terminal

| Tamaño mínimo (columnas × líneas) | Techo de perfil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| por debajo | `mono` |

El perfil final elegido es **el más restrictivo de los dos** (emulador y tamaño).

## 6. Arquitectura

Clean Architecture (dominio / aplicación / infraestructura / interfaces), la misma convención que el resto de la suite OMEGA:

```text
src/omega_log/
├── core/            Registro de capacidades (deteccion de servicios)
├── domain/          Logica de negocio pura (analisis, estadisticas, rotacion, purga)
├── ports/           Contratos (Protocol)
├── application/     Casos de uso
├── infrastructure/  Implementaciones reales (sondas, almacenamiento, archivos, exportacion, lnav, concurrencia)
├── interfaces/      TUI (Textual) + CLI
└── app/             Composition root
```

Depende de [`omega-lib`](../../../../LIB/omega-lib) para el tema (10 temas TUI + 5 temas de exportación), la detección del terminal y el almacenamiento de ajustes — la misma base que el resto de la suite. Los cálculos pesados (top de IP, estadísticas de acceso) se ejecutan en un `ProcessPoolExecutor` dedicado (`infrastructure/concurrency/`), nunca en el hilo de la interfaz, para seguir siendo reactiva incluso con un archivo de varios cientos de miles de líneas.

## 7. Pruebas

```bash
source .venv/bin/activate
pytest tests/ -q      # 243 pruebas
ruff check .
mypy src
```

Estructura: `tests/unit/` (dominio y aplicación, sin E/S real), `tests/integration/` (archivos reales, TUI headless mediante la API `Pilot` de Textual).

## 8. Estado del desarrollo

Las 10 fases del plan de desarrollo están terminadas: base, dominio, TUI básica, visores, favoritos/biblioteca/IP, mantenimiento, estadísticas/exportación, finalización, elevación sudo puntual, cálculos CPU-bound trasladados a un proceso aparte — ver `plan_omega_log.md` para el detalle de cada decisión de portabilidad. Desde la 1.6.0 se han incorporado las novedades del gestor de logs de omega-serv 2.6.0: Salud de los logs, copias programadas, búsqueda de una IP concreta, versión mostrada y comprobación de actualizaciones.

## 9. Licencia

MIT — ver [LICENSE](../../../LICENSE).

---

> Omega-log — Detectar, centralizar, leer, analizar, mantener.
> Sus logs siguen siendo suyos: ninguna elevación de privilegios sin una necesidad real, ninguna acción destructiva sin confirmación.
