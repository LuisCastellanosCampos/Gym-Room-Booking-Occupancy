# Tareas de implementación: optimización del cálculo de aforo

Las tareas están ordenadas por dependencia y dimensionadas para completarse en
un máximo de 20–30 minutos cada una. El alcance se limita a los requisitos de
`spec.md`; se conservarán el contrato público y las reglas vigentes. El
algoritmo continuará usando únicamente la biblioteca estándar. La documentación
técnica del producto (`README.md` y `ANALYSIS.md`) se redactará en inglés.

## Tareas

- [x] **T001 — Caracterizar el comportamiento vigente** (20 min)  
  **RF:** RF-3.  
  **Depende de:** ninguna.  
  Revisar las pruebas existentes y registrar los resultados, los errores exactos,
  el orden de selección de errores, la semántica de intervalos, el desempate y
  las garantías de determinismo e inmutabilidad que deberán conservarse.  
  **Hecho cuando:** existe una lista verificable de comportamientos vigentes y
  sus pruebas de referencia para usar durante el cambio.

- [x] **T002 — Validar reservas al extraer eventos** (30 min)  
  **RF:** RF-1, RF-3.  
  **Depende de:** T001.  
  Unificar la validación de cada reserva y la obtención de sus eventos de inicio
  y fin en una única visita a esa reserva. Conservar el rechazo completo de
  entradas inválidas, sin resultado parcial y con el primer error según el orden
  de entrada.  
  **Hecho cuando:** pruebas y revisión del flujo confirman que cada reserva se
  valida durante la extracción de eventos, no hay un recorrido posterior de
  validación y se conserva el primer error vigente.

- [ ] **T003 — Representar eventos con etiquetas enteras** (25 min)  
  **RF:** RF-2, RF-3.  
  **Depende de:** T002.  
  Sustituir las etiquetas textuales de inicio y fin por etiquetas enteras.
  Mantener explícitamente el orden de inicios antes que finales en un mismo
  instante, independientemente de los enteros elegidos.  
  **Hecho cuando:** las pruebas verifican etiquetas enteras, orden inicio-antes-
  que-fin en instantes coincidentes y ausencia de cambios en el resultado
  público.

- [ ] **T004 — Verificar compatibilidad y casos límite** (30 min)  
  **RF:** RF-1, RF-2, RF-3.  
  **Depende de:** T002, T003.  
  Ejecutar y, cuando sea necesario, adaptar pruebas de regresión para entrada
  vacía, reservas válidas e inválidas, duplicados, extremos negativos, eventos
  coincidentes, máximos sostenidos y separados, determinismo y conservación de
  la entrada.  
  **Hecho cuando:** las pruebas confirman que esos casos mantienen el
  comportamiento especificado y que las entradas inválidas no producen
  resultados parciales.

- [ ] **T005 — Actualizar la documentación de uso** (25 min)  
  **RF:** RF-1, RF-2, RF-3.  
  **Depende de:** T004.  
  Actualizar `README.md` en inglés para explicar el contrato vigente y describir
  las dos mejoras sin prometer interfaces ni umbrales numéricos que no formen
  parte del alcance.  
  **Hecho cuando:** el README describe el resultado, la validación y las reglas
  relevantes, además del recorrido único y las etiquetas enteras, sin
  contradicciones con `spec.md`.

- [ ] **T006 — Documentar decisiones y complejidad** (30 min)  
  **RF:** RF-1, RF-2, RF-3.  
  **Depende de:** T004.  
  Actualizar `ANALYSIS.md` en inglés con la justificación de las decisiones, el
  análisis de los casos límite y la complejidad temporal `O(n log n)` y espacial
  `O(n)`. No introducir benchmarks ni umbrales no acordados.  
  **Hecho cuando:** el análisis explica ambas optimizaciones, demuestra cómo se
  conserva el orden de eventos y documenta las complejidades y casos límite
  definidos.

- [ ] **T007 — Ejecutar la verificación final** (20 min)  
  **RF:** RF-1, RF-2, RF-3.  
  **Depende de:** T004, T005, T006.  
  Ejecutar la suite completa y revisar que la implementación y la documentación
  final cumplen los requisitos de esta especificación y las restricciones
  aplicables de la constitución.  
  **Hecho cuando:** `pytest -q` termina con código de salida cero y la revisión
  confirma un único recorrido de validación y extracción, etiquetas enteras,
  orden correcto de eventos y ausencia de cambios funcionales no especificados.
