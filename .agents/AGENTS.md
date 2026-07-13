# Reglas del Proyecto Nidus Monitor

Este archivo contiene las directrices, estándares de codificación y reglas de comportamiento para los agentes de desarrollo que trabajan en la solución Nidus Monitor.

---

## 1. Reglas Generales de Programación

1. **Mantener la Integridad del Código**: Preservar todos los comentarios, docstrings y lógica existente que no esté directamente relacionada con la tarea actual.
2. **Asincronismo**:
   - En el backend (FastAPI, Socket.IO, WebRTC), priorizar funciones asíncronas (`async def`) para evitar bloquear el bucle de eventos.
   - En Flutter, gestionar operaciones de red y streaming usando `Future`, `Stream` y `async/await` de forma segura.
3. **Eficiencia en la IA**:
   - No aumentar el tamaño de frame (`320x240`) ni los FPS (`5 FPS`) configurados en `settings.py` sin justificación y prueba de rendimiento previa.
   - Mantener la complejidad del modelo de Pose en `0` (`model_complexity=0`).

---

## 2. Pautas para el Desarrollo del Servidor (FastAPI)

- Las configuraciones deben cargarse desde `config.settings` utilizando la clase Pydantic `Settings`. No hardcodear contraseñas, URLs ni rutas de Firebase.
- Todas las alertas críticas deben desencadenar:
  - Un evento de Socket.IO (`broadcast_alert`).
  - Una notificación push a través de `services.fcm.send_push_notification` (canal `baby_alerts`).
- Los endpoints REST deben validar tokens JWT para operaciones que requieran privilegios de administrador.

---

## 3. Pautas para el Desarrollo Móvil (Flutter)

- **Estructura**: Separar las pantallas (`lib/screens`) de la lógica de red e integración (`lib/services`).
- **Nombres**: Si se agregan widgets personalizados, ubicarlos bajo `lib/widgets` (corrigiendo el directorio `widgest` si es necesario).
- **Diseño**: Aplicar los colores oscuros de calma detallados en `nidus-app-design`. Los botones interactivos y de alerta deben ofrecer retroalimentación visual clara y respuestas hápticas leves.

---

## 4. Skills Disponibles en este Espacio de Trabajo

- [nidus-app-dev](file:///d:/Dev/nidusMonitor/.agents/skills/nidus-app-dev/SKILL.md): Guía de desarrollo e integración WebRTC/Socket.IO.
- [nidus-app-design](file:///d:/Dev/nidusMonitor/.agents/skills/nidus-app-design/SKILL.md): Guía de diseño de interfaces UI/UX, animaciones de métricas y ROI.
