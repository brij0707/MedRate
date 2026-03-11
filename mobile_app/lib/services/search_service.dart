import 'package:supabase_flutter/supabase_flutter.dart';

class SearchService {
  final _supabase = Supabase.instance.client;

  // Search across 15k+ records using our optimized SQL View
  Future<List<Map<String, dynamic>>> searchColleges(String query) async {
    if (query.isEmpty) return [];

    try {
      // Searches name, state, and course_name simultaneously
      final response = await _supabase
          .from('colleges') 
          .select()
          .or('college_name.ilike.%$query%,state.ilike.%$query%,course_name.ilike.%$query%')
          .limit(20); // Limit for mobile performance

      return List<Map<String, dynamic>>.from(response);
    } catch (e) {
      print('Search Error: $e');
      return [];
    }
  }

  // Fetch departments for a specific college when selected
  Future<List<Map<String, dynamic>>> getDepartments(String collegeId) async {
    try {
      final response = await _supabase
          .from('departments')
          .select('id, degree, course_name')
          .eq('college_id', collegeId);
      
      return List<Map<String, dynamic>>.from(response);
    } catch (e) {
      print('Error fetching departments: $e');
      return [];
    }
  }
}
