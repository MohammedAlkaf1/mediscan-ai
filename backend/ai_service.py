"""
AI Service for generating intelligent medical explanations using OpenAI/LLMs
"""
import logging
import os
from typing import List, Dict, Optional
from parser_service import ParsedLabResult

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        # Check which AI provider to use
        self.provider = os.getenv("AI_PROVIDER", "openai").lower()  # openai or gemini
        
        if self.provider == "gemini":
            self.api_key = os.getenv("GEMINI_API_KEY")
            self.model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            self.enabled = bool(self.api_key)
            
            if self.enabled:
                try:
                    import google.generativeai as genai
                    import warnings
                    warnings.filterwarnings('ignore', category=FutureWarning)
                    genai.configure(api_key=self.api_key)
                    
                    # Initialize model without any default generation config
                    # (config will be passed at generation time)
                    self.client = genai.GenerativeModel(self.model)
                    
                    logger.info(f"AI Service initialized with Google Gemini ({self.model})")
                    logger.info(f"Model name from env: {self.model}")
                except ImportError:
                    logger.error("google-generativeai package not installed. Run: pip install google-generativeai")
                    self.enabled = False
            else:
                logger.warning("Gemini API key not provided")
        else:
            # OpenAI (default)
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.model = os.getenv("OPENAI_MODEL", "gpt-4")
            self.enabled = bool(self.api_key)
            
            if self.enabled:
                try:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=self.api_key)
                    logger.info(f"AI Service initialized with OpenAI ({self.model})")
                except ImportError:
                    logger.error("openai package not installed. Run: pip install openai")
                    self.enabled = False
            else:
                logger.warning("OpenAI API key not provided")
    
    def generate_personalized_explanation(
        self, 
        results: List[ParsedLabResult],
        report_type: str,
        user_age: Optional[int] = None,
        user_gender: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate AI-powered personalized explanation of lab results
        
        Args:
            results: List of parsed lab results
            report_type: Type of report (CBC, Lipid, etc.)
            user_age: Optional user age for context
            user_gender: Optional user gender for context
            
        Returns:
            Dict with summary, tips, and warnings
        """
        if not self.enabled:
            logger.warning("AI generation requested but service is disabled")
            return self._fallback_explanation(results, report_type)
        
        try:
            # Prepare lab results for AI
            results_text = self._format_results_for_ai(results)
            
            # Build context
            context = f"Report Type: {report_type}\n"
            if user_age:
                context += f"Patient Age: {user_age}\n"
            if user_gender:
                context += f"Patient Gender: {user_gender}\n"
            
            # Create prompt
            prompt = self._create_prompt(results_text, context)
            
            # DEBUG: Log prompt details
            logger.info(f"PROMPT LENGTH: {len(prompt)} characters")
            logger.info(f"PROMPT PREVIEW (first 200 chars): {prompt[:200]}")
            
            # Call AI API based on provider
            if self.provider == "gemini":
                response = self._call_gemini(prompt)
            else:
                response = self._call_openai(prompt)
            
            # Parse response
            explanation = response
            
            # DEBUG: Log raw AI response
            logger.info(f"=== RAW AI RESPONSE ===")
            logger.info(f"Length: {len(explanation)} characters")
            logger.info(f"First 300 chars: {explanation[:300]}")
            logger.info(f"Last 300 chars: {explanation[-300:]}")
            logger.info(f"=== END RAW AI RESPONSE ===")
            
            parsed = self._parse_ai_response(explanation)
            logger.info(f"Parsed summary length: {len(parsed['summary'])} chars")
            logger.info(f"Parsed tips length: {len(parsed['tips'])} chars")
            
            return parsed
            
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return self._fallback_explanation(results, report_type)
    
    def _format_results_for_ai(self, results: List[ParsedLabResult]) -> str:
        """Format lab results for AI consumption"""
        lines = []
        for r in results:
            value = r.value_numeric if r.value_numeric else r.value_text
            ref = r.ref_text if r.ref_text else f"{r.ref_low}-{r.ref_high}" if r.ref_low and r.ref_high else "N/A"
            lines.append(f"- {r.canonical_name}: {value} {r.unit or ''} (Reference: {ref}) - Status: {r.status}")
        return "\n".join(lines)
    
    def _create_prompt(self, results_text: str, context: str) -> str:
        """Create the prompt for AI"""
        return f"""Please explain these lab results in simple, friendly language that a patient can understand.

{context}

Lab Results:
{results_text}

Please provide a clear explanation in two parts:

PART 1 - UNDERSTANDING YOUR RESULTS:
Write 3-4 paragraphs explaining:
- Overall summary of the results
- What any abnormal values mean in simple terms
- Whether any values need attention

PART 2 - WELLNESS TIPS:
Provide 5-7 practical, actionable tips for maintaining or improving health based on these results.

Keep the tone friendly and encouraging. Use simple language without medical jargon. Remind the reader this is educational only and to consult their doctor."""
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful medical assistant that explains lab results in simple, 
                    easy-to-understand language. You are NOT diagnosing or providing medical advice, 
                    just explaining what the results mean. Always remind users to consult their doctor."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API"""
        system_prompt = """You are a helpful medical assistant that explains lab results in simple, 
        easy-to-understand language. You are NOT diagnosing or providing medical advice, 
        just explaining what the results mean. Always remind users to consult their doctor."""
        
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Disable safety filters for medical content
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        gen_config = {
            "temperature": 0.7,
            "max_output_tokens": 8000,
            "top_p": 0.95,
            "top_k": 40,
        }
        
        logger.info(f"Gemini generation_config: {gen_config}")
        
        response = self.client.generate_content(
            full_prompt,
            generation_config=gen_config,
            safety_settings=safety_settings
        )
        
        # DEBUG: Check if response was blocked or incomplete
        logger.info(f"Gemini finish_reason: {response.candidates[0].finish_reason if response.candidates else 'N/A'}")
        logger.info(f"Gemini safety ratings: {response.candidates[0].safety_ratings if response.candidates else 'N/A'}")
        
        # Log token usage if available
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            logger.info(f"Gemini token usage: {response.usage_metadata}")
        
        # Check if response was blocked
        if not response.text:
            logger.error("Gemini returned empty response!")
            if response.candidates:
                logger.error(f"Candidate finish reason: {response.candidates[0].finish_reason}")
            raise Exception("Gemini returned empty response")
        
        return response.text
    
    def _parse_ai_response(self, response: str) -> Dict[str, str]:
        """Parse AI response into structured format"""
        # Import disclaimer first
        from explanation_service import DISCLAIMER
        
        # Clean up the response - remove markdown formatting
        cleaned_response = response.replace('###', '').replace('**', '').replace('***', '')
        
        # Try to split by PART 2 or wellness tips section
        split_markers = [
            'PART 2',
            'WELLNESS TIPS',
            'Part 2',
            'Wellness Tips',
            'practical lifestyle tips',
            'lifestyle tips',
            'health tips',
            'tips for',
            'recommendations'
        ]
        
        tips_start = -1
        tips_marker_used = None
        for marker in split_markers:
            idx = cleaned_response.find(marker)
            if idx > 0:
                tips_start = idx
                tips_marker_used = marker
                break
        
        if tips_start > 0:
            # Split at the tips section
            summary = cleaned_response[:tips_start].strip()
            tips = cleaned_response[tips_start:].strip()
            
            # Remove the marker from tips
            if tips_marker_used and tips.startswith(tips_marker_used):
                tips = tips[len(tips_marker_used):].strip()
                # Remove leading dash, colon, or hyphen
                tips = tips.lstrip(' -:—')
        else:
            # No clear split, put everything in summary
            summary = cleaned_response.strip()
            tips = ""
        
        # Clean up summary - remove PART 1 header and explanation section markers
        summary_markers_to_remove = [
            'PART 1',
            'Part 1', 
            'UNDERSTANDING YOUR RESULTS',
            'Understanding Your Results',
            'Explanation of Abnormal Results',
            'Brief Overall Summary',
            '1. Brief Overall Summary',
            '2. Explanation of Abnormal Results'
        ]
        for marker in summary_markers_to_remove:
            if marker in summary:
                summary = summary.replace(marker, '').strip()
                summary = summary.lstrip(' -:—\n')
        
        # Clean up tips - remove section markers
        tips_markers_to_remove = [
            '3. Practical Lifestyle Tips',
            'Practical Lifestyle Tips',
            '4. Any Values That Might Need Urgent Attention'
        ]
        for marker in tips_markers_to_remove:
            if marker in tips:
                tips = tips.replace(marker, '').strip()
                tips = tips.lstrip(' -:—\n')
        
        # Clean up formatting
        summary = self._clean_formatting(summary)
        tips = self._clean_formatting(tips)
        
        return {
            "summary": summary,
            "tips": tips,
            "disclaimer": DISCLAIMER
        }
    
    def _clean_formatting(self, text: str) -> str:
        """Clean up text formatting"""
        if not text:
            return ""
        
        # Remove excessive newlines (more than 2 in a row)
        import re
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove common trailing disclaimers that repeat what we already know
        trailing_patterns = [
            r'\*\*Please remember:.*$',
            r'Please remember:.*$',
            r'\*\*Important:.*consult.*doctor.*$',
            r'Important:.*consult.*doctor.*$',
            r'\*\*Note:.*medical advice.*$',
            r'Note:.*medical advice.*$'
        ]
        for pattern in trailing_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Convert numbered lists (1., 2., etc.) to bullet points for better display
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append('')
                continue
            
            # Check if line starts with number and period (1., 2., etc.)
            match = re.match(r'^(\d+)\.\s*(.+)', line)
            if match:
                # Convert to bullet point
                content = match.group(2)
                formatted_lines.append(f'• {content}')
            else:
                # Check if line starts with ** (markdown bold for list items)
                if line.startswith('*') and not line.startswith('**'):
                    # Already a list item, clean it up
                    formatted_lines.append(line)
                else:
                    formatted_lines.append(line)
        
        # Remove empty lines at start and end
        while formatted_lines and not formatted_lines[0]:
            formatted_lines.pop(0)
        while formatted_lines and not formatted_lines[-1]:
            formatted_lines.pop()
        
        return '\n'.join(formatted_lines)
    
    def _extract_warnings(self, text: str) -> str:
        """Extract any urgent warnings from the text"""
        warning_keywords = ["urgent", "immediate", "critical", "emergency", "seek medical"]
        lines = text.split('\n')
        warnings = [line for line in lines if any(kw in line.lower() for kw in warning_keywords)]
        return '\n'.join(warnings) if warnings else ""
    
    def _fallback_explanation(self, results: List[ParsedLabResult], report_type: str) -> Dict[str, str]:
        """Fallback to rule-based explanation if AI is unavailable"""
        from explanation_service import generate_explanation
        return generate_explanation(results, report_type)
    
    def generate_health_insights(self, historical_results: List[Dict]) -> str:
        """
        Generate insights from historical lab results showing trends
        
        Args:
            historical_results: List of dicts with test results over time
            
        Returns:
            AI-generated insights about trends
        """
        if not self.enabled:
            return "Historical analysis requires AI service (coming soon)"
        
        try:
            # Format historical data
            history_text = self._format_historical_data(historical_results)
            
            prompt = f"""Analyze these lab results over time and identify any trends or patterns:

{history_text}

Please provide:
1. Notable trends (improving, worsening, or stable)
2. Any concerning patterns
3. Positive changes to celebrate
4. Suggestions for discussion with doctor

Keep it simple and encouraging."""
            
            # Call AI based on provider
            if self.provider == "gemini":
                system_prompt = "You are a helpful health assistant analyzing lab trends."
                full_prompt = f"{system_prompt}\n\n{prompt}"
                response = self.client.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 800,
                    }
                )
                return response.text
            else:
                # OpenAI
                from openai import OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful health assistant analyzing lab trends."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=800
                )
                return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Historical analysis failed: {e}")
            return "Unable to generate historical analysis at this time."
    
    def _format_historical_data(self, historical_results: List[Dict]) -> str:
        """Format historical results for AI"""
        lines = []
        for entry in historical_results:
            date = entry.get('date', 'Unknown date')
            test = entry.get('test_name', 'Unknown test')
            value = entry.get('value', 'N/A')
            lines.append(f"{date}: {test} = {value}")
        return "\n".join(lines)


# Singleton instance
_ai_service = None

def get_ai_service() -> AIService:
    """Get or create AI service singleton"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
