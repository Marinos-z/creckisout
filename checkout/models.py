from decimal import Decimal

from django.db import models
from django.db.models import F, Sum


class Produto(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    imagem = models.ImageField(upload_to="produtos/", null=True, blank=True)

    def __str__(self) -> str:
        return self.nome


class Carrinho(models.Model):
    produtos = models.ManyToManyField(
        Produto, through="ItemCarrinho", related_name="carrinhos"
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    FRETE_FIXO = Decimal("15.00")

    def atualizar_total(self) -> None:
        subtotal = (
            self.itens.aggregate(
                total=Sum(F("preco_unitario") * F("quantidade"))
            ).get("total")
            or Decimal("0.00")
        )
        self.total = subtotal + self.FRETE_FIXO
        self.save(update_fields=["total"])

    @property
    def subtotal(self) -> Decimal:
        return (
            self.itens.aggregate(
                total=Sum(F("preco_unitario") * F("quantidade"))
            ).get("total")
            or Decimal("0.00")
        )

    def __str__(self) -> str:
        return f"Carrinho #{self.pk or 'novo'}"


class ItemCarrinho(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    carrinho = models.ForeignKey(
        Carrinho, related_name="itens", on_delete=models.CASCADE
    )
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("produto", "carrinho")

    @property
    def valor_total(self) -> Decimal:
        return self.preco_unitario * self.quantidade

    def save(self, *args, **kwargs):
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco
        super().save(*args, **kwargs)
        if self.carrinho_id:
            self.carrinho.atualizar_total()

    def __str__(self) -> str:
        return f"{self.quantidade} x {self.produto.nome}"
