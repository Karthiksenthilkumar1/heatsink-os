enum CoreStatus { cold, warm, hot }

class CoreData {
  final int id;
  final double temperature;
  final double load;
  final CoreStatus status;

  CoreData({
    required this.id,
    required this.temperature,
    required this.load,
    required this.status,
  });

  factory CoreData.initial(int id) {
    return CoreData(
      id: id,
      temperature: 40.0,
      load: 0.0,
      status: CoreStatus.cold,
    );
  }
}
