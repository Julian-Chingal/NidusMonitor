---
name: nidus-app-design
description: Pautas de diseño UI/UX, paleta de colores, interfaces interactivas y visualización de métricas para las aplicaciones móvil y web de Nidus Baby Monitor.
---

# Diseño de Interfaces (UI/UX) - Nidus Baby Monitor

Este Skill define las directrices estéticas, de experiencia de usuario (UX) e interfaz visual (UI) para las aplicaciones de Nidus Monitor, asegurando que las pantallas sean claras, hermosas y tranquilizadoras para los padres, tanto en dispositivos móviles (Flutter) como en el dashboard web.

---

## 1. Sistema de Diseño Visual

El diseño de Nidus Monitor debe transmitir **tranquilidad, seguridad y tecnología premium**. Se prioriza un diseño moderno que no fatigue la vista de los padres en la oscuridad.

### 1.1. Paleta de Colores (Tema Oscuro por Defecto)
El monitoreo ocurre principalmente de noche, por lo que el fondo oscuro evita deslumbramientos.

- **Fondo Primario**: `#0F172A` (Slate 900) - Oscuro profundo.
- **Fondo Secundario / Tarjetas**: `#1E293B` (Slate 800) - Para contenedores y cards.
- **Color de Acento / Marca**: `#4A90E2` (Soft Blue) o `#50E3C2` (Soft Teal) - Transmite tecnología y calma.
- **Texto Principal**: `#F8FAFC` (Slate 50) - Legibilidad máxima.
- **Texto Secundario**: `#94A3B8` (Slate 400) - Leyendas y metadatos.

### 1.2. Tipografía
- Se sugiere el uso de fuentes sans-serif modernas y altamente legibles como **Inter**, **Outfit** o **Cabinet Grotesk**.
- Jerarquía de títulos limpia, evitando tamaños exagerados que rompan el equilibrio visual.

---

## 2. Visualización de Estados en Tiempo Real

El estado actual del bebé debe ser identificable **de un vistazo** mediante códigos de colores y micro-animaciones en el borde del feed de video o en un banner superior.

| Estado | Color Asociado | Elemento Visual / Animación |
| :--- | :--- | :--- |
| `deep_sleep` | Indigo Pastel (`#6366F1`) | Borde estático. Onda de sueño (onda senoidal lenta tipo respiración). |
| `moving` | Violeta Claro (`#A855F7`) | Onda de respiración ligeramente más rápida con pequeñas vibraciones. |
| `awake` | Verde Teal (`#10B981`) | Pulso suave. Icono de ojitos abiertos. |
| `position_change` | Amarillo Oro (`#F59E0B`) | Flash transitorio en la interfaz. Icono de flecha de rotación. |
| `strong_motion` | Naranja Vivo (`#F97316`) | Alerta intermitente de frecuencia media. Icono de campana activa. |
| `out_of_area` | Rojo Coral (`#EF4444`) | Borde rojo pulsante de alta intensidad. Alerta sonora suave pero perceptible. |

---

## 3. Interfaz Interactiva de ROI (Región de Interés)

La zona segura de monitoreo (ROI) se configura de forma interactiva sobre la vista de la cámara.

```
+---------------------------------------+
|  Video Feed (320x240 o escalado)      |
|  +-----------------------------+      |
|  | [x_min, y_min]              |      |
|  |      +---------------+      |      |
|  |      |   ZONA        |      |      |
|  |      |   SEGURA      |      |      |
|  |      +---------------+      |      |
|  |               [x_max, y_max]|      |
|  +-----------------------------+      |
+---------------------------------------+
```

### Reglas de Diseño para el Selector de ROI:
1. **Superposición (Overlay)**: Dibujar un rectángulo semi-transparente sobre el reproductor de video.
2. **Puntos de Arrastre (Handles)**: Colocar controles interactivos (esquinas redondas y visibles, ej: 12dp de diámetro) en las esquinas superior-izquierda `(x_min, y_min)` e inferior-derecha `(x_max, y_max)`.
3. **Mapeo de Coordenadas**:
   - La pantalla móvil o web tiene dimensiones físicas en píxeles.
   - Antes de enviar las coordenadas al servidor mediante Socket.IO (`update_roi`) o REST (`/config/roi`), se deben normalizar las coordenadas a valores entre `0.0` y `1.0`.
   - **Fórmula**:
     $$\text{x\_normalizado} = \frac{\text{Pixel X}}{\text{Ancho Contenedor Video}}$$
     $$\text{y\_normalizado} = \frac{\text{Pixel Y}}{\text{Alto Contenedor Video}}$$
4. **Retroalimentación Visual**: Mientras el usuario arrastra la ROI, el color del rectángulo debe tornarse azul translúcido con un indicador del porcentaje cubierto de la pantalla. Al soltar, enviar el evento inmediatamente y mostrar un aviso breve ("Zona segura actualizada").

---

## 4. Diseño del Panel de Métricas e Historial

El panel inferior debe organizar las métricas procesadas por la IA de forma limpia y moderna.

### 4.1. Métricas de Parpadeo (EAR) y Movimiento
- **Eye Aspect Ratio (EAR)**:
  - Mostrar un medidor circular o una barra de progreso horizontal.
  - Si el valor de EAR está por debajo de `0.2` (ojos cerrados), colorear la barra en un azul suave; si está por encima, en verde brillante.
- **Gráfico de Movimiento (Motion Activity)**:
  - Un minigráfico en tiempo real (sparkline o gráfica de área) que muestre los últimos 30 puntos recibidos (los últimos ~6 segundos a 5 FPS).
  - Umbrales en el gráfico: Marcar líneas punteadas sutiles en los límites clave (`0.015` para movimiento leve y `0.05` para movimiento fuerte) para que los padres entiendan el contexto de la actividad del bebé.

### 4.2. Historial de Eventos (Cards de Eventos)
- Cada fila del historial de eventos debe llevar un icono descriptivo y un color que represente la gravedad del cambio de estado.
- Mostrar la hora relativa (ej: "Hace 5 minutos", "Hace 2 horas") y la hora exacta en un formato de texto más pequeño.
- El diseño debe ser compacto con bordes muy redondeados (`border-radius: 16px`).

---

## 5. Accesibilidad y Alertas en el Móvil
- **Vibración (Haptic Feedback)**:
  - Cambios a estados críticos (`out_of_area`, `strong_motion`) deben disparar patrones de vibración específicos (ej: doble vibración corta para salida de área).
- **Control de Audio**:
  - Los botones de silenciar audio / micrófono del panel de control deben ser grandes y fáciles de presionar a oscuras.
  - Utilizar estados de color claros para los botones activos (ej: Micrófono silenciado = Gris; Hablando = Verde brillante con un pulso de ondas circulares expansivas alrededor).
