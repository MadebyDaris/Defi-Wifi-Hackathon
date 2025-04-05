import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import 'package:defiwifi/tile_provider.dart';
import 'package:url_launcher/url_launcher.dart';



class MapPage extends StatefulWidget  {
    final String title;

    const MapPage({
      super.key,
      this.title = "Défi WiFi carte",
    });

  @override
  State<MapPage> createState() => _MapPageState();
}

class _MapPageState extends State<MapPage> {
    @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // drawer: const MenuDrawer(HomePage.route),
      body:
          FlutterMap(
            options: MapOptions(),
            children: [
              openStreetMapTileLayer,
              RichAttributionWidget(
                popupInitialDisplayDuration: const Duration(seconds: 5),
                animationConfig: const ScaleRAWA(),
                showFlutterMapAttribution: false,
                attributions: [
                  TextSourceAttribution(
                    'OpenStreetMap contributors',
                    onTap: () async => launchUrl(
                      Uri.parse('https://openstreetmap.org/copyright'),
                    ),
                  ),
                  const TextSourceAttribution(
                    'POC for Hackathon 2019 Challenge 4',
                    prependCopyright: false,
                  ),
                ],
              ),
            ],
          ),
    );
  }
}