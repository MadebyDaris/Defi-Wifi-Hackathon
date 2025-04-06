import 'dart:convert';

import 'package:defiwifi/main.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';

class WiFiData {
  final String? bSSID;
  final double? latitude;
  final double? longitude;
  final String? sSID;
  final String? timestamp;

  WiFiData({
    this.bSSID,
    this.latitude,
    this.longitude,
    this.sSID,
    this.timestamp,
  });

  factory WiFiData.fromJson(Map<String, dynamic> json) {
    return WiFiData(
      bSSID: json['BSSID'],
      latitude: (json['Latitude'] as num?)?.toDouble(),
      longitude: (json['Longitude'] as num?)?.toDouble(),
      sSID: json['SSID'],
      timestamp: json['Timestamp'],
    );
  }

  Map<String, dynamic> toJson() => {
        'BSSID': bSSID,
        'Latitude': latitude,
        'Longitude': longitude,
        'SSID': sSID,
        'Timestamp': timestamp,
      };
}

class WiFiMapWithLines extends StatefulWidget {
  const WiFiMapWithLines({Key? key, required List<Map<String, dynamic>> wifiData}) : super(key: key);

  @override
  State<WiFiMapWithLines> createState() => _WiFiMapWithLinesState();
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
      final serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        setState(() {
          _error = 'Location services are disabled.';
          _isLoading = false;
        });
        return;
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          setState(() {
            _error = 'Location permissions are denied.';
            _isLoading = false;
          });
          return;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        setState(() {
          _error = 'Location permissions are permanently denied.';
          _isLoading = false;
        });
        return;
      }

      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );

      setState(() {
        _currentPosition = LatLng(position.latitude, position.longitude);
        _isLoading = false;
      });
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
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error.isNotEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(_error),
            const SizedBox(height: 10),
            ElevatedButton(
              onPressed: _getCurrentLocation,
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_currentPosition == null) {
      return const Center(child: Text('Unable to determine current location.'));
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
      child: _buildMap(),
    );
  }

  Widget _buildMap() {
    return FlutterMap(
      options: MapOptions(
        center: _currentPosition,
        zoom: 16.0,
      ),
      children: [
        TileLayer(
          urlTemplate: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
          subdomains: const ['a', 'b', 'c'],
        ),
        MarkerLayer(
          markers: [
            Marker(
              point: _currentPosition!,
              builder: (ctx) => const Icon(
                Icons.person_pin_circle,
                color: Colors.blue,
                size: 40,
              ),
            ),
            ..._wifiData.where((wifi) =>
                wifi.latitude != null && wifi.longitude != null).map(
              (wifi) => Marker(
                point: LatLng(wifi.latitude!, wifi.longitude!),
                builder: (ctx) => const Icon(
                  Icons.wifi,
                  color: Colors.red,
                  size: 30,
                ),
              ),
            ),
          ],
        ),
        PolylineLayer(
          polylines: _wifiData
              .where((wifi) =>
                  wifi.latitude != null && wifi.longitude != null)
              .map(
                (wifi) => Polyline(
                  points: [
                    _currentPosition!,
                    LatLng(wifi.latitude!, wifi.longitude!),
                  ],
                  color: Colors.green.withOpacity(0.7),
                  strokeWidth: 2.0,
                ),
              )
              .toList(),
        ),
      ],
    );
  }
}
