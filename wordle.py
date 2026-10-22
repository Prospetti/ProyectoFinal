"""
=============================================================================
                          WORDLE EN ESPAÑOL (PYGAME)
=============================================================================
Descripción:
    Implementación completa y profesional del juego Wordle adaptado al español,
    construido en un único archivo ejecutable utilizando la librería Pygame.

Requisitos implementados:
    1. Mecánica y teclado: Matriz de 6 intentos x 5 letras. Teclado físico
       (A-Z, Backspace, Enter) y validación de palabras completas de 5 letras.
    2. Lógica de evaluación estricta: Algoritmo de dos pasadas para manejo
       exacto de letras repetidas (Verde para acierto de posición, Amarillo para
       letra presente sin exceder las apariciones en la palabra secreta, Gris
       para descartadas).
    3. Diseño visual y UX: Paleta oscura oficial (#121213, #3A3A3C, #538D4E,
       #B59F3B, #818384). Letras mayúsculas perfectamente centradas.
       Teclado virtual interactivo en pantalla que refleja el estado de las letras.
    4. Estados de juego: Pantallas de Victoria ("¡Felicidades, has adivinado la palabra!"),
       Derrota ("Fin del juego. La palabra era: ...") y reinicio fluido con [R] o [Espacio].
    5. Banco de palabras: Lista embebida de más de 80 palabras comunes de 5 letras
       en español (sin tildes ni caracteres especiales).

Ejecución:
    python wordle.py   o   py -3.12 wordle.py
=============================================================================
"""

import sys
import random
import pygame

# =============================================================================
# 1. CONSTANTES GRÁFICAS Y PALETA DE COLORES
# =============================================================================
ANCHO_VENTANA = 540
ALTO_VENTANA = 750
FPS = 60

# Paleta oficial en modo oscuro
COLOR_FONDO        = (18, 18, 19)      # #121213: Fondo oscuro de la app
COLOR_BORDE_VACIO  = (58, 58, 60)      # #3A3A3C: Borde de celda vacía
COLOR_BORDE_ACTIVO = (135, 138, 140)   # Borde de celda mientras se escribe
COLOR_VERDE        = (83, 141, 78)     # #538D4E: Posición y letra correcta
COLOR_AMARILLO     = (181, 159, 59)    # #B59F3B: Letra presente en otra posición
COLOR_GRIS         = (58, 58, 60)      # #3A3A3C: Letra no presente / consumida
COLOR_TECLA_DEF    = (129, 131, 132)   # #818384: Color neutro de teclas no usadas
COLOR_TEXTO        = (255, 255, 255)   # Blanco para letras y encabezados
COLOR_SUBTEXTO     = (160, 160, 160)   # Gris tenue para leyendas
COLOR_TOAST_FONDO  = (240, 240, 240)   # Fondo blanco para alertas flotantes
COLOR_TOAST_TEXTO  = (18, 18, 19)      # Texto oscuro dentro de la alerta
COLOR_CARD_FONDO   = (32, 32, 35)      # Fondo de la tarjeta de fin de juego

# Jerarquía para no degradar pistas en el teclado (Verde > Amarillo > Gris > Sin usar)
PRIORIDAD_PISTA = {
    'DEF': 0,
    'GRAY': 1,
    'YELLOW': 2,
    'GREEN': 3
}

# =============================================================================
# 2. BANCO DE PALABRAS EN ESPAÑOL (5 LETRAS, SIN TILDES)
# =============================================================================
BANCO_PALABRAS = [
    "ACTOR", "AGUAS", "AMIGO", "ARENA", "BANCO", "BARCO", "BOLSO", "BRAZO",
    "CABLE", "CALLE", "CAMPO", "CANTO", "CIELO", "CLAVE", "CORTE", "CREMA",
    "DANZA", "DESEO", "DISCO", "DULCE", "ENERO", "FALDA", "FAROL", "FORMA",
    "FLORA", "FRUTA", "FUEGO", "GATOS", "GENTE", "GLOBO", "GRANO", "HIELO",
    "HONOR", "HOTEL", "HUEVO", "INDIO", "ISLAS", "JARRA", "JUEGO", "LETRA",
    "LIBRO", "LINEA", "LLAVE", "LUCES", "MADRE", "MANOS", "METAL", "MONTE",
    "MUNDO", "NIEVE", "NOCHE", "NORTE", "ORDEN", "OVEJA", "PADRE", "PARED",
    "PERRO", "PLANO", "PLAYA", "PLUMA", "QUESO", "RADIO", "RATAS", "RATON",
    "REINO", "SABOR", "SELVA", "SOLAR", "SUELO", "TARDE", "TEXTO", "TINTA",
    "TIGRE", "TORRE", "TRIGO", "UNION", "VALLE", "VAPOR", "VERDE", "VIAJE",
    "VISTA", "ZORRO", "ACERO", "ARBOL", "BAILE", "CARRO", "COSTA", "VOCAL"
]

