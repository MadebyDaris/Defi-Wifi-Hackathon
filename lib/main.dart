import 'dart:convert';

import 'package:defiwifi/map.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:http/http.dart' as http;
import 'package:defiwifi/direction.dart';
import 'package:defiwifi/rs_link.dart';


void main() {
  WidgetsFlutterBinding.ensureInitialized();
  // await Firebase.initializeApp();

  runApp(const MainApp());
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home:
        Scaffold(
          body: Container(
            child:
            BlocProvider(
              create: (context) => BackendBloc(),
              child: const WiFiWidget()),
          ),
        ),
    );
  }
}

class BackendBloc extends Cubit<String> {
  BackendBloc() : super('');

  Future<void> fetchData() async {
    final response = await http.get(Uri.parse('http://localhost:5000/scan'));
    if (response.statusCode == 200) {
      emit(response.body);
    } else {
      emit('Failed to fetch data');
    }
  }
}

class WiFiWidget extends StatelessWidget {
  const WiFiWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final backendBloc = BlocProvider.of<BackendBloc>(context);

    return Scaffold(
      appBar: AppBar(
        title: Text('Défi WiFi carte'),
      ),
      body: Stack(
        children: [
          BlocBuilder<BackendBloc, String>(
            builder: (context, state) {
              if (state.isEmpty || state == 'Failed to fetch data') {
                return const Center(child: Text('No data available'));
              }
              try {
                final wifiData = jsonDecode(state) as List;
                return WiFiMapWithLines(
                  wifiData: wifiData.cast<Map<String, dynamic>>(),
                );
              } catch (e) {
                return Center(child: Text('Error parsing data: $e'));
              }
            }
          ),
          WiFiMapWithLines(wifiData: [],),
          Positioned(
            bottom: 20,
            right: 20,
            child: ElevatedButton(
              onPressed: () {
                backendBloc.fetchData();
              },
              child: const Text('Refresh Data'),
            ),
          ),
          Text(getHelloFromRust()),
        ]
      ),
    );
  }
}