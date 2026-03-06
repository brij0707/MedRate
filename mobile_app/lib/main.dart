import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'screens/search_screen.dart';
import 'config_template.dart'; // Use your real config.dart locally

void main() async {
  // Ensure Flutter is ready for async calls
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Supabase with your project credentials
  // NOTE: Replace these with your actual keys from your private config.dart
  await Supabase.initialize(
    url: 'YOUR_SUPABASE_URL',
    anonKey: 'YOUR_SUPABASE_ANON_KEY',
  );

  runApp(const MedRateApp());
}

class MedRateApp extends StatelessWidget {
  const MedRateApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'medRate Beta',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true, // Modern UI look for the Play Store
      ),
      // Set the Search Screen as the first page
      home: const SearchScreen(),
    );
  }
}
