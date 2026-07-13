import 'package:permission_handler/permission_handler.dart';

class PermissionService {
  /// Request all required permissions for Nidus Monitor
  Future<Map<Permission, PermissionStatus>> requestAllPermissions() async {
    Map<Permission, PermissionStatus> statuses = await [
      Permission.camera,
      Permission.microphone,
      Permission.notification,
    ].request();
    return statuses;
  }

  /// Check specific permission status
  Future<bool> checkPermissionStatus(Permission permission) async {
    var status = await permission.status;
    return status.isGranted;
  }
  
  /// Request single permission
  Future<bool> requestPermission(Permission permission) async {
    var status = await permission.request();
    return status.isGranted;
  }

  /// Check if all required permissions are granted
  Future<bool> areAllPermissionsGranted() async {
    bool camera = await Permission.camera.isGranted;
    bool mic = await Permission.microphone.isGranted;
    bool notification = await Permission.notification.isGranted;
    
    return camera && mic && notification;
  }
}
