from django.db import models
from django.utils import timezone

class Doacao(models.Model):
    descricao = models.TextField("Descrição do item")
    categoria = models.CharField(
        "Categoria",
        max_length=50,
        choices=[
            ("informatica", "Informática"),
            ("eletrodomestico", "Eletrodoméstico"),
            ("telefonia", "Telefonia"),
            ("audio_video", "Áudio e Vídeo"),
            ("outros", "Outros"),
        ],
        default="outros"
    )
    local = models.CharField("Local de entrega ou coleta", max_length=255)
    foto = models.ImageField("Foto do item", upload_to="fotos_doacao/", blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.categoria} - {self.descricao[:20]}"

class Coleta(models.Model):
    quantidade = models.IntegerField("Quantidade de itens", default=1)
    tipo_material = models.CharField(
        "Tipo de Material",
        max_length=50,
        choices=[
            ("eletronico", "Eletrônico"),
            ("metal", "Metal"),
            ("plastico", "Plástico"),
            ("vidro", "Vidro"),
            ("misto", "Misto"),
        ],
        default="misto"
    )
    endereco = models.CharField("Endereço para coleta", max_length=255, default="A definir")
    data_preferencial = models.DateField("Data preferencial para coleta", default=timezone.now)
    observacoes = models.TextField("Observações", blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        "Status",
        max_length=20,
        choices=[
            ("pendente", "Pendente"),
            ("agendada", "Agendada"),
            ("concluida", "Concluída"),
            ("cancelada", "Cancelada"),
        ],
        default="pendente"
    )

    def __str__(self):
        return f"Coleta de {self.tipo_material} - {self.quantidade} itens"
