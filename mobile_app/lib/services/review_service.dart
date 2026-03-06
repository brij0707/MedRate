import 'package:supabase_flutter/supabase_flutter.dart';
import 'ai_handler.dart';

class ReviewService {
  final _supabase = Supabase.instance.client;
  final AISanitizer _sanitizer;

  ReviewService(String apiKey) : _sanitizer = AISanitizer(apiKey);

  // The Master Submission Logic
  Future<bool> submitReview({
    required String collegeId,
    required String deptId,
    required Map<String, int> ratings, // Academics, Exposure, etc.
    required List<String> selectedTags, // From our taxonomy above
    required String rawComment,
    required String residentYear,
  }) async {
    try {
      // 1. Trigger the AI Sanitizer (The Anonymity Firewall)
      final sanitizedComment = await _sanitizer.sanitize(rawComment);

      // 2. Push the structured data to the 'reviews' table
      await _supabase.from('reviews').insert({
        'college_id': collegeId,
        'dept_id': deptId,
        'academics_rating': ratings['academics'],
        'clinical_exposure_rating': ratings['exposure'],
        'infrastructure_rating': ratings['infra'],
        'hands_on_rating': ratings['hands_on'],
        'stipend_rating': ratings['stipend'],
        'toxicity_rating': ratings['toxicity'],
        'tags': selectedTags,
        'raw_comment': rawComment, // Saved for internal audit
        'ai_sanitized_comment': sanitizedComment, // Shown to public
        'resident_year': residentYear,
      });

      return true;
    } catch (e) {
      print('Review submission failed: $e');
      return false;
    }
  }
}
