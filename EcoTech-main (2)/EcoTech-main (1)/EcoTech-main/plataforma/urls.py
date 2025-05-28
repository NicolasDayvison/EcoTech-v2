from django.urls import path
from . import views

app_name = 'plataforma'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('coleta/', views.coleta_view, name='coleta'),
    path('doacao/', views.doacao_view, name='doacao'),
    path('sobre/', views.sobre_view, name='sobre'),
    path('servicos/', views.servicos_view, name='servicos'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('doar/', views.doar_view, name='doar'),
    path('contato/', views.contato_view, name='contato'),
    path('sair/', views.logout_view, name='sair'),
]