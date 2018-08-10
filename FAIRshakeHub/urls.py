from django.urls import path, include
from ajax_select import urls as ajax_select_urls
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('bookmarklet/', views.bookmarklet, name='bookmarklet'),
    path('chrome_extension/', views.chrome_extension, name='chrome_extension'),
    path('ajax_select/', include(ajax_select_urls)),
]
