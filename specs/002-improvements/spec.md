# Especificación: optimización del cálculo de aforo

## Contexto y objetivo

La primera funcionalidad calcula el aforo máximo concurrente y el primer
intervalo en que se alcanza. Para cada reserva, el cálculo necesita validar sus
datos y obtener los eventos de inicio y fin. Hacer esas operaciones en
recorridos separados repite trabajo; además, las etiquetas de texto de los
eventos consumen memoria y requieren comparaciones de cadenas durante su
ordenamiento.

El objetivo de esta mejora es reducir trabajo y memoria asociados a esas
operaciones sin cambiar ningún comportamiento observable de la funcionalidad
existente. Cada reserva deberá validarse mientras se obtienen sus dos eventos, y
los eventos deberán usar etiquetas enteras en lugar de etiquetas de texto. La
codificación elegida deberá conservar el orden y la semántica ya establecidos.

## Usuarios

- La persona que integra el cálculo y necesita conservar resultados y errores
  previsibles mientras aumenta el volumen de reservas.
- La persona que mantiene el cálculo y necesita reducir trabajo y memoria
  innecesarios sin alterar las reglas existentes.

## Historias de usuario

- Como persona que integra el cálculo, quiero que la mejora conserve los
  resultados, errores y reglas vigentes para no tener que adaptar a sus
  consumidores.
- Como persona que mantiene el cálculo, quiero validar cada reserva mientras
  se obtienen sus eventos para evitar un recorrido separado de validación.
- Como persona que mantiene el cálculo, quiero que las etiquetas de los eventos
  sean enteras para evitar almacenar y comparar etiquetas de texto.

## Requisitos funcionales

### RF-1: Validar y obtener eventos en un único recorrido

El sistema deberá validar cada reserva y obtener sus eventos de inicio y fin
dentro del mismo recorrido de entrada.

**Criterios de aceptación (EARS):**

- Cuando el sistema procese una reserva válida, deberá comprobar su forma, sus
  extremos y su orden, y obtener sus dos eventos durante la misma visita a esa
  reserva.
- Cuando haya procesado todas las reservas, no deberá realizar un recorrido
  separado de la lista para validar reservas ya procesadas.
- Cuando encuentre una reserva inválida, deberá rechazar la entrada completa y
  no deberá devolver un resultado parcial.
- Cuando la entrada esté vacía, deberá conservar el resultado vacío vigente:
  `(0, None, None)`.

### RF-2: Usar etiquetas enteras para los eventos

El sistema deberá representar con valores enteros las etiquetas que distinguen
los eventos de inicio y fin, en lugar de representarlas con texto. La elección
concreta de los valores enteros no forma parte del contrato, pero su uso no
deberá alterar el orden de procesamiento requerido ni exponerse en el resultado
del cálculo.

**Criterios de aceptación (EARS):**

- Cuando el sistema obtenga un evento de inicio o de fin, deberá distinguirlo
  mediante una etiqueta entera y no mediante una etiqueta de texto.
- Cuando varios eventos correspondan al mismo instante, el sistema deberá
  procesar los inicios antes que los finales, independientemente de los valores
  enteros elegidos para sus etiquetas.
- Cuando el sistema devuelva un resultado, este deberá mantener el formato
  público vigente y no incluir las etiquetas internas de los eventos.

### RF-3: Conservar el contrato funcional vigente

El sistema deberá conservar el comportamiento funcional ya acordado para el
cálculo de aforo.

**Criterios de aceptación (EARS):**

- Cuando reciba una entrada válida no vacía, deberá devolver el aforo máximo y
  el primer intervalo cronológico continuo en que se alcanza ese máximo.
- Cuando una reserva termine en el instante en que otra comience, no deberá
  contarlas como solapadas en ese instante.
- Cuando el máximo se mantenga a través de un cambio de instante sin caer por
  debajo de él, deberá informar un único intervalo continuo.
- Cuando haya varios intervalos separados con el mismo máximo global, deberá
  informar el primero en orden cronológico.
- Cuando haya reservas duplicadas, cada entrada deberá contribuir
  independientemente al aforo.
