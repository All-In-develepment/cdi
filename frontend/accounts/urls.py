from django.urls import path
from .views import SignUpView, custom_login_view, custom_logout_view, listar_mercados, criar_mercado, criar_transacao,listar_transacoes

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', custom_login_view, name='login'),  # Alterado para CustomLoginView
    path('mercado/', criar_mercado, name='criar_mercado'),  # Acessa diretamente
    path('logout/', custom_logout_view, name='logout'),
    path('mercados/', listar_mercados, name='listar_mercados'),  # Acessa diretamente
    path('transacoes/', criar_transacao, name='criar_transacao'),
    path('transacoes/listar/', listar_transacoes, name='listar_transacoes'),

]
