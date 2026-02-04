from users.models import User
from decimal import Decimal
from aura.models import ChatMessageLog
from ..utils import format_history
from .llm import onboarding_model, checkin_model, general_model
from .tools import finalize_onboarding, finish_check_in


# =================================
# Core Chat Processing Function
# =================================
def process_aura_chat(user, message, session_type, llm_model, tool_handler=None):
    text = message.get("text", "")
    chat_id = str(message["chat"]["id"])

    # Log User Message
    ChatMessageLog.objects.create(
        chat_id=chat_id, role="user", content=text, session_type=session_type
    )

    # Get LLM Response
    history = format_history(chat_id, session_type=session_type)
    response = llm_model(history, user)

    # Handle Tool Calls (The Dynamic Part)
    if "tool" in response and tool_handler:
        return tool_handler(user, response["tool"])

    # Handle Text Reply
    ai_reply = response.get("assistant", "I'm sorry, I couldn't process that.")
    
    # Log Assistant Message
    ChatMessageLog.objects.create(
        chat_id=chat_id, role="assistant", content=ai_reply, session_type=session_type
    )

    return ai_reply


# ========================================
# Handlers for Different Message Types
# ========================================
def handle_onboarding_message(user, message):
    def onboarding_tool_logic(user, tool_data):
        if tool_data["name"] == "finalize_onboarding":
            data = finalize_onboarding(user_id=user.id, **tool_data["arguments"])
            return (
                f"Your profile is officially set up! Based on our chat, I’ve tailored your "
                f"coaching strategy to help you stay consistent and build that bulletproof saving habit.\n\n"
                
                f"I’ll reach out for our first progress audit based on your **{data['check_in_frequency']}** preference, "
                f"but you can message me anytime if you’re feeling tempted to spend or need a quick tip.\n\n"
                
                f"**Your first habit-building task:**\n{data['action_plan']}\n\n"
            )
    
    return process_aura_chat(user, message, "onboarding", onboarding_model, onboarding_tool_logic)
        

def handle_checkin_message(user, message):
    def checkin_tool_logic(user, tool_data):
        if tool_data["name"] == "finish_check_in":
            # Capture the calculated data from the function
            res = finish_check_in(user_id=user.id, **tool_data["arguments"])
            
            if res["status"] == "success":
                velocity = res["velocity"]
                tag = res["behavioral_tag"]
                plan = res["action_plan"]
                
                # Dynamic feedback based on velocity
                if res["is_up"]:
                    feedback = f"Great work! You’ve added {velocity:,.2f} to your savings since we last spoke. Your consistency is paying off! 🦾🥳"
                elif velocity == 0:
                    feedback = "Audit complete. You’ve held steady—no ground lost, but let’s see if we can spark some growth before our next sync."
                else:
                    feedback = f"Audit finished. It looks like {abs(velocity):,.2f} left your savings. No stress—let’s look at what happened and adjust our strategy."

                return (
                    f"{feedback}\n\n"
                    f"**Your tailored habit-building plan:**\n"
                    f"{plan}"
                )
            return "Check-in failed. Please try again."


            
    return process_aura_chat(user, message, "check_in", checkin_model, checkin_tool_logic)


def handle_general_message(user, message):
    return process_aura_chat(user, message, "general", general_model)