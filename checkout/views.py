from decimal import Decimal
from typing import Optional

from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PaymentForm
from .models import Carrinho, ItemCarrinho, Produto


def _seed_produtos() -> None:
    if Produto.objects.exists():
        return
    Produto.objects.bulk_create(
        [
            Produto(
                nome="Curso Python Básico",
                descricao="Aprenda os fundamentos de Python com exemplos práticos.",
                preco=Decimal("99.90"),
            ),
            Produto(
                nome="Curso Python Avançado",
                descricao="Aprofunde-se em APIs, testes e automação com Python.",
                preco=Decimal("179.90"),
            ),
            Produto(
                nome="Mentoria Express",
                descricao="Sessão rápida para tirar dúvidas específicas.",
                preco=Decimal("59.90"),
            ),
            Produto(
                nome="Suporte Premium",
                descricao="Atendimento prioritário com especialistas.",
                preco=Decimal("129.90"),
            ),
        ]
    )


def _seed_carrinho() -> Carrinho:
    cart = Carrinho.objects.first()
    if cart:
        return cart
    cart = Carrinho.objects.create()
    produto_principal = Produto.objects.order_by("-preco").first()
    if produto_principal:
        ItemCarrinho.objects.create(
            carrinho=cart, produto=produto_principal, quantidade=1, preco_unitario=produto_principal.preco
        )
    cart.atualizar_total()
    return cart


def _selecionar_ofertas(cart: Carrinho) -> tuple[Optional[Produto], Optional[Produto]]:
    produtos_no_carrinho = cart.produtos.all()
    upsell = (
        Produto.objects.exclude(id__in=produtos_no_carrinho)
        .order_by("-preco")
        .first()
    )
    downsell = None
    if upsell:
        downsell = (
            Produto.objects.filter(~Q(id__in=produtos_no_carrinho), ~Q(id=upsell.id))
            .order_by("preco")
            .first()
        )
    return upsell, downsell


def checkout_view(request: HttpRequest) -> HttpResponse:
    _seed_produtos()
    cart = _seed_carrinho()

    upsell, downsell = _selecionar_ofertas(cart)
    mensagem = None

    if request.method == "POST":
        acao = request.POST.get("acao")
        produto_id = request.POST.get("produto_id")
        if acao in {"add_upsell", "add_downsell"} and produto_id:
            produto = get_object_or_404(Produto, id=produto_id)
            item, _ = ItemCarrinho.objects.get_or_create(
                carrinho=cart,
                produto=produto,
                defaults={"preco_unitario": produto.preco},
            )
            if not _:
                item.quantidade += 1
            item.save()
            mensagem = "Oferta adicionada ao pedido!"
            return redirect("checkout")
        elif acao == "recusar_upsell":
            mensagem = "Oferta recusada. Confira nossa opção alternativa!"
        elif acao == "recusar_downsell":
            mensagem = "Tudo bem, seguimos com seu pedido atual."

    payment_form = PaymentForm(request.POST or None)
    itens = cart.itens.select_related("produto")

    contexto = {
        "carrinho": cart,
        "itens": itens,
        "upsell": upsell,
        "downsell": downsell,
        "frete": cart.FRETE_FIXO,
        "mensagem": mensagem,
        "payment_form": payment_form,
    }

    return render(request, "checkout/checkout.html", contexto)
