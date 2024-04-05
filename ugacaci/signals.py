from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CompteBancaire, Client

@receiver(post_save, sender=CompteBancaire)
def update_eligibility_for_compte_bancaire(sender, instance, **kwargs):
    print("Signal is triggered for CompteBancaire!")
    # Ajoutez ici votre logique spécifique pour CompteBancaire
@receiver(post_save, sender=Client)
def create_compte_bancaire(sender, instance, created, **kwargs):
    if created:
        CompteBancaire.objects.create(client=instance, solde_initial=instance.montant)
    