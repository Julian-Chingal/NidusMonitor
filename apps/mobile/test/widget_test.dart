// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter_test/flutter_test.dart';

import 'package:nidus_monitor/main.dart';

void main() {
  testWidgets('Login screen rendering test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const NidusMonitorApp());

    // Verify that the login screen elements are present.
    expect(find.text('nidusMonitor'), findsOneWidget);
    expect(find.text('Tu bebé, siempre seguro'), findsOneWidget);
    expect(find.text('Iniciar Sesión'), findsOneWidget);
  });
}
