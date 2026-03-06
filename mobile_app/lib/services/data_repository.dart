import 'package:supabase_flutter/supabase_flutter.dart';

class DataRepository {
  final _supabase = Supabase.instance.client;

  // Fetches aggregated ratings for a specific department
  // This hits the 'department_analytics' view we created in SQL
  Future<Map<String, dynamic>?> getDepartmentStats(String deptId) async {
    try {
      final response = await _supabase
          .from('department_analytics')
          .select()
          .eq('dept_id', deptId)
          .single();
      
      return response;
    } catch (e) {
      print('Error fetching department stats: $e');
      return null;
    }
  }

  // Fetches all reviews for a department to show the AI-sanitized comments
  Future<List<Map<String, dynamic>>> getDepartmentReviews(String deptId) async {
    try {
      final response = await _supabase
          .from('reviews')
          .select('ai_sanitized_comment, tags, resident_year, created_at')
          .eq('dept_id', deptId)
          .order('created_at', ascending: false);
      
      return List<Map<String, dynamic>>.from(response);
    } catch (e) {
      print('Error fetching reviews: $e');
      return [];
    }
  }
}