# =============================================================================
# 3. LÓGICA DE EVALUACIÓN (ALGORITMO ESTÁNDAR DE WORDLE)
# =============================================================================
def evaluar_intento(intento: str, palabra_secreta: str) -> list[str]:
    """
    Evalúa una palabra de 5 letras frente a la palabra secreta.
    Implementa el algoritmo canónico de Wordle en dos pasadas para resolver
    correctamente las letras repetidas:

    1. Primera pasada (Verdes):
       Localiza las letras que coinciden exactamente en posición y caracter,
       restando su disponibilidad del conteo de letras de la palabra secreta.
    2. Segunda pasada (Amarillos y Grises):
       Para los caracteres restantes, si la letra aún tiene ocurrencias
       disponibles en la palabra secreta se marca como 'YELLOW' y se descuenta.
       Si ya no quedan apariciones libres, se marca como 'GRAY'.
    """
    resultado = ['GRAY'] * 5
    conteo_disponibles = {}

    # Contabilizar frecuencia de cada letra en la palabra secreta
    for letra in palabra_secreta:
        conteo_disponibles[letra] = conteo_disponibles.get(letra, 0) + 1

    # PASO 1: Prioridad absoluta a los aciertos exactos (Verde)
    for i in range(5):
        if intento[i] == palabra_secreta[i]:
            resultado[i] = 'GREEN'
            conteo_disponibles[intento[i]] -= 1

    # PASO 2: Asignación de letras presentes (Amarillo) o ausentes (Gris)
    for i in range(5):
        if resultado[i] != 'GREEN':
            letra = intento[i]
            if conteo_disponibles.get(letra, 0) > 0:
                resultado[i] = 'YELLOW'
                conteo_disponibles[letra] -= 1
            else:
                resultado[i] = 'GRAY'

    return resultado


