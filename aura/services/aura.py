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
                f"Your profile is officially set up. Based on our chat, I’ve categorized you as **{data['behavioral_tag']}**.\n\n"
                f"It’s a solid starting point on your journey to becoming a PAW. You can continue to chat with me for advice "
                f"at any time, but I’ll reach out for our first progress check-in based on your **{data['check_in_frequency']}** preference.\n\n"
                f"**Your immediate Action Plan:**\n{data['action_plan']}"
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
                    feedback = f"Excellent. Your wealth has grown by {velocity:,.2f} since our last session—true PAW behavior."
                elif velocity == 0:
                    feedback = "Audit complete. Your balance is holding steady, but we should look for ways to increase your velocity."
                else:
                    feedback = f"Check-in finished. Your balance has dipped by {abs(velocity):,.2f}. Let’s focus on tightening the efficiency."

                return (
                    f"{feedback}\n\n"
                    f"As a **{tag}**, here is your action plan until our next sync:\n"
                    f"{plan}"
                )
            return "Check-in failed. Please try again."
            
    return process_aura_chat(user, message, "check_in", checkin_model, checkin_tool_logic)


def handle_general_message(user, message):
    return process_aura_chat(user, message, "general", general_model)