from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.generic import ListView, DetailView

User = get_user_model()

def ping(request):
    return JsonResponse({"status": "ok", "app": "users"})

class UserListView(ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"

    def render_to_response(self, context, **response_kwargs):
        data = [{"id": u.id, "email": u.email, "is_active": u.is_active} for u in context["users"]]
        return JsonResponse(data, safe=False)

class UserDetailView(DetailView):
    model = User
    template_name = "users/user_detail.html"
    context_object_name = "user"

    def render_to_response(self, context, **response_kwargs):
        u = context["user"]
        data = {"id": u.id, "email": u.email, "is_active": u.is_active, "date_joined": u.date_joined}
        return JsonResponse(data, safe=False)
