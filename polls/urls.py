from django.urls import include, path

from . import views

app_name = "polls"
urlpatterns = [
    # ex: /polls/
    # ex: /polls/5/
    # ex: /polls/5/results/
    # ex: /polls/5/vote/
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
]