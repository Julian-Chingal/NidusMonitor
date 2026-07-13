import 'package:flutter/material.dart';
import 'package:nidus_monitor/screens/login_screen.dart';
import 'package:nidus_monitor/screens/home_screen.dart';
import 'package:nidus_monitor/services/auth_service.dart';
import 'package:nidus_monitor/theme/app_theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const NidusMonitorApp());
}

class NidusMonitorApp extends StatelessWidget {
  const NidusMonitorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NidusMonitor',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: FutureBuilder<bool>(
        future: AuthService().isLoggedIn(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Scaffold(
              body: Center(
                child: CircularProgressIndicator(),
              ),
            );
          }
          final isLoggedIn = snapshot.data ?? false;
          return isLoggedIn ? const HomeScreen() : const LoginScreen();
        },
      ),
    );
  }
}