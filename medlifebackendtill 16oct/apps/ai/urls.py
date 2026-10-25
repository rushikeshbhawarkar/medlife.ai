# Purpose: AI endpoint routes.
from django.urls import path
from .views import ask_member, prompt, providers

urlpatterns = [
    path("providers/", providers, name="ai-providers"),
    path("prompt/", prompt, name="prompt"),
    path("chat/ask/", ask_member, name="chat-ask-member"),
]
