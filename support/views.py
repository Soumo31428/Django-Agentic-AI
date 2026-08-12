from django.shortcuts import render, get_object_or_404
import json
from django.http import JsonResponse
import time
from django.contrib.auth.decorators import login_required
from orders.models import Order
from support.agents import run_support_agent
from .models import Conversation, Message

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


