from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from .models import Film, Category

def ping(request):
    return JsonResponse({"status": "ok", "app": "films"})

class CategoryListView(ListView):
    model = Category
    template_name = "films/category_list.html"
    context_object_name = "categories"

    def render_to_response(self, context, **response_kwargs):
        data = [
            {"id": c.id, "name": c.name, "slug": c.slug}
            for c in context["categories"]
        ]
        return JsonResponse(data, safe=False)

class CategoryDetailView(DetailView):
    model = Category
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "films/category_detail.html"
    context_object_name = "category"

    def render_to_response(self, context, **response_kwargs):
        category = context["category"]
        data = {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "films": [
                {"id": f.id, "title": f.title, "slug": f.slug, "status": f.status}
                for f in category.films.all()
            ],
        }
        return JsonResponse(data, safe=False)

class FilmListView(ListView):
    model = Film
    template_name = "films/film_list.html"
    context_object_name = "films"

    def render_to_response(self, context, **response_kwargs):
        data = [
            {
                "id": f.id,
                "title": f.title,
                "slug": f.slug,
                "status": f.status,
                "price": float(f.price),
                "category": f.category.name if f.category else None,
            }
            for f in context["films"]
        ]
        return JsonResponse(data, safe=False)

class FilmDetailView(DetailView):
    model = Film
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "films/film_detail.html"
    context_object_name = "film"

    def render_to_response(self, context, **response_kwargs):
        f = context["film"]
        data = {
            "id": f.id,
            "title": f.title,
            "slug": f.slug,
            "description": f.description,
            "status": f.status,
            "price": float(f.price),
            "poster": f.poster.url if f.poster else None,
            "trailer_url": f.trailer_url,
            "video_file": f.video_file.url if f.video_file else None,
            "category": f.category.name if f.category else None,
            "created_at": f.created_at,
            "updated_at": f.updated_at,
        }
        return JsonResponse(data, safe=False)
