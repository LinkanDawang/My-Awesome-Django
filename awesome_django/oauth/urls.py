from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from .views.logto import LogtoView

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("logto", LogtoView, basename="logto")


app_name = "oauth"
urlpatterns = router.urls
