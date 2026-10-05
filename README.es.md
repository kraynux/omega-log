<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licencia MIT (ver archivo LICENSE) -->

<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-log.png" alt="Omega-Log" width="384">
</div>

# 📜 OMEGA-LOG

**Gestor y visor de logs de servidor**

> Desarrollado por **kraynux** para **Omega-server**
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

Página oficial: [OMEGA-LOG](https://kraynux.snake-mackarel.ts.net/omega-log/) &nbsp; Vista previa: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-log/screenshots/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-Textual%20TUI-cyan.svg)](https://github.com/Textualize/textual)

**Idiomas:**
🇫🇷 [Français](README.md) · 🇬🇧 [English](README.en.md) · 🇪🇸 **[Español](README.es.md)** · 🇷🇺 [Русский](README.ru.md) · 🇨🇳 [中文](README.zh.md)

---

**Omega-log** es la herramienta de la suite `omega-` dedicada a gestionar, leer y analizar archivos de log de servidor en una TUI — detección automática de los servicios activos y sus logs, una biblioteca central, tres modos de lectura (seguimiento simple, lectura clásica, fusión multiarchivo vía `lnav`), procesamiento de IP, estadísticas, rotación/copia de seguridad/restauración, purgado seguro y exportación. Construida mediante el **porting y adaptación** del código ya maduro de [omega-fire](https://github.com/kraynux) y [omega-serv](https://github.com/kraynux), en lugar de reescribirse desde cero.

## 1. Visión y alcance

Omega-log responde a una pregunta sencilla: «¿qué está pasando en mis logs, y cómo me ocupo de ello?» — sin depender de una lista fija de rutas conocidas, sin ejecutarse nunca como root por defecto, y sin perder ni corromper nunca silenciosamente un archivo de log real.

### Qué hace Omega-log

- Detecta automáticamente los servicios activos en la máquina (servidores web, bases de datos, correo, DNS, seguridad, `omega-serv`...) y ofrece importar sus logs conocidos, en detalle o por completo — además de un escaneo manual de cualquier carpeta.
- Centraliza los logs a procesar en una Biblioteca única, punto de entrada de todas las demás pantallas.
- Lee un log según tres modos según la necesidad: seguimiento simple con análisis y estadísticas, lectura clásica en bruto con seguimiento en vivo, o fusión multiarchivo que encapsula `lnav`.
- Memoriza combinaciones de log(s) + visor como Favoritos, para un lanzamiento directo.
- Calcula el top 10 de IP por período y permite su eliminación selectiva en uno o varios archivos.
- Calcula estadísticas de acceso (volumen, IPs únicas, tasa de error, distribución horaria) exportables en JSON o HTML con tema.
- Hace copia de seguridad (compresión + retención automática), restaura (fusión o sobrescritura, con copia de seguridad previa) y purga (truncado in situ o eliminación) los archivos de log, siempre con confirmación explícita.
- Se adapta automáticamente a las capacidades del terminal (colores, tamaño) vía `omega-lib`, como el resto de la suite.

### Qué no hace Omega-log

| Función | Herramienta responsable |
|---|---|
| Cortafuegos, reglas de red, detección de intrusiones | OMEGA-FIRE |
| Servidor web, proxy inverso, WAF, Active Defense | OMEGA-SERV |
| Escaneo de puertos, identificación de servicios de red | OMEGA-CHECK |
| Observación de red, identidad digital de un objetivo | OMEGA-TRACK |

Todavía no hay una CLI con paridad completa respecto a la TUI (el modo de línea de comandos actual solo cubre el escaneo de servicios, ver §3.2), no hay agregación centralizada multi-máquina, ni alertas en tiempo real por umbral — Omega-log sigue siendo una herramienta de inspección y mantenimiento local, no un SIEM.

### Aviso de uso

Las acciones de mantenimiento (**Purgar**, **Rotate → Restaurar en modo Sobrescritura**) modifican o borran definitivamente el contenido real de sus archivos de log — siempre precedidas de una confirmación explícita que detalla los archivos afectados, nunca desencadenadas automáticamente. En caso de duda, haga una copia de seguridad (**Rotate → Hacer copia de seguridad ahora**) antes de actuar.

## 2. Instalación

### Requisitos previos

- Python 3.10+
- Linux (probado en Arch/Manjaro, Debian/Ubuntu, RHEL/Fedora)
- `lnav` instalado en el sistema, únicamente para el visor de fusión multiarchivo (los otros dos visores funcionan normalmente sin él):

```bash
# Arch / Manjaro
sudo pacman -S lnav

# Debian / Ubuntu
sudo apt install lnav
```

### Instalación

```bash
[ -d omega-log ] && echo "ℹ️ Ya extraído aquí, paso omitido." || tar -xzf omega-log.tar.gz
cd omega-log/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Crea el entorno virtual `.venv` si no existe ya.
2. Instala las dependencias (primero `omega-lib` vendorizada si está presente, luego `pip install -e .` — `pyproject.toml` sigue siendo la única fuente de verdad).
3. Hace ejecutables `omega-log.sh` e `install.sh`.
4. Comprueba la presencia de `lnav` (aviso informativo si falta, nunca bloqueante).
5. Añade el alias `log` a `~/.bashrc` y `~/.zshrc` (sin duplicados si ya está presente).

### Dependencias

Declaradas en `pyproject.toml` (sin `requirements.txt` separado):
- `omega-lib`: biblioteca compartida de la suite (temas TUI + exportación, detección de terminal, almacenamiento de ajustes)
- `textual`: framework de la TUI
- `jinja2`: exportación HTML con tema (estadísticas, archivos)
- `pyte`: emulación de terminal para el visor `lnav` (renderizado dentro de un pty encapsulado)
- Dependencias de desarrollo (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `ruff`, `mypy`

## 3. Uso

### 3.1. Modo interactivo (TUI)

Recomendado para el uso diario — lanzado sin argumentos:

```bash
./omega-log.sh
```
si creó el alias, simplemente escriba `log` en una nueva terminal:
```bash
log
```

Recorrido general: pantalla de inicio → menú principal (dos columnas — Registro/Biblioteca/Ver logs/Favoritos/Ver y Procesar IP/Estadísticas por un lado, Rotate/Purgar/Exportar/Opciones/Ayuda/Salir por el otro) → la pantalla elegida → vuelta al menú (`Esc`). La ayuda completa integrada (`a`) detalla cada pantalla, cada visor y los conceptos transversales (elevación sudo puntual, estados de los logs, selección por número) — ver §4 para lo esencial.

#### Atajos de teclado

| Tecla | Acción |
|---|---|
| `↑` / `↓` | Navegar entre los elementos de una pantalla |
| `Tab` / `Mayús+Tab` | Navegar entre los campos de un formulario |
| `Esc` | Volver a la pantalla anterior (confirmación de salida en la pantalla de inicio) |
| `t` | Tema siguiente (aplicado inmediatamente, sin confirmación) |
| `r` | Actualizar la detección del terminal |
| `a` | Mostrar la ayuda (exhaustiva, un capítulo por pantalla) |
| `q` | Salir (con confirmación) |

### 3.2. Modo línea de comandos (CLI)

Limitado al escaneo de servicios por ahora (todavía no tiene paridad completa con la TUI — favoritos, rotate y purgado llegarán con sus propias fases, ver `plan_omega_log.md` §12):

```bash
# Detecta los servicios activos y sus logs conocidos
python -m omega_log scan

# + escaneo manual de una carpeta adicional
python -m omega_log scan --path /var/log
```

### 3.3. Variables de entorno

| Variable | Efecto |
|---|---|
| `OMEGA_LOG_VAR_DIR` | Cambia la ubicación de la carpeta de estado de la aplicación (`./var` por defecto, relativa a la carpeta de lanzamiento) |

## 4. Funcionalidades

| Pantalla | Descripción |
|---|---|
| **Registro de capacidades** | Detecta los servicios activos en la máquina y ofrece importar sus logs conocidos, en detalle o por completo. Escaneo manual de carpeta disponible además. |
| **Biblioteca** | Centro central que referencia todos los logs a procesar — alimentada por el Registro o por importación manual. |
| **Ver logs** | Selección de uno o varios logs de la Biblioteca + elección del visor (1 log → los 3 visores; 2+ logs → solo `lnav`). |
| **Favoritos** | Combinaciones de log(s) + visor guardadas con un nombre, para un lanzamiento directo. |
| **Ver y Procesar IP** | Top 10 de IP por período (24h/7d/30d/todo) y eliminación selectiva de una IP de uno o varios logs. |
| **Estadísticas (acceso)** | Volumen, IPs únicas, tasa de error, top de IP, distribución horaria — exportación JSON/HTML con 5 temas. |
| **Rotate** | Copia de seguridad comprimida de un log + retención automática de los archivos excedentes + restauración (fusión o sobrescritura, con copia de seguridad previa). |
| **Purgar** | Vacía el contenido de un log (truncado in situ, seguro para un servicio que aún lo tiene abierto) o elimina completamente uno o varios archivos — siempre con confirmación. |
| **Exportar** | Exportación de la lista de archivos (Rotate) en JSON o HTML con tema. |
| **Opciones** | Tema, perfil de renderizado, purga de las carpetas de la aplicación (exports/screenshots). |

### Los 3 visores

1. **Simple** — seguimiento en vivo con análisis genérico (marca de tiempo, IP, nivel, servicio) y un pequeño panel de estadísticas. Para un log de acceso HTTP reconocido, aparecen columnas adicionales de código HTTP / latencia, coloreadas según el umbral.
2. **Clásico** — lee las últimas líneas en bruto + un interruptor "Seguir en vivo", sin análisis: la opción más simple y fiable sea cual sea el formato.
3. **lnav** — fusiona varios archivos dentro de una terminal encapsulada (pty), para un análisis cruzado. Ciclo de tema (`t`), marcar + copiar al portapapeles (`Ctrl+C`, OSC 52), salir (`Ctrl+Q`) — todos interceptados antes de llegar al propio `lnav`.

## 5. Compatibilidad de terminales

La TUI (Textual) detecta automáticamente las capacidades del terminal (emulador, tamaño) y adapta en consecuencia su hoja de estilo estructural (`complete`/`standard`/`reduced`/`mono`), sin necesidad de ninguna opción manual — la misma política compartida por toda la suite `omega-` (`omega-lib`, `terminal/policies.py`). Actualizable en vivo con la tecla `r`.

### Perfil según el emulador detectado

| Emulador | Perfil inicial |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderno | `reduced` |
| TTY Linux, SSH antiguo | `mono` |
| Emulador no reconocido | `reduced` (repliegue por defecto) |

### Perfil según el tamaño del terminal

| Tamaño mínimo (columnas × filas) | Techo de perfil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| por debajo | `mono` |

El perfil final utilizado es **el más restrictivo de los dos** (emulador y tamaño).

## 6. Arquitectura

Clean Architecture (domain / application / infrastructure / interfaces), la misma convención que el resto de la suite OMEGA:

```text
src/omega_log/
├── core/            Registro de capacidades (deteccion de servicios)
├── domain/          Logica de negocio pura (parsing, estadisticas, rotacion, purga)
├── ports/           Contratos (Protocol)
├── application/     Casos de uso
├── infrastructure/  Implementaciones reales (sondas, almacenamiento, archivos, exportacion, lnav, concurrencia)
├── interfaces/      TUI (Textual) + CLI
└── app/             Raiz de composicion
```

Depende de [`omega-lib`](../LIB/omega-lib) para los temas (10 temas TUI + 5 temas de exportación), la detección de terminal y el almacenamiento de ajustes — la misma base que el resto de la suite. Los cálculos pesados (top IP, estadísticas de acceso) se ejecutan en un `ProcessPoolExecutor` dedicado (`infrastructure/concurrency/`), nunca en el hilo de la interfaz, para seguir siendo reactivo incluso en un archivo de varios cientos de miles de líneas.

## 7. Pruebas

```bash
source .venv/bin/activate
pytest tests/ -q      # 171 pruebas
ruff check .
mypy src
```

Estructura: `tests/unit/` (dominio y aplicación, sin E/S real), `tests/integration/` (archivos reales, TUI sin interfaz vía la API `Pilot` de Textual).

## 8. Estado del desarrollo

Las 10 fases del plan de desarrollo están terminadas: base, dominio, TUI básica, visores, favoritos/biblioteca/IP, mantenimiento, estadísticas/exportación, finalización, elevación sudo puntual, cálculos intensivos en CPU delegados a un proceso separado — ver `plan_omega_log.md` para el detalle de cada decisión de porting.

## 9. Licencia

MIT — ver [LICENSE](LICENSE).

---

> Omega-log — Detectar, centralizar, leer, analizar, mantener.
> Sus logs siguen siendo suyos: ninguna elevación de privilegios sin necesidad real, ninguna acción destructiva sin confirmación.
