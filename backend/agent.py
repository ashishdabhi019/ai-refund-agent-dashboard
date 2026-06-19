import os
import re
import json
from tools import TOOLS, execute_tool
from refund_policy import REFUND_POLICY

# Detect key mode
groq_key = os.environ.get("GROQ_API_KEY", "")
is_groq = bool(groq_key and groq_key != "your_key_here" and groq_key != "")
is_simulation = not is_groq

SYSTEM_PROMPT = f"""You are a strict AI customer support agent for an e-commerce store. 
Your job is to process refund requests by following the policy EXACTLY.

{REFUND_POLICY}

INSTRUCTIONS:
- Always lookup the order first
- Always check refund eligibility using the tool
- Approve ONLY if eligibility check says eligible
- Deny firmly but politely if not eligible
- Explain your reasoning clearly to the customer
- Never override policy rules"""

if is_groq:
    from groq import Groq
    groq_client = Groq(api_key=groq_key)
    
    # Convert tool definitions to Groq format (OpenAI-compatible)
    GROQ_TOOLS = [{
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["input_schema"]
        }
    } for t in TOOLS]

def run_groq_agent(user_message: str, conversation_history: list) -> dict:
    logs = [{"step": "USER_INPUT", "content": user_message}]
    
    # Clean and build messages list
    messages = []
    messages.append({"role": "system", "content": SYSTEM_PROMPT})
    
    # Process history
    if conversation_history:
        for msg in conversation_history:
            if isinstance(msg, dict):
                role = msg.get("role")
                content = msg.get("content")
                
                # Map Gemini role
                if role == "model":
                    role = "assistant"
                
                # Convert Gemini structure content if any
                if isinstance(content, list):
                    text_parts = [block["text"] for block in content if isinstance(block, dict) and block.get("type") == "text"]
                    content = " ".join(text_parts)
                
                if role in ["user", "assistant", "system", "tool"]:
                    new_msg = {"role": role, "content": str(content)}
                    if "name" in msg:
                        new_msg["name"] = msg["name"]
                    if "tool_call_id" in msg:
                        new_msg["tool_call_id"] = msg["tool_call_id"]
                    if "tool_calls" in msg:
                        new_msg["tool_calls"] = msg["tool_calls"]
                    messages.append(new_msg)
            elif hasattr(msg, "role") and hasattr(msg, "content"):
                role = msg.role
                if role == "model":
                    role = "assistant"
                content = msg.content
                messages.append({"role": role, "content": str(content)})

    # Add new user message
    messages.append({"role": "user", "content": user_message})
    
    # Run loop
    try:
        while True:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=GROQ_TOOLS,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            # If no tool calls, this is the final answer!
            if not tool_calls:
                final_text = response_message.content or ""
                logs.append({"step": "FINAL_ANSWER", "content": final_text})
                
                messages.append({"role": "assistant", "content": final_text})
                return {
                    "response": final_text,
                    "logs": logs,
                    "messages": messages
                }
            
            # Add assistant's request with tool calls to history
            tool_calls_list = []
            for tc in tool_calls:
                tool_calls_list.append({
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                })
            
            assistant_msg = {
                "role": "assistant",
                "content": response_message.content or "",
                "tool_calls": tool_calls_list
            }
            messages.append(assistant_msg)
            
            # Execute tool calls
            for tc in tool_calls:
                tool_name = tc.function.name
                tool_input = json.loads(tc.function.arguments)
                
                logs.append({"step": "TOOL_CALL", "tool": tool_name, "input": tool_input})
                result = execute_tool(tool_name, tool_input)
                logs.append({"step": "TOOL_RESULT", "tool": tool_name, "result": result})
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": tool_name,
                    "content": json.dumps(result)
                })
                
    except Exception as e:
        error_msg = str(e)
        if "rate limit" in error_msg.lower() or "429" in error_msg or "ResourceExhausted" in error_msg or "quota" in error_msg.lower():
            friendly_text = "⚠️ **Groq API Rate Limit Exceeded:** The Groq free tier limit has been reached. Please wait a few seconds and try again, or comment out the GROQ_API_KEY in `.env` to use the offline simulator."
        else:
            friendly_text = f"⚠️ **Groq API Error:** {error_msg}"
        
        logs.append({"step": "FINAL_ANSWER", "content": friendly_text})
        return {
            "response": friendly_text,
            "logs": logs,
            "messages": conversation_history
        }

