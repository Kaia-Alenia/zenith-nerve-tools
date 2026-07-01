# Changelog

Todos los cambios notables en el proyecto "Nerve Media Suite" serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/), y este proyecto adhiere al [Versionado Semántico](https://semver.org/lang/es/).

## [Unreleased]

## [v1.1.0] - 2026-07-01

### Agregado
- Implementación oficial de la arquitectura Monorepo (Nerve Media Suite).
- Creación de `alenia_bridge` como paquete local instalable (`pyproject.toml`) reemplazando los hacks de manipulación de `sys.path`.
- Despliegue de GitHub Actions (CI/CD) unificado para compilar ambas aplicaciones (`framegrid` y `giftly-lite`) para Windows, macOS y Linux.
- Archivo de documentación README actualizado con descripciones técnicas a fondo de cada herramienta y el mecanismo interno de Nerve (IPC).

### Modificado
- Los importes en `framegrid` y `giftly-lite` ahora utilizan importación estándar vía `libs/alenia_bridge`.
- Consolidación de archivos Markdown en la raíz del repositorio (`README.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`).
- Flujo de GitHub Actions modificado para compilar con la bandera `--include-package=alenia_bridge` de Nuitka asegurando la inclusión completa del motor.

### Eliminado
- Se eliminaron todos los flujos de trabajo duplicados y archivos `.md` de las carpetas interiores.
