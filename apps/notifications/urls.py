from apps.notifications.views import CreateNotification, RetrieveNotification
from django.urls import path

app_name = 'notification'

urlpatterns = [
    path('notifications/', CreateNotification.as_view()),
    path('notifications/<uuid:id>/', RetrieveNotification.as_view())
]
