from django.db import models
from django.utils import timezone
import random
import string

class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=64)
    foto = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)
    cidade = models.CharField(max_length=100, null=True, blank=True)
    pontos_eco = models.IntegerField(default=0)
    nivel = models.CharField(max_length=20, default='Iniciante')
    atividades = models.JSONField(default=dict, null=True, blank=True)
    data_cadastro = models.DateTimeField(default=timezone.now)
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    email_verificado = models.BooleanField(default=False)
    codigo_verificacao = models.CharField(max_length=6, null=True, blank=True)
    codigo_expira_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.nome

    def gerar_codigo_verificacao(self):
        """
        Gera um código de verificação de 6 dígitos e define prazo de expiração
        """
        codigo = ''.join(random.choices(string.digits, k=6))
        self.codigo_verificacao = codigo
        self.codigo_expira_em = timezone.now() + timezone.timedelta(minutes=30)
        self.save()
        return codigo

    def verificar_codigo(self, codigo):
        """
        Verifica se o código fornecido é válido e não expirou
        """
        if (self.codigo_verificacao == codigo and 
            self.codigo_expira_em and 
            timezone.now() <= self.codigo_expira_em):
            self.email_verificado = True
            self.codigo_verificacao = None
            self.codigo_expira_em = None
            self.save()
            return True
        return False

    def adicionar_atividade(self, tipo, quantidade=1):
        """
        Adiciona uma atividade sustentável ao usuário
        """
        if not self.atividades:
            self.atividades = {}
        
        if tipo in self.atividades:
            self.atividades[tipo] += quantidade
        else:
            self.atividades[tipo] = quantidade
        
        self.save()