# =============================================================================
# 4. TECLADO VIRTUAL INTERACTIVO
# =============================================================================
class TecladoVirtual:
    """Gestiona el renderizado y clics sobre el teclado en pantalla."""
    def __init__(self, y_inicio: int):
        self.y_inicio = y_inicio
        self.filas = [
            list("QWERTYUIOP"),
            list("ASDFGHJKL"),
            ["ENTER"] + list("ZXCVBNM") + ["⌫"]
        ]
        self.estados = {}  # Letra -> 'DEF' | 'GRAY' | 'YELLOW' | 'GREEN'
        self.botones = []  # Lista de (pygame.Rect, texto_etiqueta, accion)
        self._construir_teclas()

    def reset(self):
        """Limpia los estados de las teclas para una nueva partida."""
        self.estados.clear()

    def actualizar_pistas(self, intento: str, evaluacion: list[str]):
        """Actualiza el color de cada tecla respetando la prioridad de aciertos."""
        for letra, color_nuevo in zip(intento, evaluacion):
            color_previo = self.estados.get(letra, 'DEF')
            if PRIORIDAD_PISTA[color_nuevo] > PRIORIDAD_PISTA[color_previo]:
                self.estados[letra] = color_nuevo

    def _construir_teclas(self):
        """Calcula el tamaño y posición de cada tecla virtual."""
        self.botones.clear()
        alto_tecla = 52
        gap = 5
        ancho_letra = 44
        y = self.y_inicio

        # Fila 1: Q W E R T Y U I O P (10 teclas)
        ancho_f1 = 10 * ancho_letra + 9 * gap
        x_f1 = (ANCHO_VENTANA - ancho_f1) // 2
        for i, letra in enumerate(self.filas[0]):
            rect = pygame.Rect(x_f1 + i * (ancho_letra + gap), y, ancho_letra, alto_tecla)
            self.botones.append((rect, letra, letra))

        # Fila 2: A S D F G H J K L (9 teclas)
        y += alto_tecla + 6
        ancho_f2 = 9 * ancho_letra + 8 * gap
        x_f2 = (ANCHO_VENTANA - ancho_f2) // 2
        for i, letra in enumerate(self.filas[1]):
            rect = pygame.Rect(x_f2 + i * (ancho_letra + gap), y, ancho_letra, alto_tecla)
            self.botones.append((rect, letra, letra))

        # Fila 3: ENTER + 7 letras (Z-M) + ⌫ (Borrar)
        y += alto_tecla + 6
        ancho_especial = 66
        ancho_f3 = (ancho_especial * 2) + (7 * ancho_letra) + (8 * gap)
        x = (ANCHO_VENTANA - ancho_f3) // 2

        for tecla in self.filas[2]:
            if tecla == "ENTER":
                w = ancho_especial
                accion = "ENTER"
            elif tecla == "⌫":
                w = ancho_especial
                accion = "BACKSPACE"
            else:
                w = ancho_letra
                accion = tecla

            rect = pygame.Rect(x, y, w, alto_tecla)
            self.botones.append((rect, tecla, accion))
            x += w + gap

    def detectar_clic(self, pos: tuple[int, int]) -> str | None:
        """Devuelve la acción correspondiente a la tecla clickeada, si existe."""
        for rect, _, accion in self.botones:
            if rect.collidepoint(pos):
                return accion
        return None

    def dibujar(self, superficie: pygame.Surface, fuente: pygame.font.Font, pos_mouse: tuple[int, int]):
        """Renderiza cada tecla con sus esquinas redondeadas y pistas de color."""
        mapa_colores = {
            'DEF': COLOR_TECLA_DEF,
            'GRAY': COLOR_GRIS,
            'YELLOW': COLOR_AMARILLO,
            'GREEN': COLOR_VERDE
        }

        for rect, etiqueta, _ in self.botones:
            estado = self.estados.get(etiqueta, 'DEF')
            color = mapa_colores[estado]

            # Efecto hover sobre teclas sin revelar
            if rect.collidepoint(pos_mouse) and estado == 'DEF':
                color = (min(color[0] + 25, 255),
                         min(color[1] + 25, 255),
                         min(color[2] + 25, 255))

            pygame.draw.rect(superficie, color, rect, border_radius=5)
            texto_surf = fuente.render(etiqueta, True, COLOR_TEXTO)
            texto_rect = texto_surf.get_rect(center=rect.center)
            superficie.blit(texto_surf, texto_rect)


