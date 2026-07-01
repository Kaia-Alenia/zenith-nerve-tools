<div align="center">

<img src="assets/logo.png" alt="Zenith Nerve Tools Logo" width="600">

# Zenith Nerve Tools (Alenia Apps)

**Welcome to the official Zenith Nerve Tools monorepo by Alenia Studios! This repository houses our powerful and lightweight media editing and processing tools.**

*Read this in other languages: [🇬🇧 English](README.md) | [🇪🇸 Español](README.es.md)*

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

The architecture of this repository follows modern Python Packaging (PyPA) guidelines in a **Monorepo** environment, where native applications coexist and interact thanks to a shared core (`alenia_bridge`).

---

## Core Open-Source Libraries

The magic of our ecosystem is powered by two robust, open-source libraries we developed. Feel free to explore and use them:

- **[Alenia Zenith](https://github.com/Kaia-Alenia/alenia-zenith)**: The visual foundation. Handles beautiful, high-performance UI rendering and graphical integrations.
- **[Alenia Nerve](https://github.com/Kaia-Alenia/alenia-nerve)**: The brain of our IPC (Inter-Process Communication). Enables real-time, low-latency socket communication between standalone tools.

---

## Suite Tools

Our suite consists of minimalist, high-performance tools developed in Python and natively compiled.

### 1. Framegrid (FG.SLICER)
**Framegrid** is a precision spritesheet slicer. It is specifically designed to take large texture sheets (spritesheets) from video games or animations and extract each "frame" automatically.
- **What it does**: Reads individual images or entire directories and mathematically slices them based on a custom Width and Height block.
- **Use cases**: Separating the frames of a walking character (e.g., slicing a 256x256 spritesheet into sixteen 64x64 images).
- **Efficiency**: Processes multiple images using precise calculations without quality loss.

### 2. Giftly
**Giftly** is an animation assembly engine. It takes individual frames (or an instantly sliced spritesheet) and converts them into fluid, optimized `.gif` files.
- **What it does**: Generates and previews animations, providing full control over artistic parameters such as Frames Per Second (FPS), Scale factor (for pixel art), and Background Color (supports alpha masks and true transparency).
- **Features**: Can process files in batches, and resizes frames (using ideal `NEAREST` sampling for pixel-art) to export flawless visuals.

---

## Nerve: The Intercommunication Bridge



The true magic behind the Alenia suite is **Nerve**, an Inter-Process Communication (IPC) protocol living at the core of our local `alenia-bridge` library.

### How does Nerve work?
In traditional software ecosystems, tools are isolated. Nerve breaks that barrier by creating a local network architecture that connects all our applications simultaneously.
1. **NexusHub**: When you toggle "Nerve" in any suite tool, it spins up (or connects to) an underlying socket coordinator. It uses **local TCP/IP (Port 50505)** on Windows or a blazing fast **UNIX Socket (`/tmp/nerve.sock`)** on Linux/macOS.
2. **NexusClient**: Each opened application acts as a client to the Nexus, sending and receiving events in real time.

### The Connected Workflow
When using the ecosystem and toggling the **Nerve Switch** in the UI:
- Suppose you just exported hundreds of visual frames in **Framegrid**.
- Once finished, **Framegrid** sends a message (`batch_ready`) over the Nerve channel containing the dimensions and the path of the extracted files.
- **Giftly**, which is open in the background, receives the event in real time via `alenia_bridge`, automatically loads the paths into its interface without the user opening a file explorer, and calibrates the dimensions (X/Y) so it is instantly ready to assemble the animations.

The entire creation process becomes a frictionless ecosystem, completely removing the need to manually drag and drop files.

---

## Architecture & Compilation

The project uses a **local editable install** system to share clean logic, and native automated packaging via Nuitka.

### Local Development Environment
To work in the monorepo and run the tools without import errors:
```bash
# 1. Install the shared library in editable mode
# (This registers `alenia_bridge` globally in your environment without uploading it to the internet)
pip install -e ./libs/alenia_bridge

# 2. Install any tool's dependencies and launch
pip install -r tools/framegrid/requirements.txt
python tools/framegrid/src/main.py
```

### CI/CD with GitHub Actions
The repository features a master workflow at `.github/workflows/build.yml`.
- Upon pushing a version *tag* (e.g., `v1.1`), GitHub Actions pulls the code and independently triggers the process matrix for **Ubuntu, Windows, and macOS**.
- It uses **Nuitka** with bundled packages and *assets* (`--include-package=alenia_bridge`) to compile a single, blazing fast C++ binary free of dependencies.
- The `Releases` are automatically published with the ZIP of each platform, ready for the end consumer.

---

## License

This project is licensed under the **GNU General Public License v3 (GPL v3)**. See the `LICENSE` file for more information.

For business inquiries, please contact: **contact.aleniastudios@gmail.com**
