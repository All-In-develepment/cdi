from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('mercados/', views.MercadoListView.as_view(), name='mercado-list'),
    path('mercados/novo/', views.MercadoCreateView.as_view(), name='mercado-create'),
    path('mercados/editar/<int:pk>/', views.MercadoUpdateView.as_view(), name='mercado-update'),
    path('mercados/deletar/<int:pk>/', views.MercadoDeleteView.as_view(), name='mercado-delete'),
]
