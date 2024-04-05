import random
import string
from datetime import timedelta
from django.db import models
from django.utils import timezone


class Ville(models.Model):
    nom = models.CharField(max_length=50)

    def __str__(self):
        return self.nom


class Collection(models.Model):
    collection_name = models.CharField(max_length=60, null=True)

    def __str__(self):
        return self.collection_name


class Client(models.Model):
    nom_prenoms = models.CharField(max_length=50)
    nombre_depot = models.PositiveIntegerField(default=0)
    numero_telephone = models.CharField(max_length=15)
    localite = models.CharField(max_length=50)
    profession = models.CharField(max_length=50)
    numero_cni = models.CharField(max_length=50)
    ville = models.ForeignKey(Ville, null=True, on_delete=models.SET_NULL)
    montant = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(
        "Collection", blank=True, null=True, on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="adherent_images/")
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=100)

    def creer_pret(self, montant, duree):
        if self.nombre_depot >= 14:
            montant_pret = 100000  # Montant fixe à 100000 FCFA
            montant_remboursement = (
                montant * 2
            )  # Calculer le montant total à rembourser
            date_limite_remboursement = timezone.now() + timedelta(days=(duree * 30))

            # Créer un nouvel objet Pret associé à ce client
            Pret.objects.create(
                client=self,
                montant_depot_eligible=montant,
                duree=duree,
                montant_pret=montant_pret,
                montant_remboursement=montant_remboursement,
                date_limite_remboursement=date_limite_remboursement,
            )

    def get_numero_compte(self):
        # Retourner le numéro de compte associé à ce client s'il existe, sinon 'Aucun compte associé'
        return (
            self.comptes_bancaires.first().numero_compte
            if self.comptes_bancaires.exists()
            else "Aucun compte associé"
        )

    def get_solde_actuel(self):
        # Retourner le solde actuel du compte bancaire associé à ce client s'il existe, sinon None
        return (
            self.comptes_bancaires.first().solde_actuel
            if self.comptes_bancaires.exists()
            else None
        )

    def eligibility_details(self):
        montant_empruntable = 0
        date_remboursement = None

        if self.nombre_depot >= 14:
            montant_empruntable = 100000  # Montant fixe à 100000 FCFA
            date_remboursement = timezone.now() + timedelta(
                days=90
            )  # Remboursement dans 3 mois

        return {
            "montant_empruntable": montant_empruntable,
            "date_remboursement": date_remboursement,
        }

    def get_commissions(self):
        return self.commissions.all()

    def get_total_commissions(self):
        return sum(commission.montant for commission in self.commissions.all())

    def save(self, *args, **kwargs):
        # Assurer que le nombre de dépôts du client est égal au nombre de dépôts de son compte bancaire
        if self.id:
            self.nombre_depot = self.comptes_bancaires.first().depots.count()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom_prenoms


class Pret(models.Model):
    client = models.ForeignKey(Client, related_name="prets", on_delete=models.CASCADE)
    montant_depot_eligible = models.PositiveIntegerField(default=0)
    duree = models.PositiveIntegerField(default=3)
    date_pret = models.DateTimeField(auto_now=True)
    montant_pret = models.PositiveIntegerField()
    montant_remboursement = models.PositiveIntegerField()
    date_limite_remboursement = models.DateTimeField()

    def __str__(self):
        return f"Pret de {self.montant_pret} FCFA pour {self.client}"


class CompteBancaire(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="comptes_bancaires"
    )
    solde_initial = models.PositiveIntegerField(default=0)
    solde_actuel = models.PositiveIntegerField(default=0)
    nb_depot = models.PositiveIntegerField(default=0)
    date_ouverture = models.DateField(auto_now_add=True)
    numero_compte = models.CharField(max_length=20, unique=True, null=True)

    def montant_cotise_moins_ouverture(self):
        return self.solde_actuel - self.solde_initial

    def save(self, *args, **kwargs):
        if not self.id:
            self.solde_actuel = self.solde_initial
            random_chars = "".join(
                random.choices(string.ascii_letters + string.digits, k=16)
            )
            self.numero_compte = ".".join([random_chars[:4], random_chars[4:]])

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Compte de {self.client} - Solde actuel: {self.solde_actuel}"


class Depot(models.Model):
    client = models.ForeignKey(Client, related_name="depots", on_delete=models.CASCADE)
    montant = models.PositiveIntegerField(default=0)
    date_depot = models.DateTimeField(auto_now=True)

    def calculer_frais(self):
        return self.montant * 0.142857  # Calculer les frais de dépôt

    def save(self, *args, **kwargs):
        frais = self.calculer_frais()
        compte_client = self.client.comptes_bancaires.first()

        if compte_client:
            compte_client.solde_actuel += (
                self.montant - frais
            )  # Mettre à jour le solde actuel du compte
            compte_client.save()

        super().save(*args, **kwargs)


class Commission(models.Model):
    montant = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Commission de {self.montant} FCFA"


class CommissionClient(models.Model):
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    client = models.ForeignKey(
        "Client", on_delete=models.CASCADE, related_name="commissions"
    )
    commission = models.ForeignKey("Commission", on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commission de {self.commission.montant} FCFA pour {self.client}"

    class Meta:
        ordering = ["-date_creation"]


class Operation(models.Model):
    compte = models.ForeignKey("CompteBancaire", on_delete=models.CASCADE)
    type_operation = models.CharField(max_length=50)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_operation = models.DateTimeField(auto_now_add=True)
    lieu_operation = models.CharField(max_length=200, default="Non spécifié")

    def __str__(self):
        return f"{self.type_operation} - {self.montant} - {self.compte}"



class PretBancaire(models.Model):
    client = models.ForeignKey(
        Client, related_name="prets_bancaires", on_delete=models.CASCADE
    )
    montant_demande = models.IntegerField()  # Champs pour le montant demandé (entier)
    date_demande = models.DateField(null=True)
    montant_rembourssement = models.IntegerField(null=True)  # Champs pour le montant de remboursement (entier)
    statut = models.CharField(max_length=20, default="En attente")
    date_rembourssement = models.DateField(null=True)
    lieu_demande = models.CharField(max_length=26, null=True)

    def confirmer_pret(self):
        if self.statut == "En attente":
            self.statut = "Succès"
            self.date_remboursement = timezone.now() + timezone.timedelta(
                days=180
            )  # Exemple: Date de remboursement dans 180 jours
            self.save()

    def __str__(self):
        return f"Demande de prêt de {self.client.nom_prenoms} - Montant: {self.montant_demande} FCFA - Statut: {self.statut}"
