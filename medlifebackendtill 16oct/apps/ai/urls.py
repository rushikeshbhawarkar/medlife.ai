# # Purpose: AI endpoint routes.
# # Keep the trailing slash because the frontend calls /prompt/.
# from django.urls import path
# from .views import prompt
# urlpatterns = [path("prompt/", prompt, name="prompt")]





# # Purpose: AI endpoint routes.
# from django.urls import path
# from .views import ask_member, prompt

# urlpatterns = [
#     path("prompt/", prompt, name="prompt"),
#     path("chat/ask/", ask_member, name="chat-ask-member"),
# ]





# Purpose: AI endpoint routes.
from django.urls import path
from .views import ask_member, prompt, providers

urlpatterns = [
    path("providers/", providers, name="ai-providers"),
    path("prompt/", prompt, name="prompt"),
    path("chat/ask/", ask_member, name="chat-ask-member"),
]
