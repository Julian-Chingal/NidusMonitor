import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../config/settings.dart';

class AuthService {
  static const String _tokenKey = 'auth_token';

  /// Performs login and saves the JWT token
  Future<bool> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('${AppSettings.apiBaseUrl}/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body);
        if (data.containsKey('access_token')) {
          await saveToken(data['access_token']);
          return true;
        }
      }
      // Log for debugging
      debugPrint('Login failed: ${response.statusCode} - ${response.body}');
      return false;
    } catch (e) {
      debugPrint('Login Error: $e');
      return false;
    }
  }

  /// Saves the token in SharedPreferences
  Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  /// Retrieves the saved token
  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  /// Checks if a token exists
  Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }

  /// Logs out by removing the token
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
  }
}
