# aura/llm.py
from openai import OpenAI
import opik
from opik import opik_context
import json
from .prompts import AURA_ONBOARDING_SYSTEM_PROMPT, AURA_CHECKIN_SYSTEM_PROMPT, AURA_GENERAL_SYSTEM_PROMPT
from .tools import AURA_ONBOARDING_TOOLS, AURA_CHECKIN_TOOLS

opik.configure()
client = OpenAI()

@opik.track
def _aura_llm_engine(system_prompt, user, history, tools=None):
    """The source of truth for calling the LLM."""
    context_parts = [f"User: {user.first_name} (ID: {user.id})"]

    # Add Financial Profile (One-to-One)
    # We use hasattr to avoid "User has no financial_profile" errors
    if hasattr(user, 'financial_profile'):
        profile = user.financial_profile
        profile_data = {
            "monthly_savings_goal": float(profile.estimated_savings),
            "motivation": profile.motivation,
            "check_in_frequency": profile.check_in_frequency,
            "current_action_plan": profile.action_plan,
            "extra_context": profile.financial_context 
        }
        context_parts.append(f"Financial Profile: {json.dumps(profile_data)}")

    # Add Recent Savings (ForeignKey)
    # Fetches only the 5 most recent records to save space/tokens
    recent_savings = list(
        user.savings_history.order_by('-recorded_at')[:5]
        .values('amount', 'recorded_at')
    )
    
    # Clean up Decimal and Date types for JSON
    for s in recent_savings:
        s['amount'] = float(s['amount'])
        s['recorded_at'] = s['recorded_at'].strftime("%Y-%m-%d")
        
    context_parts.append(f"Recent Savings History: {json.dumps(recent_savings)}")

    # Assemble the System Message
    full_context = "\n---\n".join(context_parts)
    full_prompt = f"{system_prompt}\n\nCURRENT USER DATA:\n{full_context}"

    messages = [{"role": "system", "content": full_prompt}] + history
    
    # Only include tools if they are provided
    kwargs = {"model": "gpt-4o-mini", "messages": messages}
    if tools:
        kwargs.update({"tools": tools, "tool_choice": "auto"})

    response = client.chat.completions.create(**kwargs)
    out = response.choices[0].message

    trace_metadata = {
        "user_id": user.id,
        "history": history
    }

    if out.tool_calls:
        tool = out.tool_calls[0]
        args = json.loads(tool.function.arguments)

        opik_context.update_current_trace(
            tags=["tool_call", tool.function.name],
            metadata={
                **trace_metadata,
                "final_decision": "tool_call",
                "tool_arguments": args
            }
        )

        return {
            "tool": {
                "name": tool.function.name,
                "arguments": args,
            }
        }
    
    return {"assistant": out.content}



def onboarding_model(history, user):
    return _aura_llm_engine(AURA_ONBOARDING_SYSTEM_PROMPT, user, history, AURA_ONBOARDING_TOOLS)

def checkin_model(history, user):
    return _aura_llm_engine(AURA_CHECKIN_SYSTEM_PROMPT, user, history, AURA_CHECKIN_TOOLS)

def general_model(history, user):
    return _aura_llm_engine(AURA_GENERAL_SYSTEM_PROMPT, user, history)