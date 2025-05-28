from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('valida_login/', views.valida_login, name='valida_login'),
    path('valida_cadastro/', views.valida_cadastro, name='valida_cadastro'),
    path('sair/', views.sair, name='sair'),
    path('usuario/', views.perfil_usuario, name='usuario'),
    path('atualizar_foto/', views.atualizar_foto, name='atualizar_foto'),
    path('atualizar_perfil/', views.atualizar_perfil, name='atualizar_perfil'),
    path('excluir_conta/', views.excluir_conta, name='excluir_conta'),
    path('atualizar_cidade/', views.atualizar_cidade, name='atualizar_cidade'),
    path('registrar_atividade/', views.registrar_atividade, name='registrar_atividade'),
    path('verificar-email/', views.verificar_email, name='verificar_email'),
    path('verificar-codigo/', views.verificar_codigo, name='verificar_codigo'),
    path('reenviar-codigo/', views.reenviar_codigo, name='reenviar_codigo'),
]