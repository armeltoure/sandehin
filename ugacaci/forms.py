from django import forms
from .models import PretBancaire
from .models import Client






class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            "nom_prenoms",
            "numero_telephone",
            "numero_cni",
        ]  # Champs que vous souhaitez modifier

    # Vous pouvez ajouter des validations personnalisées ou des widgets supplémentaires ici si nécessaire
    def clean_numero_telephone(self):
        numero_telephone = self.cleaned_data.get("numero_telephone")
        # Vérifier si un autre client possède déjà ce numéro de téléphone
        if Client.objects.filter(numero_telephone=numero_telephone).exists():
            raise forms.ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return numero_telephone


# forms.py


class PretBancaireForm(forms.ModelForm):
    class Meta:
        model = PretBancaire
        fields = [
            "montant_demande",
            "date_demande",
            "lieu_demande",
            "date_rembourssement",
            "montant_rembourssement",
        ]
        widgets = {
            'montant_demande': forms.TextInput(attrs={'placeholder': 'Montant demandé'}),
            'date_demande': forms.DateInput(attrs={'placeholder': 'Date de demande','type': 'date'}),
            'lieu_demande': forms.TextInput(attrs={'placeholder': 'Lieu de demande'}),
            'date_rembourssement': forms.DateInput(attrs={'placeholder': 'Date de remboursement','type': 'date'}),
            'montant_rembourssement': forms.TextInput(attrs={'placeholder': 'Montant de remboursement'}),
        }