def run_simulation_agent(user_message: str, conversation_history: list) -> dict:
    """Run simulated tool-use flows when live API Key is not set"""
    logs = []
    logs.append({
        "step": "USER_INPUT",
        "content": user_message
    })
    
    # Extract order ID from message or conversation history
    order_id = None
    
    # Try current message
    match = re.search(r'ORD\d+', user_message.upper())
    if match:
        order_id = match.group(0)
    else:
        # Try history
        for msg in reversed(conversation_history):
            content = msg.get("content", "")
            if isinstance(content, str):
                match = re.search(r'ORD\d+', content.upper())
                if match:
                    order_id = match.group(0)
                    break
    
    if not order_id:
        final_answer = "Hello! I am your AI refund support agent. Please provide your Order ID (e.g. ORD001) so I can assist you with your refund request.\n\n*(Note: Running in Simulation Mode. Add a valid GROQ_API_KEY to your .env file to enable the live agent.)*"
        logs.append({
            "step": "FINAL_ANSWER",
            "content": final_answer
        })
        
        # Format messages history for the simulation agent
        updated_history = conversation_history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": [{"type": "text", "text": final_answer}]}
        ]
        return {
            "response": final_answer,
            "logs": logs,
            "messages": updated_history
        }
    
    # Run mock tools
    # 1. Lookup order
    logs.append({
        "step": "TOOL_CALL",
        "tool": "lookup_order",
        "input": {"order_id": order_id}
    })
    
    order = execute_tool("lookup_order", {"order_id": order_id})
    logs.append({
        "step": "TOOL_RESULT",
        "tool": "lookup_order",
        "result": order
    })
    
    if "error" in order:
        final_answer = f"I looked up order ID {order_id} in our CRM database but could not find it. Please verify your order ID and try again.\n\n*(Note: Running in Simulation Mode. Add a valid GROQ_API_KEY to your .env file to enable the live agent.)*"
        logs.append({
            "step": "FINAL_ANSWER",
            "content": final_answer
        })
        updated_history = conversation_history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": [{"type": "text", "text": final_answer}]}
        ]
        return {
            "response": final_answer,
            "logs": logs,
            "messages": updated_history
        }
    
    # 2. Check eligibility
    logs.append({
        "step": "TOOL_CALL",
        "tool": "check_refund_eligibility",
        "input": {"order_id": order_id}
    })
    
    eligibility = execute_tool("check_refund_eligibility", {"order_id": order_id})
    logs.append({
        "step": "TOOL_RESULT",
        "tool": "check_refund_eligibility",
        "result": eligibility
    })
    
    # 3. Approve or deny
    if eligibility.get("eligible"):
        logs.append({
            "step": "TOOL_CALL",
            "tool": "approve_refund",
            "input": {"order_id": order_id}
        })
        refund_result = execute_tool("approve_refund", {"order_id": order_id})
        logs.append({
            "step": "TOOL_RESULT",
            "tool": "approve_refund",
            "result": refund_result
        })
        
        final_answer = f"Hello {order['name']}. I have successfully processed your refund request for your order {order_id} ({order['product']}).\n\n**Refund Status:** APPROVED\n**Amount:** ₹{order['amount']}\n**Timeline:** {refund_result['timeline']}\n**Notification Sent to:** {order['email']}\n\n*(Note: Running in Simulation Mode. Add a valid GROQ_API_KEY to your .env file to enable the live agent.)*"
    else:
        reason = eligibility.get("reason", "Not eligible under standard refund policy")
        logs.append({
            "step": "TOOL_CALL",
            "tool": "deny_refund",
            "input": {"order_id": order_id, "reason": reason}
        })
        deny_result = execute_tool("deny_refund", {"order_id": order_id, "reason": reason})
        logs.append({
            "step": "TOOL_RESULT",
            "tool": "deny_refund",
            "result": deny_result
        })
        
        final_answer = f"Hello {order['name']}. I've checked the details for order {order_id} ({order['product']}). Unfortunately, your refund request has been denied.\n\n**Reason:** {reason}\n\nIf you have any questions, please let me know.\n\n*(Note: Running in Simulation Mode. Add a valid GROQ_API_KEY to your .env file to enable the live agent.)*"
        
    logs.append({
        "step": "FINAL_ANSWER",
        "content": final_answer
    })
    
    # Save to history
    updated_history = conversation_history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": [{"type": "text", "text": final_answer}]}
    ]
    
    return {
        "response": final_answer,
        "logs": logs,
        "messages": updated_history
    }

def run_agent(user_message: str, conversation_history: list) -> dict:
    """Run the appropriate agent depending on API Key status"""
    if is_simulation:
        return run_simulation_agent(user_message, conversation_history)
    else:
        return run_groq_agent(user_message, conversation_history)