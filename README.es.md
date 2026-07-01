<div align="center">

<img src="assets/logo.png" alt="Zenith Nerve Tools Logo" width="600">

# Zenith Nerve Tools (Alenia Apps)

**¡Bienvenido al monorepo oficial de Zenith Nerve Tools de Alenia Studios! Este repositorio alberga nuestras potentes y ligeras herramientas de edición y procesamiento de medios interactivos.**

*Leer en otros idiomas: [🇬🇧 English](README.md) | [🇪🇸 Español](README.es.md)*

[![GitGem](https://gitgem.org/api/badge/github/Kaia-Alenia/zenith-nerve-tools.svg)](https://gitgem.org/github/Kaia-Alenia/zenith-nerve-tools)
[![Build Status](https://github.com/Kaia-Alenia/zenith-nerve-tools/actions/workflows/build.yml/badge.svg)](https://github.com/Kaia-Alenia/zenith-nerve-tools/actions)
[![GitHub Release](https://img.shields.io/github/v/release/Kaia-Alenia/zenith-nerve-tools?color=blue)](https://github.com/Kaia-Alenia/zenith-nerve-tools/releases)
[![Downloads](https://img.shields.io/github/downloads/Kaia-Alenia/zenith-nerve-tools/total?color=blue)](https://github.com/Kaia-Alenia/zenith-nerve-tools/releases)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)](https://www.python.org/)

[![Patreon](https://img.shields.io/badge/Patreon-alenia__studios-F96854?logo=patreon&logoColor=white)](https://www.patreon.com/alenia_studios)
[![Ko-Fi](https://img.shields.io/badge/Ko--Fi-alenia__studios-F16061?logo=ko-fi&logoColor=white)](https://ko-fi.com/alenia_studios)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/ncp/payment/TCCYMCFSVMV8E)
[![Itch.io](https://img.shields.io/badge/Itch.io-Alenia_Studios-FA5C5C?logo=itch.io&logoColor=white)](https://alenia-studios.itch.io/)

<br/>

</div>

La arquitectura de este repositorio ha sido estructurada siguiendo las directrices modernas de empaquetado de Python (PyPA) en modo **Monorepo**, donde las aplicaciones nativas conviven e interactúan gracias a un núcleo compartido (`alenia_bridge`).

---

## Librerías Core Open-Source

La magia de nuestro ecosistema es impulsada por dos robustas librerías open-source que hemos desarrollado. Siéntete libre de explorarlas y utilizarlas:

- **[Alenia Zenith](https://github.com/Kaia-Alenia/alenia-zenith)**: La base visual. Maneja componentes de UI modernos, integraciones gráficas y de alto rendimiento.
- **[Alenia Nerve](https://github.com/Kaia-Alenia/alenia-nerve)**: El cerebro de nuestro IPC. Permite una comunicación ultra rápida de baja latencia por sockets entre herramientas independientes.

---

## Herramientas de la Suite

Nuestra suite está compuesta por herramientas minimalistas y de alto rendimiento desarrolladas en Python y compiladas nativamente. 

### 1. Framegrid (FG.SLICER)
**Framegrid** es un cortador de spritesheets de precisión. Está diseñado específicamente para tomar grandes hojas de texturas (spritesheets) de videojuegos o animaciones y extraer cada "fotograma" de forma automatizada.
- **¿Qué hace?** Lee imágenes individuales o directorios completos y los "rebana" (slice) matemáticamente basándose en un bloque de anchura (Width) y altura (Height) personalizados.
- **Casos de uso**: Separar los cuadros de un personaje caminando (e.g. un spritesheet de 256x256 en 16 imágenes de 64x64).
- **Eficiencia**: Procesa múltiples imágenes usando cálculos precisos sin pérdida de calidad.

### 2. Giftly
**Giftly** es un motor de ensamblaje de animaciones. Toma fotogramas individuales (o un spritesheet que corta en el momento) y los convierte en archivos `.gif` fluidos y optimizados.
- **¿Qué hace?** Genera y previsualiza animaciones proporcionando un control total sobre parámetros artísticos como Fotogramas por Segundo (FPS), factor de Escala (para pixel art) y el Color de Fondo (soporta máscaras alfa y transparencias verdaderas).
- **Características**: Puede procesar archivos en lote, y redimensiona (mediante un muestreo `NEAREST` ideal para pixel-art) los cuadros para exportar visuales impecables.

---

## Nerve: El puente de Intercomunicación



La verdadera magia detrás de la suite de Alenia es **Nerve**, un protocolo de comunicación entre procesos (IPC) que vive en el corazón de nuestra librería local `alenia-bridge`. 

### ¿Cómo funciona Nerve?
En sistemas de software tradicionales, las herramientas están aisladas. Nerve rompe esa barrera creando una arquitectura local en red que conecta todas nuestras aplicaciones simultáneamente.
1. **NexusHub**: Cuando activas "Nerve" en cualquier herramienta de la suite, esta levanta (o se conecta a) un coordinador de sockets subyacente. Usa **TCP/IP local (Puerto 50505)** en Windows o un **Socket UNIX (`/tmp/nerve.sock`)** extremadamente rápido en Linux/macOS.
2. **NexusClient**: Cada aplicación abierta actúa como un cliente del Nexus, enviando y recibiendo eventos en tiempo real. 

### El Flujo Conectado (Workflow)
Al usar el ecosistema activando el **Nerve Switch** en la interfaz gráfica:
- Supongamos que acabas de exportar cientos de recuadros visuales en **Framegrid**. 
- Una vez finaliza, **Framegrid** manda por el canal Nerve un mensaje (`batch_ready`) con las dimensiones y la ruta de los archivos extraídos.
- **Giftly**, que está abierto en segundo plano, recibe el evento en tiempo real mediante `alenia_bridge`, carga automáticamente las rutas en su interfaz sin que el usuario tenga que abrir un explorador de archivos, y calibra las dimensiones (X/Y) para estar inmediatamente listo para ensamblar las animaciones.

Todo el proceso de creación se vuelve un ecosistema sin interrupciones ni arrastre manual de ficheros. 

---

## Arquitectura y Compilación

El proyecto utiliza un sistema de **instalaciones editables local** para compartir lógica limpia, y empaquetamiento automatizado nativo vía Nuitka.

### Entorno de Desarrollo Local
Para trabajar en el monorepo y poder ejecutar las herramientas sin errores de importe:
```bash
# 1. Instala la librería compartida en modo editable 
# (Esto registra `alenia_bridge` globalmente en tu entorno sin subirlo a internet)
pip install -e ./libs/alenia_bridge

# 2. Instalar dependencias de cualquier herramienta e iniciar
pip install -r tools/framegrid/requirements.txt
python tools/framegrid/src/main.py
```

### CI/CD con GitHub Actions
El repositorio cuenta con un flujo de trabajo maestro en `.github/workflows/build.yml`.
- Al empujar (push) un *tag* de versión (ej. `v1.1`), GitHub Actions toma el código y de forma independiente dispara en la matriz el proceso para **Ubuntu, Windows y macOS**.
- Utiliza **Nuitka** con los paquetes y *assets* empaquetados (`--include-package=alenia_bridge`) para compilar un único binario súper rápido (C++) libre de dependencias.
- Las `Releases` se publican automáticamente con el ZIP de cada plataforma, listas para el consumidor final.

---

## Licencia

Este proyecto está licenciado bajo la **GNU General Public License v3 (GPL v3)**. Consulta el archivo `LICENSE` para más información.

Para consultas empresariales, contacta a: **contact.aleniastudios@gmail.com**