- Cuando los extremos de una reserva sean enteros y el inicio sea menor que el
  fin, deberá aceptar también extremos negativos.
- Cuando una reserva tenga extremos no enteros o booleanos, no contenga
  exactamente dos extremos, o tenga un inicio igual o posterior al fin, deberá
  rechazar la entrada completa.
- Cuando la entrada contenga reservas inválidas, deberá señalar la primera
  reserva inválida en orden de entrada, con índice base cero y el formato de
  mensaje vigente: `Invalid booking at index {index} ({booking!r}): {reason}`.
- Cuando calcule el resultado, no deberá modificar la entrada ni sus reservas.
- Cuando se repita una misma entrada, deberá producir siempre el mismo
  resultado.

## Requisitos no funcionales

- **Eficiencia de CPU:** la validación y la obtención de eventos deberán
  compartir un recorrido de la entrada para evitar el trabajo de volver a
  recorrer las reservas con el propósito de validarlas.
- **Eficiencia de memoria:** las etiquetas de los eventos deberán ser enteras y
  no cadenas de texto.
- **Complejidad:** la mejora deberá mantener el orden de crecimiento vigente
  para el cálculo: tiempo `O(n log n)` y memoria `O(n)`, donde `n` es la cantidad
  de reservas.
- **Compatibilidad:** los cambios no deberán modificar resultados, errores,
  reglas de desempate ni la entrada recibida.
- **Medición:** no se establece un umbral numérico de latencia, consumo de
  memoria o cantidad máxima de reservas.

## Casos límite

- Entrada vacía: devolver `(0, None, None)`.
- Una reserva válida: aforo máximo de uno durante su intervalo.
- Reservas consecutivas cuyo fin y comienzo coinciden: no se solapan.
- Varios inicios o varios finales en un mismo instante: aplicar el orden
  determinista vigente.
- Inicios y finales coincidentes: procesar primero los inicios y conservar la
  semántica de intervalos semiabiertos `[inicio, fin)`.
- Máximo sostenido a través de varios instantes de cambio: informar un único
  intervalo.
- Varios intervalos separados con el mismo máximo: informar el primero.
- Reservas duplicadas: contarlas independientemente.
- Valores negativos válidos: aceptarlos sin imponer reglas de negocio sobre
  rangos horarios.
- Reserva inválida después de reservas válidas: rechazar toda la entrada y no
  producir un resultado parcial.
- Varias reservas inválidas: informar la primera según el orden de entrada.
- Entrada que se reutiliza después del cálculo: conservarla sin modificaciones.

## Fuera de alcance

- Cambiar las reglas de solapamiento, el cálculo del máximo, el período
  informado, el desempate o la gestión de entradas inválidas.
- Incorporar métricas distintas del aforo máximo y su primer período.
- Añadir límites de entrada, objetivos numéricos de rendimiento o consumo de
  memoria, o requisitos de benchmarks.
- Añadir otras técnicas de optimización no descritas en esta especificación.
- Aplicar reglas de negocio sobre rangos horarios o instantes negativos.
- Incorporar interfaces, almacenamiento o comunicación con servicios externos.

## Criterios de finalización

- La validación y la obtención de los eventos ocurren durante un único recorrido
  de la entrada, sin un recorrido separado para volver a validarla.
- Las etiquetas de inicio y fin son enteras y su ordenamiento conserva el
  procesamiento de inicios antes que finales en un mismo instante.
- Los casos límite de esta especificación conservan el comportamiento
  funcional vigente.
- Las entradas inválidas siguen produciendo el error acordado para la primera
  reserva inválida y nunca un resultado parcial.
- La entrada permanece sin cambios después del cálculo.
- La complejidad de tiempo y memoria se mantiene en `O(n log n)` y `O(n)`,
  respectivamente.
- No se exige demostrar una mejora mediante un umbral numérico no acordado.

## Dudas abiertas

No quedan dudas abiertas para esta especificación. Los valores enteros concretos
para las etiquetas de inicio y fin quedan a elección de la implementación,
siempre que se mantenga el orden de eventos requerido.
