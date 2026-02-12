import 'package:flutter/material.dart';
import 'ui/screens/dashboard_screen.dart';

void main() {
  runApp(const HeatSinkApp());
}

class HeatSinkApp extends StatelessWidget {
  const HeatSinkApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'HeatSink-OS',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.orange,
          brightness: Brightness.dark,
        ),
        fontFamily: 'Segoe UI', // Windows standard
      ),
      home: const DashboardScreen(),
    );
  }
}
