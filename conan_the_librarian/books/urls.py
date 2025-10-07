from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from conan_the_librarian.books.views import BookViewSet

router = DefaultRouter()
router.register(r"books", BookViewSet, basename="books")

urlpatterns = [
    path("", include(router.urls)),
]
