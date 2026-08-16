from django.shortcuts import render, get_object_or_404
import json
from django.http import JsonResponse
import time
from django.contrib.auth.decorators import login_required
from orders.models import Order
from support.agents import run_support_agent
from .models import Conversation, Message
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.

@login_required
def chat(request, order_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        user_message = data.get("message")

        if not user_message:
            return JsonResponse({"error": "Emptymessage"}, status= 400)

        order = get_object_or_404(Order, id = order_id, user=request.user)

        conversation, created = Conversation.objects.get_or_create(user=request.user, order=order)

        Message.objects.create(conversation=conversation, role="user", content = user_message)

        ## send user message and conversation to LLM
        try:
            reply = run_support_agent(user_message, conversation.id,order.id, request.user.id)
        except Exception as e:
            return JsonResponse({"error": f"Agent error: {e}"}, status=500)
        ## store the LLM reply
        Message.objects.create(conversation=conversation, role="agent", content = reply)
    
        return JsonResponse({"reply": reply})

@staff_member_required
def dashboard(request):
    conversations = Conversation.objects.all().order_by("-created_at")
    print("conversations ====>", conversations)
    context = {
        'conversations': conversations
    }
    return render(request, "support/dashboard.html", context)

def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    messages = conversation.message.order_by("created_at")
    agentlogs = conversation.agentlogs.order_by("created_at")
    context = {
        'conversation': conversation,
        'messages': messages,
        'agentlogs': agentlogs,
    }
    return render(request, 'support/conversation_detail.html', context)

