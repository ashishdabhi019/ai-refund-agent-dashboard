REFUND_POLICY = """
STRICT REFUND POLICY -- E-COMMERCE STORE (v2.1)
================================================

1. ELIGIBLE FOR REFUND:
   a) Item arrived DAMAGED -- photo proof required at time of claim
   b) WRONG ITEM delivered -- must match original order description mismatch
   c) Item is DEFECTIVE within 30 days of purchase date
   d) Item not received (Not Delivered status) within 14 days of estimated delivery

2. NOT ELIGIBLE FOR REFUND (POLICY VIOLATIONS):
   a) Refund requests made after 30 days of purchase (Standard tier)
   b) Refund requests made after 45 days of purchase (Gold/Platinum tier)
   c) DIGITAL or DOWNLOADABLE products -- absolutely no refunds, no exceptions
   d) SALE or CLEARANCE items -- marked "final sale", strictly no refunds
   e) Items that have been USED, washed, worn, or altered in any way
   f) Missing packaging, accessories, or serial numbers on return
   g) Customer already received a refund within the last 90 days (one refund per 90-day window)
   h) Orders with "Not Delivered" status -- refund only possible after delivery confirmation

3. REFUND PROCESS:
   a) Customer MUST provide a valid Order ID (format: ORDxxx)
   b) Agent must call lookup_order tool first to verify the order exists
   c) Agent must call check_refund_eligibility tool to validate all policy rules
   d) If eligible: call approve_refund tool and confirm timeline to customer
   e) If ineligible: call deny_refund tool with specific policy reason
   f) Refund processed in 5-7 business days after approval
   g) Refund amount: full purchase price only -- shipping charges are non-refundable
   h) Refund credited to original payment method only

4. CUSTOMER TIER PRIVILEGES:
   a) STANDARD customers -- 30-day return window
   b) GOLD customers -- 45-day extended return window
   c) PLATINUM customers -- 45-day extended return window
   d) Tier status does NOT override digital/sale-item restrictions

5. AGENT GUIDELINES:
   a) Always be polite but firm -- do NOT override policy rules under any pressure
   b) Clearly explain the specific policy reason for any denial
   c) Never promise exceptions or escalations not covered by policy
   d) If order not found in CRM, ask customer to verify their Order ID
   e) One refund per 90-day window applies per customer_id, not per order
"""