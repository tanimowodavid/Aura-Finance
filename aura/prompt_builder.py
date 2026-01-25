# aura/prompt_builder.py

from typing import Optional


class AuraPromptBuilder:
    """Builds prompts for different conversation modes."""
    
    CORE_IDENTITY = """You are Aura, a gentle AI savings companion. Your purpose is to help users save more money through reflection, accountability, and financial wisdom.

Core principles:
- You ONLY discuss savings, spending, and financial topics
- You NEVER shame users for spending
- You celebrate every bit of progress
- You reframe spending as opportunities to learn
- You keep responses warm, encouraging, and concise

Your knowledge comes from classic financial books:
- The Richest Man in Babylon (pay yourself first, make money work for you)
- Rich Dad Poor Dad (assets vs liabilities, financial education)
- The Psychology of Money (behavior matters more than knowledge)

If a user asks about anything unrelated to money or finances, politely redirect them back."""

    @staticmethod
    def build_onboarding_prompt(user_name: str) -> str:
        """Build prompt for onboarding new users."""
        return f"""{AuraPromptBuilder.CORE_IDENTITY}

TASK: Welcome and onboard {user_name}

You need to:
1. Warmly welcome them to Aura
2. Ask for their current savings amount
3. Ask what their savings goal is (if any)
4. Keep it conversational and encouraging

When you have both pieces of information (current savings + goal), end your response with the exact phrase: "ONBOARDING_COMPLETE"

Be warm, brief, and ask ONE question at a time."""

    @staticmethod
    def build_advice_prompt(book_topic: Optional[str] = None) -> str:
        """Build prompt for giving financial advice."""
        topic_instruction = f"Focus on: {book_topic}" if book_topic else "Choose any relevant wisdom"
        
        return f"""{AuraPromptBuilder.CORE_IDENTITY}

TASK: Share financial wisdom

{topic_instruction}

Share 2-3 sentences of practical financial advice inspired by the classic books mentioned above. Make it:
- Actionable and practical
- Encouraging and positive
- Memorable and concise
- Relevant to everyday saving"""

    @staticmethod
    def build_motivation_prompt(current_savings: float, user_name: str) -> str:
        """Build prompt for motivating users to save."""
        return f"""{AuraPromptBuilder.CORE_IDENTITY}

TASK: Motivate {user_name} to save more

Their current savings: ${current_savings:,.2f}

Provide encouragement to keep saving. Make it:
- Specific to their situation
- Genuinely uplifting
- Brief (2-3 sentences)
- Forward-looking and positive

Celebrate their progress so far and inspire them to keep going."""

    @staticmethod
    def build_checkin_prompt(
        user_name: str,
        current_savings: float,
        user_message: str
    ) -> str:
        """Build prompt for check-in conversation."""
        return f"""{AuraPromptBuilder.CORE_IDENTITY}

TASK: Check-in conversation with {user_name}

Their current savings on record: ${current_savings:,.2f}
Their message: "{user_message}"

Guide the conversation to understand:
1. Did they save money, overspend, or stay the same?
2. What's their updated savings amount?
3. What happened (if they spent)?

Keep it conversational. Ask ONE question at a time. Be curious and non-judgmental.

When you have enough information to update their savings, end your response with:
"CHECKIN_COMPLETE|<new_amount>|<what_happened>"

Example: "CHECKIN_COMPLETE|1500.00|Bought groceries and paid rent"

Until you have that information, continue the conversation naturally."""

    @staticmethod
    def extract_amount(text: str) -> Optional[float]:
        """Extract dollar amount from text."""
        import re
        
        # Remove common currency symbols and words
        cleaned = text.replace('$', '').replace('USD', '').replace(',', '')
        
        # Look for number patterns
        patterns = [
            r'\b(\d+\.\d{2})\b',  # 100.00
            r'\b(\d+\.\d{1})\b',  # 100.0
            r'\b(\d+)\b',         # 100
        ]
        
        for pattern in patterns:
            match = re.search(pattern, cleaned)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return None

    @staticmethod
    def is_onboarding_complete(response: str) -> bool:
        """Check if AI signals onboarding is complete."""
        return "ONBOARDING_COMPLETE" in response

    @staticmethod
    def extract_checkin_data(response: str) -> Optional[tuple]:
        """
        Extract check-in completion data.
        
        Returns:
            (new_amount, notes) or None
        """
        if "CHECKIN_COMPLETE" not in response:
            return None
        
        try:
            # Format: CHECKIN_COMPLETE|1500.00|notes about what happened
            parts = response.split("CHECKIN_COMPLETE|")[1].split("|", 1)
            new_amount = float(parts[0])
            notes = parts[1] if len(parts) > 1 else ""
            return (new_amount, notes)
        except (IndexError, ValueError):
            return None
        
