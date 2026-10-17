from django.db import models

class Colaborador(models.Model):
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=30)
    setor = models.CharField(max_length=50)

    def __str__(self):
        return self.nome


class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    login = models.CharField(max_length=50)
    senha = models.CharField(max_length=50)

    def __str__(self):
        return self.nome
    
class EPI(models.Model):
    nome = models.CharField(max_length=100)
    estoque = models.IntegerField()

    def __str__(self):
        return self.nome

class Emprestimo(models.Model):
    data_retirada = models.DateField()
    data_devolucao_previsao = models.DateField()
    data_devolucao = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50)
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE)

    def __str__(self):
        return f"Empréstimo {self.id} - {self.colaborador.nome}"

class Item(models.Model):
    emprestimo = models.ForeignKey(Emprestimo, on_delete=models.CASCADE)
    epi = models.ForeignKey(EPI, on_delete=models.CASCADE)
    quantidade = models.IntegerField()

    def __str__(self):
        return f"{self.quantidade}x {self.epi.nome}"