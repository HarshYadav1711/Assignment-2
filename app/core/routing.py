"""
Dynamic routing logic for LLM interactions.
Analyzes conversation context to determine optimal response strategy.
"""

from typing import Dict, Any, List
from app.core.state import SessionState, Message


class RoutingStrategy:
    """Enumeration of routing strategies."""
    FAST_CONCISE = "fast_concise"  # Short factual queries
    ANALYTICAL = "analytical"  # Deep reasoning required
    SUMMARIZATION_AWARE = "summarization_aware"  # Nearing session end
    TOOL_HEAVY = "tool_heavy"  # Multiple tool invocations expected


def analyze_conversation_context(state: SessionState) -> Dict[str, Any]:
    """
    Analyze conversation to determine routing strategy.
    
    This function implements the "dynamic multi-step routing" requirement.
    It considers:
    - Message count (conversation depth)
    - Tool usage patterns
    - Message length and complexity
    - Recent conversation patterns
    
    Returns:
        Dictionary with routing decision and metadata
    """
    messages = state.messages
    message_count = state.message_count
    tool_call_count = state.tool_call_count
    
    # Determine strategy based on context
    strategy = RoutingStrategy.FAST_CONCISE
    reasoning = []
    
    # Check conversation depth
    if message_count > 10:
        strategy = RoutingStrategy.SUMMARIZATION_AWARE
        reasoning.append("Deep conversation, preparing for potential summarization")
    
    # Check for analytical patterns
    if messages:
        last_user_msg = None
        for msg in reversed(messages):
            if msg.role == "user":
                last_user_msg = msg
                break
        
        if last_user_msg:
            content_lower = last_user_msg.content.lower()
            analytical_keywords = ["analyze", "explain", "why", "how", "compare", "evaluate"]
            if any(keyword in content_lower for keyword in analytical_keywords):
                strategy = RoutingStrategy.ANALYTICAL
                reasoning.append("Analytical query detected")
    
    # Check tool usage
    if tool_call_count > 2:
        strategy = RoutingStrategy.TOOL_HEAVY
        reasoning.append("High tool usage, expecting more tool calls")
    
    # Determine verbosity
    verbosity = "concise"
    if strategy == RoutingStrategy.ANALYTICAL:
        verbosity = "detailed"
    elif strategy == RoutingStrategy.SUMMARIZATION_AWARE:
        verbosity = "balanced"
    
    return {
        "strategy": strategy,
        "verbosity": verbosity,
        "reasoning": reasoning,
        "message_count": message_count,
        "tool_call_count": tool_call_count
    }


def get_system_prompt(routing_decision: Dict[str, Any]) -> str:
    """
    Generate system prompt based on routing decision.
    
    This implements dynamic prompt engineering based on context.
    
    Args:
        routing_decision: Output from analyze_conversation_context
        
    Returns:
        System prompt string
    """
    strategy = routing_decision["strategy"]
    verbosity = routing_decision["verbosity"]
    
    base_prompt = """You are a helpful AI assistant in a real-time conversational system.
You have access to tools that can fetch knowledge and contextual data.
Use tools when appropriate to provide accurate, helpful responses."""
    
    if strategy == RoutingStrategy.FAST_CONCISE:
        return f"""{base_prompt}

Current mode: Fast and concise responses.
- Provide direct, factual answers
- Use tools only when necessary
- Keep responses brief and focused"""
    
    elif strategy == RoutingStrategy.ANALYTICAL:
        return f"""{base_prompt}

Current mode: Analytical reasoning.
- Provide detailed explanations
- Break down complex topics
- Use tools to gather supporting information
- Show your reasoning process"""
    
    elif strategy == RoutingStrategy.SUMMARIZATION_AWARE:
        return f"""{base_prompt}

Current mode: Summarization-aware.
- This conversation may be ending soon
- Provide balanced, comprehensive responses
- Help wrap up topics naturally
- Be mindful of conversation closure"""
    
    elif strategy == RoutingStrategy.TOOL_HEAVY:
        return f"""{base_prompt}

Current mode: Tool-heavy interaction.
- Expect to use multiple tools
- Chain tool calls when appropriate
- Provide structured, tool-enhanced responses"""
    
    return base_prompt

