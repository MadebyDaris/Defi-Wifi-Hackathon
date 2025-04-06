import 'dart:convert';

import 'package:defiwifi/main.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';

class WiFiData {
  String? bSSID;
  double? latitude;
  double? longitude;
  String? sSID;
  String? timestamp;

  WiFiData(
      {this.bSSID, this.latitude, this.longitude, this.sSID, this.timestamp});

  WiFiData.fromJson(Map<String, dynamic> json) {
    bSSID = json['BSSID'];
    latitude = json['Latitude'];
    longitude = json['Longitude'];
    sSID = json['SSID'];
    timestamp = json['Timestamp'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = new Map<String, dynamic>();
    data['BSSID'] = this.bSSID;
    data['Latitude'] = this.latitude;
    data['Longitude'] = this.longitude;
    data['SSID'] = this.sSID;
    data['Timestamp'] = this.timestamp;
    return data;
  }
}

class WiFiMapWithLines extends StatefulWidget {
  final List<Map<String, dynamic>> wifiData;

  const WiFiMapWithLines({Key? key, required this.wifiData}) : super(key: key);

  @override
  _WiFiMapWithLinesState createState() => _WiFiMapWithLinesState();
}

class _WiFiMapWithLinesState extends State<WiFiMapWithLines> {
  LatLng? _currentPosition;
  bool _isLoading = true;
  String _error = '';
  List<WiFiData> _wifiData = [];

  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
  }

  Future<void> _getCurrentLocation() async {
    try {
      bool? serviceEnabled;
      try {
        serviceEnabled = await Geolocator.isLocationServiceEnabled();
      } on MissingPluginException catch (e) {
        debugPrint('Geolocator plugin not implemented: $e');
        setState(() {
          _error = 'Location services not available on this device';
          _isLoading = false;
        });
        return;
      }

      if (serviceEnabled == false) {
        setState(() {
          _error = 'Location services are disabled.';
          _isLoading = false;
        });
        return;
      }

      // Rest of your location permission handling...
    } catch (e) {
      setState(() {
        _error = 'Error getting location: $e';
        _isLoading = false;
      });
    }
  }
  
  List<WiFiData> _parseWiFiData(String jsonString) {
    try {
      final List<dynamic> jsonList = json.decode(jsonString);
      return jsonList.map((json) => WiFiData.fromJson(json)).toList();
    } catch (e) {
      throw Exception('Failed to parse WiFi data: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_error.contains('MissingPluginException')) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text('Location services not available'),
          ElevatedButton(
            onPressed: () => _getCurrentLocation(),
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }
    return BlocListener<BackendBloc, String>(
      listener: (context, state) {
        if (state.isNotEmpty && state != 'Failed to fetch data') {
          try {
            setState(() {
              _wifiData = _parseWiFiData(state);
            });
          } catch (e) {
            setState(() {
              _error = e.toString();
            });
          }
        }
      },
      child: _buildMapContent(context),
    );
  }

  @override
  Widget _buildMapContent(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error.isNotEmpty) {
      return Center(child: Text(_error));
    }

    if (_currentPosition == null) {
      return const Center(child: Text('Unable to determine current location'));
    }

    return FlutterMap(
      options: MapOptions(
        center: _currentPosition,
        zoom: 16.0,
      ),
      children: [
        TileLayer(
          urlTemplate: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
          subdomains: ['a', 'b', 'c'],
        ),
        MarkerLayer(
          markers: [
            Marker(
              point: _currentPosition!,
              builder: (ctx) => const Icon(Icons.person_pin_circle, color: Colors.blue, size: 40),
            ),
            ...widget.wifiData.map((wifi) => Marker(
              point: LatLng(wifi['Latitude'], wifi['Longitude']),
              builder: (ctx) => const Icon(Icons.wifi, color: Colors.red, size: 30),
            )).toList(),
          ],
        ),
        PolylineLayer(
          polylines: [
            ...widget.wifiData.map((wifi) => Polyline(
              points: [
                _currentPosition!,
                LatLng(wifi['Latitude'], wifi['Longitude']),
              ],
              color: Colors.green.withOpacity(0.7),
              strokeWidth: 2.0,
            )).toList(),
          ],
        ),
      ],
    );
  }
}