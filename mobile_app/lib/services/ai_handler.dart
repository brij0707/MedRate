import 'package:google_generative_ai/google_generative_ai.dart';

class AISanitizer {
  // The system instructions that tell the AI how to behave as a "Privacy Officer"
  static const String _systemPrompt = """
    You are the medRate Privacy Officer. Your job is to rewrite medical residency reviews for 100% anonymity.
    
    STRICT RULES:
    1. REMOVE ALL NOUNS: Delete names of doctors, HODs, residents, or specific staff members.
    2. GENERALIZE TIMELINES: Change specific dates (e.g., 'Jan 5th') to 'frequently' or 'regularly'.
    3. STRIP IDENTIFIERS: Remove specific room numbers, phone numbers, or emails.
    4. PRESERVE SENTIMENT: If the review is about a 'toxic environment' or 'poor hands-on,' keep that meaning, but remove the 'who' and 'exactly where'.
    5. OUTPUT ONLY: Provide only the sanitized text. No conversational filler.
  """;

  final GenerativeModel _model;

  AISanitizer(String apiKey) 
      : _model = GenerativeModel(model: 'gemini-1.5-flash', apiKey: apiKey);

  Future<String> sanitize(String rawReview) async {
    try {
      final content = [
        Content.text("$_systemPrompt\n\nReview to sanitize: $rawReview")
      ];
      final response = await _model.generateContent(content);
      
      // Returns the washed version or a fallback error message
      return response.text ?? "Error: Could not sanitize text.";
    } catch (e) {
      return "Anonymization failed. Please check your connection.";
    }
  }
}

