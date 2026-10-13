# Warehouse Vision Counting System

**Idiomas:** [العربية](../README.md) · [English](README.en.md) · [Français](README.fr.md) · [Español](README.es.md) · [Türkçe](README.tr.md) · [中文](README.zh-CN.md)

Núcleo local y auditable para contar cajas y palés que cruzan una línea en un
almacén. El MVP convierte observaciones rastreadas en eventos direccionales
`IN/OUT`, evita duplicados y guarda metadatos de evidencia en SQLite.

## Inicio rápido

```bash
python3 -m pytest -q
PYTHONPATH=src python3 -m warehouse_counting.demo
```

El núcleo requiere Python 3.11+ y la biblioteca estándar. La entrada de cámara,
los paneles y la validación de precisión en producción están en la hoja de ruta.

## Alcance actual

Una línea de conteo, objetos `carton` y `pallet`, filtrado por confianza,
prevención de duplicados, almacenamiento SQLite y reglas explícitas para la
capacidad de los palés. Los vídeos actuales son material suplementario, no un
benchmark de aceptación.

## Únete a la comunidad

Invitamos a desarrolladores, investigadores, especialistas de almacenes y
traductores a contribuir. Lee [`CONTRIBUTING.md`](../CONTRIBUTING.md), abre una
Issue y envía Pull Requests pequeñas, claras y probadas.

## Licencia

MIT — consulta [`LICENSE`](../LICENSE).
