# ProyectoFinal

Crear un juego completo de Wordle en Python utilizando Pygame.

### Requisitos Funcionales y Técnicos:

1. **Mecánica de Juego y Teclado:**
   - Matriz visual de 6 filas (intentos) por 5 columnas (letras).
   - Soporte para teclado físico: entrada de letras (A-Z), tecla Backspace para borrar y Enter para enviar la palabra.
   - Validación: solo permitir enviar la palabra si la fila actual contiene exactamente 5 letras.

2. **Lógica de Evaluación (Manejo correcto de letras duplicadas):**
   - **Verde:** La letra está en la palabra secreta y en la posición exacta.
   - **Amarillo:** La letra está en la palabra secreta pero en una posición incorrecta.
   - **Gris:** La letra no está en la palabra secreta.
   - *Regla de duplicados:* Implementa el algoritmo estándar de Wordle (dar prioridad a los aciertos exactos en verde y consumir las apariciones disponibles para no marcar amarillos de más si una letra se repite).

3. **Diseño Visual y UX:**
   - Estética pulida en modo oscuro: fondo `#121213`, bordes vacíos `#3A3A3C`, verde `#538D4E`, amarillo `#B59F3B`, gris `#3A3A3C`.
   - Letras mayúsculas bien centradas dentro de cada casilla.
   - Teclado en pantalla (opcional pero deseado) que actualice el color de cada tecla usada según las pistas obtenidas.

4. **Estados de Juego:**
   - **Victoria:** Si se adivina la palabra, mostrar en pantalla: "¡Felicidades, has adivinado la palabra!".
   - **Derrota:** Si se fallan los 6 intentos, mostrar un mensaje de fin de juego revelando la palabra oculta.
   - **Reinicio:** Presionar la tecla `R` o `Espacio` para comenzar una partida nueva sin cerrar la aplicación.

5. **Banco de Palabras:**
   - Incluye una lista embebida en el código con al menos 40 palabras comunes de 5 letras en español (sin acentos ni caracteres especiales) para seleccionar una al azar en cada intento.
