# Constitución — room-booking-occupancy

Principios innegociables. Toda spec, plan y tarea debe cumplirlos.

1. **Eficiencia y rendimiento extremos**: Python 3.12+ y solo librería estándar
   para el algoritmo.
2. **La spec manda**: ningún comportamiento se implementa si no está en la
   spec activa. Si falta una decisión, se detiene el trabajo y se pregunta.
3. **Núcleo puro e independiente**: La función `max_occupancy` es lógica pura, 
   independiente de entradas/salidas de red, bases de datos o interfaces de usuario, 
   permitiendo pruebas unitarias rigurosas.
4. **Tests como puerta**: cada tarea termina con sus tests en verde.
   Prohibido avanzar con tests en rojo.
5. **Calidad y rigor analítico**: Se exige documentación y análisis detallado 
   en inglés (`README.md` y `ANALYSIS.md`) que incluya complejidad Big O (tiempo y memoria), 
   análisis de escenarios límite y justificación de decisiones.
6. **Idioma**: Código, nombres, comentarios, tests, commits, README y ANALYSIS estrictamente en inglés. 
   Todo el código va en inglés siempre.