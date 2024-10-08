from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from contas.models import Mercado

# Create your models here.
class Transacao(models.Model):
    TIPO_CHOICES = [
        ('Aporte', 'Aporte'),
        ('Retirada', 'Retirada'),
        ('Aposta', 'Aposta'),
    ]

    RESULTADO_CHOICES = [
        ('Green', 'Green'),
        ('Red', 'Red'),
    ]

    id = models.AutoField(primary_key=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)  # Decimal não nulo
    mercado = models.ForeignKey(Mercado, on_delete=models.CASCADE)  # Chave estrangeira para Mercado
    tipo = models.CharField(max_length=8, choices=TIPO_CHOICES)  # Enum Tipo
    resultado = models.CharField(max_length=5, choices=RESULTADO_CHOICES, blank=True, null=True)  # Enum Resultado (opcional)
    odd = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # Decimal Odd
    retorno = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True)  # Retorno calculado automaticamente
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Chave estrangeira para o usuário
    data_registro = models.DateField(null=True, auto_now_add=True)  # Data de registro

    def save(self, *args, **kwargs):
        # Calcula o retorno: Valor * Odd - Valor
        if self.odd and self.valor:
            self.retorno = Decimal(self.valor) * Decimal(self.odd) - Decimal(self.valor)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.tipo} - {self.valor}'
