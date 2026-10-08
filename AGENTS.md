# AGENTS.md — room-booking-occupancy

## Proyecto
Núcleo algorítmico en Python diseñado para calcular el aforo máximo concurrente de
reservas de salas (`max_occupancy`), optimizado para escalar bajo picos masivos 
de tráfico en producción. Arquitectura de función pura basada en la biblioteca estándar.

## Comandos
- Ejecutar: `python -m occupancy` (o mediante la suite de pruebas)
- Tests: `pytest -q`
- Lint/formato: `ruff check .` (o herramienta estándar de linting del entorno)

## Estilo y convenciones
- Python 3.12+, type hints obligatorios en todas las funciones públicas.
- Solo biblioteca estándar (pytest únicamente para tests).
- Identificadores, comentarios, código, README y ANALYSIS estrictamente en inglés. Mensajes de error/usuario (si aplica) en inglés.

## Reglas
- Lee `docs/constitution.md` y la spec activa en `specs/` antes de tocar código.
- Entregar la solución más eficiente (complejidad óptima para grandes volúmenes de datos reales).
- Incluir la suite completa de tests (casos del enunciado + casos límite propios).
- No modificar la firma de retorno: `max_occupancy(bookings: list[tuple[int, int]]) -> tuple[int, int | None, int | None]`.
- No modifiques archivos dentro de `specs/` salvo petición explícita.

## Al terminar cualquier tarea
- Ejecuta `pytest -q` y confirma en tu respuesta que todo pasa.