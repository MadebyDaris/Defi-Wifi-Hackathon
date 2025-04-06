import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:defiwifi/direction.dart';

class FirestoreService {
  final FirebaseFirestore _db = FirebaseFirestore.instance;

  Stream<List<WiFiData>> getWiFiDataStream() {
    return _db.collection('wifi_scans')
      .orderBy('timestamp', descending: true)
      .snapshots()
      .map((snapshot) => snapshot.docs
          .map((doc) => WiFiData.fromJson(doc.data()))
          .toList());
  }

  Future<List<WiFiData>> getWiFiDataOnce() async {
    try {
      final snapshot = await _db.collection('wifi_scans')
        .orderBy('timestamp', descending: true)
        .limit(100)
        .get();
      
      return snapshot.docs
          .map((doc) => WiFiData.fromJson(doc.data()))
          .toList();
    } catch (e) {
      print('Error getting WiFi data: $e');
      return [];
    }
  }
}