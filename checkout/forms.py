from django import forms


class PaymentForm(forms.Form):
    nome = forms.CharField(label="Nome completo", max_length=255)
    endereco = forms.CharField(label="Endereço", widget=forms.Textarea(attrs={"rows": 2}))
    metodo_pagamento = forms.ChoiceField(
        label="Método de pagamento",
        choices=(
            ("card", "Cartão de crédito"),
            ("pix", "PIX"),
            ("boleto", "Boleto"),
        ),
    )
    aceitar_upsell = forms.BooleanField(
        label="Adicionar oferta especial", required=False, initial=False
    )
