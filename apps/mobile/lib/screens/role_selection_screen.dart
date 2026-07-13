// lib/screens/role_selection_screen.dart
import 'package:flutter/material.dart';
import 'transmitter_screen.dart'; // Importamos la pantalla del transmisor (Bebé)
import 'receiver_screen.dart';    // Importamos la pantalla del receptor (Padres)

class RoleSelectionScreen extends StatelessWidget {
  const RoleSelectionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'nidusMonitor',
          style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF2C3E50)),
        ),
        centerTitle: true,
        automaticallyImplyLeading: false, // Evita que el usuario regrese al Login deslizando
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                '¿Cómo vas a usar este dispositivo hoy?',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF2C3E50),
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Selecciona el rol para este teléfono.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey, fontSize: 14),
              ),
              const SizedBox(height: 40),

              // Tarjeta para el Modo Bebé
              _RoleCard(
                title: 'Modo Bebé',
                description: 'Coloca este teléfono en la habitación del bebé para transmitir audio y video en tiempo real.',
                icon: Icons.child_care,
                iconColor: const Color(0xFF4A90E2),
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const TransmitterScreen()),
                  );
                },
              ),

              const SizedBox(height: 24),

              // Tarjeta para el Modo Padres
              _RoleCard(
                title: 'Modo Padres',
                description: 'Usa este dispositivo para vigilar, escuchar y recibir alertas de tu bebé desde cualquier lugar.',
                icon: Icons.visibility,
                iconColor: const Color(0xFF50E3C2),
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const ReceiverScreen()),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Widget personalizado y estilizado para las opciones
class _RoleCard extends StatelessWidget {
  final String title;
  final String description;
  final IconData icon;
  final Color iconColor;
  final VoidCallback onTap;

  const _RoleCard({
    required this.title,
    required this.description,
    required this.icon,
    required this.iconColor,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 3,
      shadowColor: Colors.black12,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20), // Asegura que el efecto táctil respete las esquinas
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Contenedor circular para el icono
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: iconColor.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, size: 40, color: iconColor),
              ),
              const SizedBox(width: 16),
              // Textos descriptivos de la tarjeta
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF2C3E50),
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      description,
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.grey[600],
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}