from django.urls import path

from . import views
app_name = 'searchranking'
urlpatterns = [
    path('', views.index, name='index'),
    path('results', views.results, name='results'),
    path('go_to_selection', views.go_to_selection, name='go_to_selection')
]
