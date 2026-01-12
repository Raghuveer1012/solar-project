from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("about/", views.about_view, name="about"),
    path("contact/", views.contact_view, name="contact"),
    path("products/", views.products_view, name="products"),
    # path("solar-calculator/", views.solar_calculator, name="solar_calculator"),
    path("profile/", views.profile_view, name="profile"),
]
