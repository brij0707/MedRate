import 'package:flutter/material.dart';
import '../services/review_service.dart';
import '../config_template.dart'; // Remember to use your real config locally

class SubmitReviewScreen extends StatefulWidget {
  final String collegeId;
  final String deptId;

  const SubmitReviewScreen({super.key, required this.collegeId, required this.deptId});

  @override
  State<SubmitReviewScreen> createState() => _SubmitReviewScreenState();
}

class _SubmitReviewScreenState extends State<SubmitReviewScreen> {
  // Use the service we built in Step 4.2
  late final ReviewService _reviewService;
  
  // State for ratings (1-5)
  Map<String, int> _ratings = {
    'academics': 3, 'exposure': 3, 'infra': 3, 'hands_on': 3, 'stipend': 3, 'toxicity': 3,
  };

  final List<String> _allTags = [
    '#highly_toxic', '#supportive_seniors', '#hands_on_goldmine', 
    '#stipend_on_time', '#huge_patient_load', '#regular_seminars'
  ];
  List<String> _selectedTags = [];
  final TextEditingController _commentController = TextEditingController();
  String _residentYear = 'JR1';

  @override
  void initState() {
    super.initState();
    // In a real build, you'd use AppConfig.geminiApiKey here
    _reviewService = ReviewService('YOUR_KEY_HERE'); 
  }

  Widget _buildSlider(String label, String key) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('$label: ${_ratings[key]}'),
        Slider(
          value: _ratings[key]!.toDouble(),
          min: 1, max: 5, divisions: 4,
          onChanged: (val) => setState(() => _ratings[key] = val.toInt()),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Submit Resident Review')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            DropdownButton<String>(
              value: _residentYear,
              items: ['JR1', 'JR2', 'JR3', 'SR'].map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(),
              onChanged: (val) => setState(() => _residentYear = val!),
            ),
            _buildSlider('Academics', 'academics'),
            _buildSlider('Clinical Exposure', 'exposure'),
            _buildSlider('Toxicity (5 is worst)', 'toxicity'),
            const Divider(),
            Wrap(
              spacing: 8,
              children: _allTags.map((tag) => FilterChip(
                label: Text(tag),
                selected: _selectedTags.contains(tag),
                onSelected: (bool selected) {
                  setState(() {
                    selected ? _selectedTags.add(tag) : _selectedTags.remove(tag);
                  });
                },
              )).toList(),
            ),
            TextField(
              controller: _commentController,
              maxLines: 4,
              decoration: const InputDecoration(hintText: 'Share your candid experience (AI will anonymize this)'),
            ),
            ElevatedButton(
              onPressed: () async {
                final success = await _reviewService.submitReview(
                  collegeId: widget.collegeId,
                  deptId: widget.deptId,
                  ratings: _ratings,
                  selectedTags: _selectedTags,
                  rawComment: _commentController.text,
                  residentYear: _residentYear,
                );
                if (success) Navigator.pop(context);
              },
              child: const Text('Submit Anonymously'),
            ),
          ],
        ),
      ),
    );
  }
}
