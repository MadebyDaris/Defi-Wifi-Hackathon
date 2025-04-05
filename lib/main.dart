import 'package:defiwifi/map.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MainApp());
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: 
      MapPage()
      // Scaffold(
      //   body: Center(
      //     child: 
      //     BlocProvider(
      //       create: (context) => BackendBloc(),
      //       child: const MyWidget()),
      //   ),
      // ),
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

class MyWidget extends StatelessWidget {
  const MyWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final backendBloc = BlocProvider.of<BackendBloc>(context);

    return Scaffold(
      appBar: AppBar(
        title: Text('Flutter App with Python Backend'),
      ),
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            backendBloc.fetchData();
          },
          child: BlocBuilder<BackendBloc, String>(
          builder: (context, state) {
            return Text(state);
          },
        ),
        ),
      ),
    );
  }
}