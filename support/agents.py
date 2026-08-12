from google import genai
from google.genai import types
from django.conf import settings
from .tools import get_order_details, get_refund_history, check_delivery_status
from .models import Conversation, Message, AgentLog

## Initialize the client
client = genai.Client(api_key=settings.GEMINI_API_KEY)
gemini_model = settings.GEMINI_MODEL


## SUPPORT SYSTEM PROMPT    --->   Maya's job description
SUPPORT_SYSTEM_PROMPT = """
You are Maya, a customer support agent at CoolBreeze AC.
You help customers with issues related to their AC orders.

Your responsibilities:
- Always use your tools to gather facts before responding
- Check order details when customer mentions their order
- Check refund history before making any refund decisions
- Be empathetic but honest

Your personality:
- Friendly and professional
- Patient even when customer is angry
- Clear and concise in your replies
- No emojies

Important rules:
- Always check order details first before responding
- Never approve or deny a refund yourself
- If refund decision is needed — tell customer you are checking with your team
- Never use bold text, bullet points or any markdown formatting. Plain text only.
- Keep replies concise and conversational. Maximum 3-4 sentences. No long paragraphs.

"""

## SUPPORT TOOLS     -->>    Tools schemas, that AI agents will read
SUPPORT_TOOLS = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="get_order_details",
                description="Fetch complete order details including status, carrier, tracking number and days since order was placed. Use this when customer mentions their order or complains about delivery.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "order_id": types.Schema(
                            type="INTEGER",
                            description="The order ID to look up"
                        )
                    },
                    required=["order_id"]
                )
            ),
            types.FunctionDeclaration(
                name="get_refund_history",
                description="Get complete refund history for a user. Use this before making any refund related decisions.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "user_id": types.Schema(
                            type="INTEGER",
                            description="The user ID to check refund history for"
                        )
                    },
                    required=["user_id"]
                )
            ),
            types.FunctionDeclaration(
                name="check_delivery_status",
                description="Check current delivery status using tracking number and carrier. Use this when customer complains about delayed or missing delivery.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "tracking_number": types.Schema(
                            type="STRING",
                            description="The shipment tracking number"
                        ),
                        "carrier": types.Schema(
                            type="STRING",
                            description="The carrier name for example BlueDart or Delhivery"
                        )
                    },
                    required=["tracking_number", "carrier"]
                )
            ),
            types.FunctionDeclaration(
                name="escalate_to_manager",
                description="Escalate the case to manager for refund decision. Always include customer's user_id in the case summary so manager can assess fraud risk accurately.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "case_summary": types.Schema(
                            type="STRING",
                            description="Complete case summary. Must include: customer user_id, order details, refund history and complaint. Format: Start with 'Customer User ID: X' on the first line."
                        )
                    },
                    required=["case_summary"]
                )
            ),
            types.FunctionDeclaration(
                name="search_knowledge_base",
                description="Search CoolBreeze AC company documents including refund policy, warranty policy, and product FAQs. Use this when customer asks about company policies, warranty coverage, warranty claims, refund eligibility, or any general product information that requires accurate company documentation.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "query": types.Schema(
                            type="STRING",
                            description="The search query to find relevant information from company documents. Be specific — for example 'refund eligibility within 30 days' instead of just 'refund'."
                        )
                    },
                    required=["query"]
                )
            )
        ]
    )
]


## execute_tool()  --> bridge between gemini and python functions

def execute_tool(tool_name, tool_input, conversation_id=None):
    if tool_name == "get_order_details":
        return get_order_details(tool_input["order_id"])
    
    if tool_name == "get_refund_history":
        return get_refund_history(tool_input["user_id"])
    
    if tool_name == "check_delivery_status":
        return check_delivery_status(tool_input["tracking_number"], tool_input["carrier"])
    '''
    if tool_name == "escalate_to_manager":
            case_summary = tool_input["case_summary"]
            print("escalating to manager=====>", case_summary)
            decision = run_manager_agent(case_summary, conversation_id)
            print("decision===>", decision)
            return decision
        
        if tool_name == 'assess_fraud_risk':
            user_id = tool_input['user_id']
            print("Consulting risk agent for user==>", user_id)
            verdict = run_risk_agent(user_id, conversation_id)
            print("risk verdict==>", verdict)
            return verdict
        
        if tool_name == 'get_customer_risk_profile':
            return get_customer_risk_profile(tool_input['user_id'])
        
        if tool_name == "search_knowledge_base":
            return search_knowledge_base(tool_input["query"])
    '''


## Agent Loop  -->  while loop that loops until the task is done.

def run_support_agent(user_message, conversation_id, order_id, user_id):
    conv = Conversation.objects.get(id=conversation_id)

    # Format history strictly according to SDK requirements
    conversation_messages= []
    for msg in conv.message.order_by("created_at"):
        role = "model" if msg.role == "agent" else msg.role
        conversation_messages.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg.content)]
            )
        )
    while True:
        response = client.models.generate_content(
            model=gemini_model,
            contents=conversation_messages,
            config=types.GenerateContentConfig(
                system_instruction=SUPPORT_SYSTEM_PROMPT + f"\n\nContext: This conversation is about Order #{order_id}, user: {user_id}",
                tools=SUPPORT_TOOLS,
                max_output_tokens=1024,
            )
        )
        
        if response.function_calls:
            conversation_messages.append(response.candidates[0].content)

            tool_response_parts = []
            for call in response.function_calls:
                event = {"type": "tool_call", "message": f"Calling tool {call.name} with {call.args}"}
               
                
                AgentLog.objects.create(conversation=conv, event_type="tool_call", message=f"Calling tool {call.name} with {call.args}")

                result = execute_tool(call.name, call.args, conversation_id)

                event = {"type": "tool_result", "message": f"{call.name} returned: {str(result)[:200]}"}
               

                AgentLog.objects.create(conversation=conv, event_type="tool_result", message=f"{call.name} returned: {str(result)[:200]}")
                print('executing tool==>', call.name)
                print('call.args===>', call.args)

                tool_response_parts.append(
                    types.Part.from_function_response(
                        name=call.name,
                        response={"result": str(result)}
                    )
                )

            conversation_messages.append(
                types.Content(
                    role="user",
                    parts=tool_response_parts
                )
            )

        else:
            final_reply = response.text
            event = {"type": "final", "message": final_reply}
           
            AgentLog.objects.create(conversation=conv, event_type="final", message=final_reply)

            print("Running raw implementation")
            return final_reply