import 'package:flutter/material.dart';
import '../../models/core_data.dart';

class ThermalCard extends StatelessWidget {
  final CoreData coreData;

  const ThermalCard({super.key, required this.coreData});

  Color _getStatusColor(CoreStatus status) {
    switch (status) {
      case CoreStatus.hot:
        return Colors.redAccent;
      case CoreStatus.warm:
        return Colors.orangeAccent;
      case CoreStatus.cold:
        return Colors.blueAccent;
    }
  }

  IconData _getStatusIcon(CoreStatus status) {
    switch (status) {
      case CoreStatus.hot:
        return Icons.local_fire_department;
      case CoreStatus.warm:
        return Icons.wb_sunny;
      case CoreStatus.cold:
        return Icons.ac_unit;
    }
  }

  @override
  Widget build(BuildContext context) {
    final color = _getStatusColor(coreData.status);

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            colors: [color.withOpacity(0.1), color.withOpacity(0.05)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          border: Border.all(color: color.withOpacity(0.3), width: 1),
        ),
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Core ${coreData.id}',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.white70,
                      ),
                ),
                Icon(_getStatusIcon(coreData.status), color: color),
              ],
            ),
            const Spacer(),
            Text(
              '${coreData.temperature.toStringAsFixed(1)}°C',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
            ),
            const SizedBox(height: 8),
            LinearProgressIndicator(
              value: coreData.load / 100,
              backgroundColor: Colors.white10,
              valueColor: AlwaysStoppedAnimation<Color>(color),
            ),
            const SizedBox(height: 4),
            Text(
              'Load: ${coreData.load.toStringAsFixed(0)}%',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.white54),
            ),
          ],
        ),
      ),
    );
  }
}
