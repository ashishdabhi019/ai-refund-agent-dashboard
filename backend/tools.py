from crm_data import CRM_DATABASE
from refund_policy import REFUND_POLICY
from datetime import datetime, date

def lookup_order(order_id: str) -> dict:
    """Look up customer order from CRM"""
    order = CRM_DATABASE.get(order_id.upper())
    if not order:
        return {"error": f"Order {order_id} not found in CRM database"}
    return order

def check_refund_eligibility(order_id: str) -> dict:
    """Check if order is eligible for refund based on policy"""
    order = CRM_DATABASE.get(order_id.upper())
    if not order:
        return {"eligible": False, "reason": "Order not found"}
    
    # Mock today as 2025-06-18 to match database dates
    today = date(2025, 6, 18)
    purchase_date = datetime.strptime(order["purchase_date"], "%Y-%m-%d").date()
    days_since_purchase = (today - purchase_date).days
    
    # Check digital products
    if order["is_digital"]:
        return {"eligible": False, "reason": "Digital products are not eligible for refund per policy"}
    
    # Check sale items
    if order["is_sale_item"]:
        return {"eligible": False, "reason": "Sale/clearance items are final sale - no refunds"}
    
    # Check time window (VIP gets 45 days, others get 30)
    time_limit = 45 if order["tier"] in ["Gold", "Platinum"] else 30
    if days_since_purchase > time_limit:
        return {"eligible": False, "reason": f"Refund window expired. Purchase was {days_since_purchase} days ago. Limit is {time_limit} days for {order['tier']} tier"}
    
    # Check delivery status
    if order["delivery_status"] == "Not Delivered":
        return {"eligible": True, "reason": "Item not delivered - eligible for full refund"}
    
    # Check item condition
    condition_map = {
        "Damaged": "Item arrived damaged - eligible for refund",
        "Wrong Item": "Wrong item delivered - eligible for full refund",
        "Defective": "Item is defective within 30 days - eligible for refund"
    }
    if order["item_condition"] in condition_map:
        # Check 90-day refund limit
        if order["last_refund_date"]:
            last_refund = datetime.strptime(order["last_refund_date"], "%Y-%m-%d").date()
            if (today - last_refund).days < 90:
                return {"eligible": False, "reason": "Customer already received a refund within the last 90 days"}
        return {"eligible": True, "reason": condition_map[order["item_condition"]]}
    
    # Used/altered items
    if order["item_condition"] == "Used":
        return {"eligible": False, "reason": "Used or altered items are not eligible for refund"}
    
    return {"eligible": False, "reason": "No valid reason for refund found based on current policy"}

def approve_refund(order_id: str) -> dict:
    """Approve and process the refund"""
    order = CRM_DATABASE.get(order_id.upper())
    if not order:
        return {"success": False, "message": "Order not found"}
    
    # Update CRM in-memory database status
    order["delivery_status"] = "Refunded"
    order["last_refund_date"] = date(2025, 6, 18).strftime("%Y-%m-%d")

    return {
        "success": True,
        "message": f"Refund of ₹{order['amount']} approved for {order['name']}",
        "refund_amount": order["amount"],
        "timeline": "5-7 business days",
        "customer_email": order["email"]
    }

def deny_refund(order_id: str, reason: str) -> dict:
    """Deny the refund with a reason"""
    order = CRM_DATABASE.get(order_id.upper())
    customer_name = order["name"] if order else "Customer"
    return {
        "success": True,
        "message": f"Refund denied for {customer_name}",
        "reason": reason
    }

def get_policy() -> dict:
    """Return the refund policy"""
    return {"policy": REFUND_POLICY}

# Tool definitions for Claude API
TOOLS = [
    {
        "name": "lookup_order",
        "description": "Look up a customer order from the CRM database using Order ID",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The order ID (e.g., ORD001)"}
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "check_refund_eligibility",
        "description": "Check if an order is eligible for a refund based on the refund policy",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The order ID to check"}
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "approve_refund",
        "description": "Approve and process a refund for an eligible order",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The order ID to approve refund for"}
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "deny_refund",
        "description": "Deny a refund request with a specific reason",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The order ID"},
                "reason": {"type": "string", "description": "Clear reason for denial"}
            },
            "required": ["order_id", "reason"]
        }
    },
    {
        "name": "get_policy",
        "description": "Retrieve the full refund policy document",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]

def execute_tool(tool_name: str, tool_input: dict):
    """Execute a tool by name"""
    tool_map = {
        "lookup_order": lookup_order,
        "check_refund_eligibility": check_refund_eligibility,
        "approve_refund": approve_refund,
        "deny_refund": deny_refund,
        "get_policy": get_policy
    }
    func = tool_map.get(tool_name)
    if func:
        return func(**tool_input)
    return {"error": f"Unknown tool: {tool_name}"}