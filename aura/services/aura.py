from users.models import User
from decimal import Decimal
from aura.models import ChatMessage
from ..utils import format_history
from .llm import onboarding_model, checkin_model, general_model
from .tools import finalize_onboarding, finish_check_in


def process_aura_chat(user, message, session_type, llm_model, tool_handler=None):
    """Universal handler for all chat types."""
    text = message.get("text", "")
    chat_id = str(message["chat"]["id"])

    # Log User Message
    ChatMessage.objects.create(
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
    ChatMessage.objects.create(
        chat_id=chat_id, role="assistant", content=ai_reply, session_type=session_type
    )

    return ai_reply


def handle_onboarding_message(user, message):
    def onboarding_tool_logic(user, tool_data):
        if tool_data["name"] == "finalize_onboarding":
            finalize_onboarding(user_id=user.id, **tool_data["arguments"])
            return "Great—your profile is fully set up!"
    
    return process_aura_chat(user, message, "onboarding", onboarding_model, onboarding_tool_logic)
        


def handle_checkin_message(user, message):
    def checkin_tool_logic(user, tool_data):
        if tool_data["name"] == "finish_check_in":
            finish_check_in(user_id=user.id, **tool_data["arguments"])
            return "Your checkin is complete!"
            
    return process_aura_chat(user, message, "check_in", checkin_model, checkin_tool_logic)

def handle_general_message(user, message):
    return process_aura_chat(user, message, "general", general_model)