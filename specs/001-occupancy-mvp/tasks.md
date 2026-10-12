# Tareas de implementación: cálculo de aforo máximo

Las tareas están ordenadas por dependencia. Cada una está dimensionada para
completarse en un máximo de 20–30 minutos. La implementación debe conservar el
alcance del plan: función Python pura, biblioteca estándar para el algoritmo,
sin CLI ni interfaces externas. Toda documentación técnica del producto
(`README.md` y `ANALYSIS.md`) se redactará en inglés.

## Tareas

- [x] **T001 — Acordar la representación del error de validación** (20 min)
  **RF:** RF-5.  
  **Depende de:** ninguna.  
  Definir con la persona responsable la clase de excepción y cómo el mensaje
  identificará la reserva inválida y el motivo, sin ampliar los formatos de
  entrada admitidos. Es un bloqueo para implementar y probar errores.  
  **Hecho cuando:** la decisión está confirmada y registrada de forma consultable
  para implementar las pruebas de RF-5.
  **Decisión confirmada:** usar `InvalidBookingError`, subclase de
  `ValueError`, con el formato inglés
  `Invalid booking at index {index} ({booking!r}): {reason}`; el índice es
  base cero y el motivo describe brevemente la regla incumplida.

- [x] **T002 — Crear la función pública y cubrir la entrada vacía** (25 min)
  **RF:** RF-1, RF-3, RF-4.  
  **Depende de:** ninguna.  
  Crear `occupancy.py` con la firma pública especificada y agregar
  `tests/test_occupancy.py`; implementar y probar el resultado para una lista
  vacía.  
  **Hecho cuando:** la llamada con `[]` devuelve exactamente
  `(0, None, None)` y las pruebas enfocadas pasan.

- [x] **T003 — Validar la forma y el orden de cada reserva** (30 min)
  **RF:** RF-5.  
  **Depende de:** T001, T002.  
  Rechazar reservas que no contengan exactamente dos extremos y aquellas cuyo
  inicio sea igual o posterior al fin. Agregar pruebas para ambos casos,
  comprobando la excepción y los detalles acordados en T001.  
  **Hecho cuando:** cada entrada inválida produce el error acordado, identifica
  la reserva y su motivo, y las pruebas enfocadas pasan.

- [x] **T004 — Validar extremos enteros y rechazar booleanos** (25 min)
  **RF:** RF-5, RF-8.  
  **Depende de:** T001, T003.  
  Rechazar extremos que no sean enteros y excluir explícitamente valores
  booleanos. Probar valores no enteros y booleanos tanto en inicio como en fin.  
  **Hecho cuando:** las pruebas confirman que los enteros se admiten, los
  booleanos y otros tipos no enteros se rechazan con el error acordado, y pasan.

- [x] **T005 — Aceptar instantes negativos válidos** (20 min)
  **RF:** RF-5, RF-9.  
  **Depende de:** T003, T004.  
  Agregar pruebas de reservas con inicio negativo, fin negativo y extremos a
  ambos lados de cero; no imponer reglas de negocio sobre rangos horarios.  
  **Hecho cuando:** las reservas negativas con `inicio < fin` se aceptan y las
  pruebas enfocadas pasan.

- [x] **T006 — Construir y ordenar los eventos del barrido** (25 min)\
  **RF:** RF-2, RF-6.  
  **Depende de:** T003, T004.  
  Generar eventos de inicio y fin por cada reserva y ordenarlos por instante,
  colocando los inicios antes que los finales cuando coincidan. Cubrir
  coincidencia de inicios, de finales y de inicios con finales en el mismo
  instante.  
  **Hecho cuando:** las pruebas verifican la semántica `[inicio, fin)`, el
  orden determinista y que no se cuentan estados de duración cero.

- [x] **T007 — Calcular el máximo de reservas concurrentes** (25 min)  
  **RF:** RF-1, RF-2, RF-6.  
  **Depende de:** T006.  
  Recorrer los instantes distintos, aplicar todos sus eventos antes de medir el
  intervalo siguiente y calcular la concurrencia máxima para intervalos
  semiabiertos `[inicio, fin)`.  
  **Hecho cuando:** pruebas de una reserva, solapamientos y reservas
  consecutivas devuelven la concurrencia esperada y pasan.

- [x] **T008 — Devolver el primer período de máximo aforo** (30 min)  
  **RF:** RF-1, RF-3.  
  **Depende de:** T007.  
  Registrar el comienzo y fin del primer período del máximo global; extenderlo
  si el máximo continúa a través de un cambio de instante y conservar el
  primero cuando haya períodos máximos separados.  
  **Hecho cuando:** pruebas de máximo sostenido y de máximos separados iguales
  verifican los límites del primer período y pasan.

- [x] **T009 — Contar las reservas duplicadas de forma independiente** (20 min)  
  **RF:** RF-1, RF-7.  
  **Depende de:** T007.  
  Agregar pruebas con reservas idénticas repetidas y comprobar que ninguna se
  elimina ni se fusiona automáticamente.  
  **Hecho cuando:** cada duplicado incrementa la concurrencia según corresponda
  y las pruebas enfocadas pasan.

- [x] **T010 — Verificar el rechazo completo de listas inválidas** (25 min)  
  **RF:** RF-5, RF-8.  
  **Depende de:** T003, T004, T007.  
  Probar listas que mezclen reservas válidas e inválidas y confirmar que la
  validación ocurre antes de producir un resultado parcial.  
  **Hecho cuando:** cualquier reserva inválida hace fallar la llamada con el
  error acordado y la prueba confirma que no se devuelve un resultado parcial.

- [x] **T011 — Verificar determinismo y conservación de la entrada**
  **RF:** RF-1, RF-3, RF-6.  
  **Depende de:** T006, T008.  
  Agregar pruebas que repitan la misma entrada y que comprueben que el cálculo
  no modifica la lista ni sus reservas.  
  **Hecho cuando:** las llamadas repetidas devuelven el mismo resultado, la
  entrada permanece intacta y las pruebas enfocadas pasan.

- [x] **T012 — Documentar el contrato y los fundamentos en README** (30 min)  
  **RF:** RF-1–RF-9.  
  **Depende de:** T002, T003, T007, T008.  
  Actualizar `README.md` en inglés y que no te lleve más de cinco minutos: 
  cómo instalar y ejecutar, cómo lanzar los tests, y prepara un apartado par colocar el enlace a un vídeo.  
  **Hecho cuando:** el README documenta lo neceasario.

- [x] **T013 — Documentar algoritmo, complejidad y casos límite** (30 min)
  **RF:** RF-1–RF-9.  
  **Depende de:** T003–T011.  
  Crear `ANALYSIS.md` en inglés con el barrido de eventos, la complejidad
  temporal y espacial, las decisiones de diseño y el análisis de los casos
  límite definidos en la especificación.  
  **Hecho cuando:** el documento explica `O(n log n)` de tiempo, `O(n)` de
  espacio y cubre los nueve requisitos sin introducir umbrales de rendimiento.

- [x] **T014 — Ejecutar la verificación final de la suite** (20 min)  
  **RF:** RF-1–RF-9.  
  **Depende de:** T002–T013.  
  Ejecutar la suite completa del proyecto y corregir cualquier regresión
  relacionada con estas tareas antes de dar por terminada la implementación.  
  **Hecho cuando:** `pytest -q` termina con código de salida cero y todas las
  pruebas pasan.
