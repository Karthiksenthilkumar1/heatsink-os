import 'package:flutter/material.dart';
import '../../models/core_data.dart';
import '../../services/thermal_service.dart';
import '../../services/api_thermal_service.dart';
import '../../services/mock_thermal_service.dart'; // Keep for fallback if needed
import '../widgets/thermal_card.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  // Switch to ApiThermalService for real data
  final ThermalService _thermalService = ApiThermalService();
  late Stream<List<CoreData>> _coreDataStream;

  @override
  void initState() {
    super.initState();
    _coreDataStream = _thermalService.coreDataStream;
  }

  @override
  void dispose() {
    _thermalService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1E1E1E),
      appBar: AppBar(
        title: const Text('HeatSink-OS Dashboard'),
        backgroundColor: const Color(0xFF2D2D2D),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              // TODO: Settings
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Tropical Climate Optimizer',
              style: TextStyle(
                color: Colors.white54,
                fontSize: 14,
                letterSpacing: 1.2,
              ),
            ),
            const SizedBox(height: 20),
            Expanded(
              child: StreamBuilder<List<CoreData>>(
                stream: _coreDataStream,
                builder: (context, snapshot) {
                  if (snapshot.hasError) {
                    return Center(child: Text('Error: ${snapshot.error}', style: const TextStyle(color: Colors.red)));
                  }
                  if (!snapshot.hasData) {
                    return const Center(child: CircularProgressIndicator());
                  }

                  final cores = snapshot.data!;
                  return GridView.builder(
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 4, // Desktop layout
                      childAspectRatio: 1.2,
                      crossAxisSpacing: 16,
                      mainAxisSpacing: 16,
                    ),
                    itemCount: cores.length,
                    itemBuilder: (context, index) {
                      return ThermalCard(coreData: cores[index]);
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
