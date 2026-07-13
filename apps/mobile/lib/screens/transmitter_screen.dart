// lib/screens/transmitter_screen.dart
import 'dart:async';
import 'package:flutter/material.dart';

class TransmitterScreen extends StatefulWidget {
  const TransmitterScreen({super.key});

  @override
  State<TransmitterScreen> createState() => _TransmitterScreenState();
}

class _TransmitterScreenState extends State<TransmitterScreen> {
  bool _isTransmitting = false;
  bool _isMicMuted = false;
  bool _isFlashOn = false;
  bool _isFrontCamera = false;
  
  // Timer for a simple flashing red dot animation when transmitting
  Timer? _blinkTimer;
  bool _showRedDot = true;

  void _toggleTransmission() {
    setState(() {
      _isTransmitting = !_isTransmitting;
      if (_isTransmitting) {
        _blinkTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
          setState(() {
            _showRedDot = !_showRedDot;
          });
        });
      } else {
        _blinkTimer?.cancel();
        _blinkTimer = null;
      }
    });
  }

  @override
  void dispose() {
    _blinkTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      appBar: AppBar(
        title: const Text(
          'nidusMonitor - Bebé',
          style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF2C3E50)),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Contenedor principal del Video (Vista de transmisión / cámara local)
            Expanded(
              child: Container(
                margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.grey[900], // Fondo oscuro
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: const [
                    BoxShadow(color: Colors.black12, blurRadius: 10, offset: Offset(0, 4))
                  ],
                ),
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    // Simulación del Stream / Cámara
                    Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          _isTransmitting ? Icons.child_care : Icons.child_care_outlined,
                          size: 80,
                          color: _isTransmitting ? const Color(0xFF4A90E2) : Colors.white24,
                        ),
                        const SizedBox(height: 16),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 24.0),
                          child: Text(
                            _isTransmitting
                                ? 'Transmitiendo audio y video en vivo...'
                                : 'Cámara en espera. Presiona "Transmitir" para comenzar.',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: _isTransmitting ? Colors.white : Colors.white54,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ],
                    ),
                    
                    // Indicador de "Grabando / Transmitiendo" en la esquina superior izquierda
                    if (_isTransmitting)
                      Positioned(
                        top: 16,
                        left: 16,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: Colors.black54,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              AnimatedContainer(
                                duration: const Duration(milliseconds: 300),
                                width: 8,
                                height: 8,
                                decoration: BoxDecoration(
                                  color: _showRedDot ? Colors.red : Colors.transparent,
                                  shape: BoxShape.circle,
                                ),
                              ),
                              const SizedBox(width: 6),
                              const Text(
                                'EN VIVO',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),

                    // Indicador de micrófono silenciado en la esquina superior derecha
                    if (_isMicMuted)
                      Positioned(
                        top: 16,
                        right: 16,
                        child: Container(
                          padding: const EdgeInsets.all(6),
                          decoration: const BoxDecoration(
                            color: Colors.black54,
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(
                            Icons.mic_off,
                            color: Colors.redAccent,
                            size: 16,
                          ),
                        ),
                      ),
                  ],
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
                      // Botón para mutear/activar micrófono local
                      _ControlButton(
                        icon: _isMicMuted ? Icons.mic_off : Icons.mic,
                        label: _isMicMuted ? 'Mudo' : 'Micrófono',
                        color: _isMicMuted ? Colors.redAccent : const Color(0xFF4A90E2),
                        onPressed: () {
                          setState(() {
                            _isMicMuted = !_isMicMuted;
                          });
                        },
                      ),

                      // Botón de encender/apagar transmisión (Grande, central)
                      _ControlButton(
                        icon: _isTransmitting ? Icons.stop : Icons.play_arrow,
                        label: _isTransmitting ? 'Detener' : 'Transmitir',
                        color: _isTransmitting ? Colors.red : const Color(0xFF50E3C2),
                        onPressed: _toggleTransmission,
                      ),

                      // Botón para alternar cámara frontal/trasera
                      _ControlButton(
                        icon: Icons.switch_camera,
                        label: _isFrontCamera ? 'Frontal' : 'Trasera',
                        color: const Color(0xFF4A90E2),
                        onPressed: () {
                          setState(() {
                            _isFrontCamera = !_isFrontCamera;
                          });
                        },
                      ),

                      // Botón para encender/apagar flash (linterna)
                      _ControlButton(
                        icon: _isFlashOn ? Icons.flash_on : Icons.flash_off,
                        label: 'Luz',
                        color: _isFlashOn ? Colors.amber : Colors.grey,
                        onPressed: () {
                          setState(() {
                            _isFlashOn = !_isFlashOn;
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