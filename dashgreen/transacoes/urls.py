from django.urls import path
from . import views

urlpatterns = [
    path('', views.TransacaoListView.as_view(), name='transacao-list'),
    path('novo/', views.TransacaoCreateView.as_view(), name='transacao-create'),
    path('editar/<int:pk>/', views.TransacaoUpdateView.as_view(), name='transacao-update'),
    path('deletar/<int:pk>/', views.TransacaoDeleteView.as_view(), name='transacao-delete'),
]
