import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Auto AI App Builder',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const Scaffold(
        appBar: AppBar(title: Text('Hello Sipho')),
        body: Center(child: Text('Your Flutter app is running!')),
      ),
    );
  }
}