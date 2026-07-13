// lib/screens/receiver_screen.dart
import 'package:flutter/material.dart';

class ReceiverScreen extends StatefulWidget {
  const ReceiverScreen({super.key});

  @override
  State<ReceiverScreen> createState() => _ReceiverScreenState();
}

class _ReceiverScreenState extends State<ReceiverScreen> {
  bool _isAudioEnabled = true;
  bool _isMicMuted = true;

  @override
  void initState() {
    super.initState();
    _connectToStream();
  }

  void _connectToStream() {
    // Conectarse al WebSocket/Signaling server para recibir el stream de video
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      appBar: AppBar(
        title: const Text('nidusMonitor', style: TextStyle(fontWeight: FontWeight.bold)),
        centerTitle: true,
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Contenedor principal del Video (Pantalla del bebé)
            Expanded(
              child: Container(
                margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.grey[900], // Fondo simulando video apagado o cargando
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: const [
                    BoxShadow(color: Colors.black12, blurRadius: 10, offset: Offset(0, 4))
                  ],
                ),
                child: const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      CircularProgressIndicator(color: Color(0xFF50E3C2)),
                      SizedBox(height: 16),
                      Text(
                        'Conectando con la cámara del bebé...',
                        style: TextStyle(color: Colors.white70, fontSize: 14),
                      ),
                    ],
                  ),
                ),
              ),
            ),

            // Panel de Control Inferior (Botones de acción)
            Padding(
              padding: const EdgeInsets.all(24.0),
              child: Card(
                elevation: 2,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 16.0, horizontal: 8.0),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      // Botón para mutear/escuchar al bebé
                      _ControlButton(
                        icon: _isAudioEnabled ? Icons.volume_up : Icons.volume_off,
                        label: _isAudioEnabled ? 'Escuchando' : 'Mutear',
                        color: _isAudioEnabled ? const Color(0xFF4A90E2) : Colors.grey,
                        onPressed: () {
                          setState(() {
                            _isAudioEnabled = !_isAudioEnabled;
                          });
                        },
                      ),
                      
                      // Botón para hablarle al bebé (Push to talk)
                      _ControlButton(
                        icon: _isMicMuted ? Icons.mic_off : Icons.mic,
                        label: _isMicMuted ? 'Hablar' : 'Hablando...',
                        color: _isMicMuted ? Colors.grey : const Color(0xFF50E3C2),
                        onPressed: () {
                          setState(() {
                            _isMicMuted = !_isMicMuted;
                          });
                        },
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Widget auxiliar para simplificar los botones del panel de control
class _ControlButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onPressed;

  const _ControlButton({
    required this.icon,
    required this.label,
    required this.color,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        IconButton.filledTonal(
          icon: Icon(icon, color: color),
          iconSize: 28,
          style: IconButton.styleFrom(
            padding: const EdgeInsets.all(16),
            backgroundColor: color.withValues(alpha: 0.1),
          ),
          onPressed: onPressed,
        ),
        const SizedBox(height: 6),
        Text(
          label,
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: Colors.black87),
        ),
      ],
    );
  }
}