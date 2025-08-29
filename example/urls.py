from django.urls import path
from django.views.generic import TemplateView


def view(title):
    return TemplateView.as_view(template_name="base.html", extra_context={"title": title})

urlpatterns = [
    # Main pages
    path("", view("home"), name="home"),
    path("about/", view("about"), name="about"),
    path("contact/", view("contact"), name="contact"),
    
    # Services pages
    path("services/web-design/", view("web design"), name="web_design"),
    path("services/development/", view("development"), name="development"),
    path("services/consulting/", view("consulting"), name="consulting"),
]
