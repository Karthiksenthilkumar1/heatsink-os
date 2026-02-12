import '../models/core_data.dart';

abstract class ThermalService {
  Stream<List<CoreData>> get coreDataStream;
  void dispose();
}
