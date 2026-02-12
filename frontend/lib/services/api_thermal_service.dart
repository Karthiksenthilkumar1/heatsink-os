import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/core_data.dart';
import 'thermal_service.dart';

class ApiThermalService implements ThermalService {
  final _controller = StreamController<List<CoreData>>.broadcast();
  Timer? _timer;
  final String baseUrl = 'http://127.0.0.1:8000';

  ApiThermalService() {
    _startPolling();
  }

  @override
  Stream<List<CoreData>> get coreDataStream => _controller.stream;

  void _startPolling() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) async {
      try {
        final temps = await _fetchTemps();
        final load = await _fetchLoad();
        
        final List<CoreData> data = _mergeData(temps, load);
        _controller.add(data);
      } catch (e) {
        print('Error fetching thermal data: $e');
        // Optionally emit an empty list or error state, or just keep previous data
      }
    });
  }

  Future<Map<String, dynamic>> _fetchTemps() async {
    final response = await http.get(Uri.parse('$baseUrl/temps'));
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load temps');
    }
  }

  Future<Map<String, dynamic>> _fetchLoad() async {
    final response = await http.get(Uri.parse('$baseUrl/load'));
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load load report');
    }
  }

  List<CoreData> _mergeData(Map<String, dynamic> temps, Map<String, dynamic> load) {
    List<CoreData> cores = [];
    
    // Parse cores from temps response
    // Structure: { "cores": { "0": { "temperature": 62.1 }, "1": ... } }
    final coreTemps = temps['cores'] as Map<String, dynamic>?;
    
    if (coreTemps != null) {
      coreTemps.forEach((key, value) {
        int id = int.tryParse(key) ?? -1;
        if (id != -1) {
          double temp = (value['temperature'] as num).toDouble();
          
          // Get load for this core
          // Structure: { "0": { "load_percent": 45.2 }, ... }
          double coreLoad = 0.0;
          if (load.containsKey(key)) {
            coreLoad = (load[key]['load_percent'] as num).toDouble();
          }

          CoreStatus status;
          if (temp < 60) {
            status = CoreStatus.cold;
          } else if (temp < 80) {
            status = CoreStatus.warm;
          } else {
            status = CoreStatus.hot;
          }

          cores.add(CoreData(
            id: id,
            temperature: temp,
            load: coreLoad,
            status: status,
          ));
        }
      });
    }
    
    // Sort by ID to ensure order
    cores.sort((a, b) => a.id.compareTo(b.id));
    return cores;
  }

  @override
  void dispose() {
    _timer?.cancel();
    _controller.close();
  }
}
