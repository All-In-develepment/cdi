from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Mercado(models.Model):
    id = models.AutoField(primary_key=True)  # Identificador único auto-incrementado
    nome = models.CharField(max_length=255)  # Nome do mercado
    color = models.CharField(max_length=7, default='#000000')  # Cor do mercado em hexadecimal
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Chave estrangeira do usuário

    def __str__(self):
        return self.nome
