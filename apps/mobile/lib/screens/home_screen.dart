import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:permission_handler/permission_handler.dart';
import '../services/permission_service.dart';
import '../theme/app_theme.dart';
import 'role_selection_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final PermissionService _permissionService = PermissionService();
  bool _cameraGranted = false;
  bool _micGranted = false;
  bool _notificationGranted = false;

  @override
  void initState() {
    super.initState();
    _checkPermissions();
  }

  Future<void> _checkPermissions() async {
    final camera = await _permissionService.checkPermissionStatus(Permission.camera);
    final mic = await _permissionService.checkPermissionStatus(Permission.microphone);
    final notification = await _permissionService.checkPermissionStatus(Permission.notification);
    
    setState(() {
      _cameraGranted = camera;
      _micGranted = mic;
      _notificationGranted = notification;
    });
    // Eliminado el auto-avance para dar oportunidad a aceptar notificaciones (opcional)
  }

  Future<void> _requestPermission(Permission permission) async {
    HapticFeedback.lightImpact();
    final granted = await _permissionService.requestPermission(permission);
    
    if (granted) {
      _checkPermissions();
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Permiso necesario para el funcionamiento de la app.'),
            backgroundColor: AppTheme.warningColor,
          ),
        );
      }
    }
  }

  void _proceedToRoleSelection() {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const RoleSelectionScreen()),
    );
  }

  Widget _buildPermissionCard(String title, IconData icon, bool isGranted, Permission permission) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: ListTile(
        leading: Icon(
          icon,
          color: isGranted ? AppTheme.successColor : AppTheme.textSecondary,
          size: 32,
        ),
        title: Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        trailing: isGranted
            ? const Icon(Icons.check_circle, color: AppTheme.successColor)
            : ElevatedButton(
                onPressed: () => _requestPermission(permission),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.accentColor,
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                ),
                child: const Text('Permitir'),
              ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Permisos Requeridos'),
        automaticallyImplyLeading: false,
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.security,
              size: 80,
              color: AppTheme.accentColor,
            ),
            const SizedBox(height: 24),
            Text(
              'Nidus Monitor necesita acceso a estas funciones para operar correctamente.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: AppTheme.textSecondary,
              ),
            ),
            const SizedBox(height: 32),
            
            _buildPermissionCard('Cámara', Icons.camera_alt, _cameraGranted, Permission.camera),
            _buildPermissionCard('Micrófono', Icons.mic, _micGranted, Permission.microphone),
            _buildPermissionCard('Notificaciones (Opcional)', Icons.notifications, _notificationGranted, Permission.notification),
            
            const Spacer(),
            SizedBox(
              height: 56,
              child: ElevatedButton(
                onPressed: (_cameraGranted && _micGranted) 
                  ? _proceedToRoleSelection 
                  : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: (_cameraGranted && _micGranted)
                      ? AppTheme.successColor
                      : AppTheme.backgroundSecondary,
                ),
                child: const Text(
                  'Continuar',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
