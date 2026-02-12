import 'dart:async';
import 'dart:math';
import '../models/core_data.dart';

abstract class ThermalService {
  Stream<List<CoreData>> get coreDataStream;
  void dispose();
}

class MockThermalService implements ThermalService {
  final _controller = StreamController<List<CoreData>>.broadcast();
  Timer? _timer;
  final Random _random = Random();
  final int _coreCount = 8; // Simulating an 8-core CPU

  MockThermalService() {
    _startSimulation();
  }

  @override
  Stream<List<CoreData>> get coreDataStream => _controller.stream;

  void _startSimulation() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      final List<CoreData> data = List.generate(_coreCount, (index) {
        // tropical simulation: Temps between 40C and 95C
        double temp = 40 + _random.nextDouble() * 55;
        double load = _random.nextDouble() * 100;
        
        CoreStatus status;
        if (temp < 60) {
          status = CoreStatus.cold;
        } else if (temp < 80) {
          status = CoreStatus.warm;
        } else {
          status = CoreStatus.hot;
        }

        return CoreData(
          id: index,
          temperature: temp,
          load: load,
          status: status,
        );
      });
      _controller.add(data);
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    _controller.close();
  }
}
