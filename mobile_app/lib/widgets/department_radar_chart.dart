import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

class DepartmentRadarChart extends StatelessWidget {
  final Map<String, dynamic> stats;

  const DepartmentRadarChart({super.key, required this.stats});

  @override
  Widget build(BuildContext context) {
    return AspectRatio(
      aspectRatio: 1.3,
      child: RadarChart(
        RadarChartData(
          radarShape: RadarShape.polygon,
          getTitle: (index, angle) {
            // Mapping the 6 parameters to the chart corners
            const labels = [
              'Academics',
              'Exposure',
              'Infra',
              'Hands-on',
              'Stipend',
              'Culture' // Inverted Toxicity
            ];
            return RadarChartTitle(text: labels[index], angle: angle);
          },
          dataSets: [
            RadarDataSet(
              fillColor: Colors.blue.withOpacity(0.4),
              borderColor: Colors.blue,
              entryRadius: 3,
              dataEntries: [
                RadarEntry(value: (stats['avg_academics'] ?? 0).toDouble()),
                RadarEntry(value: (stats['avg_clinical'] ?? 0).toDouble()),
                RadarEntry(value: (stats['avg_infra'] ?? 0).toDouble()),
                RadarEntry(value: (stats['avg_hands_on'] ?? 0).toDouble()),
                RadarEntry(value: (stats['avg_stipend'] ?? 0).toDouble()),
                RadarEntry(value: (stats['culture_score'] ?? 0).toDouble()),
              ],
            ),
          ],
          tickCount: 5, // 1 to 5 rating scale
          ticksTextStyle: const TextStyle(color: Colors.grey, fontSize: 10),
          gridBorderData: const BorderSide(color: Colors.black12),
        ),
      ),
    );
  }
}

