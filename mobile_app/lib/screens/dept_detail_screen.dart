import 'package:flutter/material.dart';
import '../services/data_repository.dart';
import '../widgets/department_radar_chart.dart';

class DeptDetailScreen extends StatefulWidget {
  final String deptId;
  final String deptName;

  const DeptDetailScreen({super.key, required this.deptId, required this.deptName});

  @override
  State<DeptDetailScreen> createState() => _DeptDetailScreenState();
}

class _DeptDetailScreenState extends State<DeptDetailScreen> {
  final DataRepository _repository = DataRepository();
  Map<String, dynamic>? _stats;
  List<Map<String, dynamic>> _reviews = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  void _loadData() async {
    final stats = await _repository.getDepartmentStats(widget.deptId);
    final reviews = await _repository.getDepartmentReviews(widget.deptId);
    setState(() {
      _stats = stats;
      _reviews = reviews;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.deptName)),
      body: _isLoading 
        ? const Center(child: CircularProgressIndicator())
        : SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Resident Reality Scorecard', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 20),
                if (_stats != null) DepartmentRadarChart(stats: _stats!),
                const Divider(),
                const Text('Department Tags', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                Wrap(
                  spacing: 8.0,
                  children: (_stats?['department_tags'] as List? ?? []).map((tag) => Chip(label: Text(tag))).toList(),
                ),
                const Divider(),
                const Text('Resident Comments (AI-Sanitized)', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _reviews.length,
                  itemBuilder: (context, index) {
                    final review = _reviews[index];
                    return Card(
                      margin: const EdgeInsets.symmetric(vertical: 8.0),
                      child: Padding(
                        padding: const EdgeInsets.all(12.0),
                        child: Text(review['ai_sanitized_comment'] ?? 'No comment provided.'),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
    );
  }
}