# =============================================================================
# 5. MOTOR Y CONTROLADOR PRINCIPAL DEL JUEGO
# =============================================================================
class WordleGame:
    """Administra el estado de la partida, los eventos de usuario y la vista."""
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Wordle en Español - Pygame")
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        self.reloj = pygame.time.Clock()

        # Configuración tipográfica con fuentes del sistema
        self.fuente_logo    = pygame.font.SysFont(["Arial", "Segoe UI", "sans-serif"], 28, bold=True)
        self.fuente_celda   = pygame.font.SysFont(["Arial", "Segoe UI", "sans-serif"], 32, bold=True)
        self.fuente_tecla   = pygame.font.SysFont(["Arial", "Segoe UI", "sans-serif"], 14, bold=True)
        self.fuente_alerta  = pygame.font.SysFont(["Arial", "Segoe UI", "sans-serif"], 17, bold=True)
        self.fuente_modal   = pygame.font.SysFont(["Arial", "Segoe UI", "sans-serif"], 20, bold=True)
        self.fuente_sub     = pygame.font.SysFont(["Arial", "Segoe UI", "sans-serif"], 14)
        self.fuente_btn     = pygame.font.SysFont(["Arial", "Segoe UI", "sans-serif"], 13, bold=True)

        # Dimensiones de la matriz
        self.filas = 6
        self.columnas = 5
        self.tam_celda = 58
        self.gap_celda = 6
        self.ancho_matriz = self.columnas * self.tam_celda + (self.columnas - 1) * self.gap_celda
        self.x_inicio_matriz = (ANCHO_VENTANA - self.ancho_matriz) // 2
        self.y_inicio_matriz = 80

        # Botón superior de reinicio
        self.rect_btn_reiniciar = pygame.Rect(ANCHO_VENTANA - 110, 20, 95, 30)

        # Inicializar el teclado en pantalla
        self.teclado = TecladoVirtual(y_inicio=485)

        # Iniciar variables de la primera partida
        self.reiniciar_juego()

    def reiniciar_juego(self):
        """Restaura todos los valores para comenzar una nueva partida limpia."""
        self.palabra_secreta = random.choice(BANCO_PALABRAS).upper()
        self.intentos_guardados = []     # Lista de palabras evaluadas (ej. ["BARCO"])
        self.evaluaciones = []           # Lista de resultados (ej. [["GREEN", ...]])
        self.intento_actual = ""         # Letras que el usuario está escribiendo
        self.fila_actual = 0             # Fila en curso (0 a 5)
        self.estado_juego = "JUGANDO"    # "JUGANDO" | "VICTORIA" | "DERROTA"
        self.mensaje_toast = ""          # Texto para avisos temporales
        self.tiempo_toast = 0            # Tiempo límite para ocultar toast
        self.teclado.reset()

    def notificar(self, texto: str, duracion_ms: int = 1600):
        """Despliega un aviso flotante en la pantalla durante un tiempo definido."""
        self.mensaje_toast = texto
        self.tiempo_toast = pygame.time.get_ticks() + duracion_ms

    def agregar_letra(self, letra: str):
        """Agrega una letra al intento actual si aún no se alcanzan las 5 letras."""
        if self.estado_juego == "JUGANDO" and len(self.intento_actual) < self.columnas:
            self.intento_actual += letra.upper()

    def borrar_letra(self):
        """Borra la última letra ingresada."""
        if self.estado_juego == "JUGANDO" and len(self.intento_actual) > 0:
            self.intento_actual = self.intento_actual[:-1]

    def enviar_intento(self):
        """Verifica que la palabra tenga 5 letras y procesa la evaluación."""
        if self.estado_juego != "JUGANDO":
            return

        # Validación de longitud exacta de 5 letras
        if len(self.intento_actual) < self.columnas:
            self.notificar("Se necesitan 5 letras")
            return

        # Aplicar el algoritmo de evaluación
        evaluacion = evaluar_intento(self.intento_actual, self.palabra_secreta)
        self.intentos_guardados.append(self.intento_actual)
        self.evaluaciones.append(evaluacion)
        self.teclado.actualizar_pistas(self.intento_actual, evaluacion)

        # Verificar condición de Victoria
        if self.intento_actual == self.palabra_secreta:
            self.estado_juego = "VICTORIA"
            return

        # Verificar condición de Derrota (último intento fallido)
        if self.fila_actual == self.filas - 1:
            self.estado_juego = "DERROTA"
            return

        # Avanzar a la siguiente fila
        self.fila_actual += 1
        self.intento_actual = ""

    def ejecutar_accion(self, accion: str):
        """Maneja las acciones disparadas tanto por teclas físicas como virtuales."""
        if accion == "ENTER":
            self.enviar_intento()
        elif accion == "BACKSPACE":
            self.borrar_letra()
        elif len(accion) == 1 and accion.isalpha():
            self.agregar_letra(accion)

    def dibujar_encabezado(self, pos_mouse: tuple[int, int]):
        """Dibuja el título del juego y el botón superior de nueva partida."""
        # Título
        titulo = self.fuente_logo.render("W O R D L E", True, COLOR_TEXTO)
        titulo_rect = titulo.get_rect(center=(ANCHO_VENTANA // 2, 35))
        self.pantalla.blit(titulo, titulo_rect)

        # Botón de reinicio rápido en la esquina superior
        color_btn = COLOR_TECLA_DEF
        if self.rect_btn_reiniciar.collidepoint(pos_mouse):
            color_btn = (150, 153, 155)
        pygame.draw.rect(self.pantalla, color_btn, self.rect_btn_reiniciar, border_radius=6)
        txt_btn = self.fuente_btn.render("↻ Reiniciar", True, COLOR_TEXTO)
        txt_rect = txt_btn.get_rect(center=self.rect_btn_reiniciar.center)
        self.pantalla.blit(txt_btn, txt_rect)

        # Línea separadora
        pygame.draw.line(self.pantalla, COLOR_BORDE_VACIO, (25, 65), (ANCHO_VENTANA - 25, 65), 1)

    def dibujar_tablero(self):
        """Dibuja la matriz de 6 filas x 5 columnas con letras centradas y colores."""
        mapa_colores = {
            'GREEN': COLOR_VERDE,
            'YELLOW': COLOR_AMARILLO,
            'GRAY': COLOR_GRIS
        }

        for fila in range(self.filas):
            for col in range(self.columnas):
                x = self.x_inicio_matriz + col * (self.tam_celda + self.gap_celda)
                y = self.y_inicio_matriz + fila * (self.tam_celda + self.gap_celda)
                rect_celda = pygame.Rect(x, y, self.tam_celda, self.tam_celda)

                letra = ""
                color_fondo = None
                color_borde = COLOR_BORDE_VACIO

                # Fila previamente evaluada
                if fila < len(self.intentos_guardados):
                    letra = self.intentos_guardados[fila][col]
                    estado = self.evaluaciones[fila][col]
                    color_fondo = mapa_colores[estado]
                    color_borde = color_fondo

                # Fila activa que se está escribiendo actualmente
                elif fila == self.fila_actual and self.estado_juego == "JUGANDO":
                    if col < len(self.intento_actual):
                        letra = self.intento_actual[col]
                        color_borde = COLOR_BORDE_ACTIVO

                # 1. Dibujar relleno si la celda tiene pista asignada
                if color_fondo:
                    pygame.draw.rect(self.pantalla, color_fondo, rect_celda, border_radius=4)

                # 2. Dibujar contorno de la celda
                pygame.draw.rect(self.pantalla, color_borde, rect_celda, width=2, border_radius=4)

                # 3. Dibujar letra mayúscula centrada
                if letra:
                    surf_letra = self.fuente_celda.render(letra, True, COLOR_TEXTO)
                    rect_letra = surf_letra.get_rect(center=rect_celda.center)
                    self.pantalla.blit(surf_letra, rect_letra)

    def dibujar_panel_final(self):
        """Muestra una tarjeta elegante con el estado de Victoria o Derrota."""
        if self.estado_juego not in ("VICTORIA", "DERROTA"):
            return

        # Configurar mensajes según el estado
        if self.estado_juego == "VICTORIA":
            mensaje_principal = "¡Felicidades, has adivinado la palabra!"
            color_borde = COLOR_VERDE
            sub_info = f"Completado en {len(self.intentos_guardados)} de 6 intentos"
        else:
            mensaje_principal = f"Fin del juego. La palabra era: {self.palabra_secreta}"
            color_borde = COLOR_BORDE_VACIO
            sub_info = "¡Suerte en la próxima partida!"

        # Crear superficie para la tarjeta
        ancho_card = ANCHO_VENTANA - 60
        alto_card = 95
        x_card = 30
        y_card = 390

        rect_card = pygame.Rect(x_card, y_card, ancho_card, alto_card)

        # Dibujar fondo y borde de la tarjeta
        pygame.draw.rect(self.pantalla, COLOR_CARD_FONDO, rect_card, border_radius=10)
        pygame.draw.rect(self.pantalla, color_borde, rect_card, width=2, border_radius=10)

        # Mensaje principal
        surf_msg = self.fuente_modal.render(mensaje_principal, True, COLOR_TEXTO)
        rect_msg = surf_msg.get_rect(center=(ANCHO_VENTANA // 2, y_card + 30))
        self.pantalla.blit(surf_msg, rect_msg)

        # Subtexto descriptivo
        surf_sub = self.fuente_sub.render(sub_info, True, COLOR_SUBTEXTO)
        rect_sub = surf_sub.get_rect(center=(ANCHO_VENTANA // 2, y_card + 54))
        self.pantalla.blit(surf_sub, rect_sub)

        # Indicación de reinicio
        surf_rst = self.fuente_sub.render("Presiona [R] o [Espacio] para comenzar de nuevo", True, (200, 200, 200))
        rect_rst = surf_rst.get_rect(center=(ANCHO_VENTANA // 2, y_card + 76))
        self.pantalla.blit(surf_rst, rect_rst)

    def dibujar_notificacion(self):
        """Muestra alertas emergentes temporales (ej. 'Se necesitan 5 letras')."""
        ahora = pygame.time.get_ticks()
        if self.mensaje_toast and ahora < self.tiempo_toast:
            surf_txt = self.fuente_alerta.render(self.mensaje_toast, True, COLOR_TOAST_TEXTO)
            pad_x, pad_y = 18, 10
            ancho = surf_txt.get_width() + (pad_x * 2)
            alto = surf_txt.get_height() + (pad_y * 2)

            rect_toast = pygame.Rect((ANCHO_VENTANA - ancho) // 2, 70, ancho, alto)
            pygame.draw.rect(self.pantalla, COLOR_TOAST_FONDO, rect_toast, border_radius=8)
            rect_txt = surf_txt.get_rect(center=rect_toast.center)
            self.pantalla.blit(surf_txt, rect_txt)

    def dibujar_pie(self):
        """Pie de página informativo."""
        if self.estado_juego == "JUGANDO":
            txt = "Usa tu teclado físico o haz clic en las teclas"
            color = COLOR_SUBTEXTO
            surf = self.fuente_sub.render(txt, True, color)
            rect = surf.get_rect(center=(ANCHO_VENTANA // 2, 705))
            self.pantalla.blit(surf, rect)

    def bucle_principal(self):
        """Bucle de ejecución principal a 60 FPS."""
        ejecutando = True

        while ejecutando:
            pos_mouse = pygame.mouse.get_pos()

            # --- GESTIÓN DE EVENTOS ---
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False

                # Entradas por teclado físico
                elif evento.type == pygame.KEYDOWN:
                    # Reinicio con R o Espacio al terminar la partida
                    if self.estado_juego in ("VICTORIA", "DERROTA") and evento.key in (pygame.K_r, pygame.K_SPACE):
                        self.reiniciar_juego()
                        continue

                    # Reinicio forzado con Ctrl+R en cualquier momento
                    if evento.key == pygame.K_r and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        self.reiniciar_juego()
                        continue

                    # Tecla ENTER para enviar palabra
                    if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self.enviar_intento()

                    # Tecla BACKSPACE para borrar
                    elif evento.key == pygame.K_BACKSPACE:
                        self.borrar_letra()

                    # Teclas alfabéticas (A-Z)
                    elif evento.unicode and evento.unicode.isalpha():
                        self.agregar_letra(evento.unicode)

                # Entradas por ratón (clic sobre teclado virtual o botón de reinicio)
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    # Clic en botón de reiniciar
                    if self.rect_btn_reiniciar.collidepoint(evento.pos):
                        self.reiniciar_juego()
                        continue

                    # Clic en tarjeta de fin de juego para reiniciar
                    if self.estado_juego in ("VICTORIA", "DERROTA"):
                        self.reiniciar_juego()
                        continue

                    # Clic en el teclado virtual
                    accion = self.teclado.detectar_clic(evento.pos)
                    if accion:
                        self.ejecutar_accion(accion)

            # --- DIBUJADO Y PRESENTACIÓN ---
            self.pantalla.fill(COLOR_FONDO)
            self.dibujar_encabezado(pos_mouse)
            self.dibujar_tablero()
            self.teclado.dibujar(self.pantalla, self.fuente_tecla, pos_mouse)
            self.dibujar_pie()
            self.dibujar_panel_final()
            self.dibujar_notificacion()

            pygame.display.flip()
            self.reloj.tick(FPS)

        pygame.quit()
        sys.exit()


# =============================================================================
# 6. ENTRADA DEL PROGRAMA
# =============================================================================
if __name__ == "__main__":
    juego = WordleGame()
    juego.bucle_principal()
