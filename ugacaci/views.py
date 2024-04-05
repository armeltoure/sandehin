import datetime
import hashlib
from datetime import timedelta

from django.contrib import messages
from django.db.models import F, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ClientForm, PretBancaireForm
from .models import (
    Client,
    Collection,
    CommissionClient,
    CompteBancaire,
    Operation,
    PretBancaire,
    Ville,
)
from .utils import check_loan_eligibility


def hash_password(password):
    # Utilisez une méthode de hachage sécurisée comme sha256 ou sha512
    sha256 = hashlib.sha256()
    sha256.update(password.encode("utf-8"))
    return sha256.hexdigest()


# Create your views here.
def login(request, collection_name):
    request.session["collection_name"] = (
        collection_name  # Stocke le nom de la collection dans la session
    )
    return render(
        request, "ugacaci/gestionpage.html", {"collection_name": collection_name}
    )


def home(request):
    return render(request, "ugacaci/home.html")


def collection_view(request, collection_name):
    collection = get_object_or_404(Collection, collection_name=collection_name)
    request.session["collection_name"] = (
        collection_name  # Stocke le nom de la collection dans la session
    )
    context = {
        "collection": collection,
        "selected_city": collection_name,  # Passer le nom de la ville sélectionnée
    }
    return render(request, "ugacaci/collection/login.html", context)


# Un dictionnaire de logins et mots de passe pour chaque collection
logins_mdp = {
    "Duekoue": {
        "login": "duekoue_login",
        "password": hash_password("duekoue_password"),
    },
    "Bouake": {"login": "bouake_login", "password": hash_password("bouake_password")},
    "Katiola": {
        "login": "katiola_login",
        "password": hash_password("katiola_password"),
    },
    "San-Pedro": {
        "login": "san_pedro_login",
        "password": hash_password("san_pedro_password"),
    },
    "Oume": {"login": "oume_login", "password": hash_password("oume_password")},
    "Yamoussoukro": {
        "login": "yamoussoukro_login",
        "password": hash_password("yamoussoukro_password"),
    },
    "Daloa": {"login": "daloa_login", "password": hash_password("daloa_password")},
    "Man": {"login": "man_login", "password": hash_password("man_password")},
    # ... Ajoute d'autres collections avec leurs logins et mots de passe hachés
}


def gestionpage(request):
    if request.method == "POST":
        collection_name = request.POST.get("collection_name")
        login = request.POST.get("login")
        password = request.POST.get("password")

        # Vérifie si la collection existe dans le dictionnaire logins_mdp
        if collection_name in logins_mdp:
            credentials = logins_mdp[collection_name]
            # Vérifie les identifiants pour la collection spécifiée
            if (
                login == credentials["login"]
                and hash_password(password) == credentials["password"]
            ):
                # Identifiants corrects pour cette collection
                return render(request, "ugacaci/gestionpage.html")
            # return HttpResponse(f"Connecté à la plateforme {collection_name} avec succès !")

        # Si les identifiants ne correspondent pas ou si la collection n'est pas trouvée
        return HttpResponse(
            "<div class='text-center'>Identifiants incorrects. Veuillez entrer le login et le mot de passe correct !</div>"
        )
    # Gère le rendu de la page de connexion si ce n'est pas une soumission POST
    return render(request, "ugacaci/gestionpage.html")


def adherent(request):
    selected_city = request.GET.get("collection_name", None)
    return render(request, "adherent/adherent.html", {"collection_name": selected_city})


def adherent_view(request):
    error_message = None
    new_client = None
    selected_city = None

    if "collection_name" in request.session:
        selected_city = request.session["collection_name"]

    if request.method == "POST":
        nom_prenoms = request.POST.get("nom_prenoms")
        numero_telephone = request.POST.get("numero_telephone")
        numero_cni = request.POST.get("numero_cni")
        profession = request.POST.get("profession")
        localite = request.POST.get("localite")
        montant = request.POST.get("solde_actuel")
        date_naissance = request.POST.get("date_naissance")
        lieu_naissance = request.POST.get("lieu_naissance")

        ville, created = Ville.objects.get_or_create(nom=selected_city)

        # Vérification de l'unicité du numéro de téléphone
        if Client.objects.filter(numero_telephone=numero_telephone).exists():
            error_message = "Ce numéro de téléphone existe déjà dans la base de données. Veuillez en choisir un autre numéro."
        else:
            # Création du nouveau client seulement si le numéro de téléphone est unique
            new_client = Client.objects.create(
                nom_prenoms=nom_prenoms,
                numero_telephone=numero_telephone,
                numero_cni=numero_cni,
                profession=profession,
                localite=localite,
                ville=ville,
                montant=montant,
                date_naissance=date_naissance,
                lieu_naissance=lieu_naissance,
            )

            messages.success(
                request, "L'adhérent a bien été ajouté dans la base de données!"
            )

    context = {
        "error_message": error_message,
        "new_client": new_client,
        "selected_city": selected_city,
    }

    return render(request, "adherent/adherent.html", context)


def pret(request):
    # Récupérer tous les clients avec leur nombre de dépôts sur le compte
    clients_eligibles = Client.objects.filter(
        comptes_bancaires__nb_depot__gte=14
    ).prefetch_related("comptes_bancaires")

    context = {"clients_eligibles": clients_eligibles}
    return render(request, "ugacaci/pret.html", context)


def search_clients(request):
    resultats = []  # Initialise une liste vide pour stocker les résultats
    if request.method == "POST":
        telephone = request.POST.get("numero_telephone")
        if telephone:  # Utilisation directe de la vérité des valeurs en Python
            # Effectue la recherche dans ton modèle pour obtenir plusieurs résultats
            resultats = Client.objects.filter(numero_telephone__contains=telephone)

    return render(request, "ugacaci/gestionpage.html", {"resultats": resultats})


def clients_eligibles(request):
    clients_eligibles = Client.objects.filter(nombre_depot__gt=13, montant__gt=1000)

    context = {
        "clients_eligibles": clients_eligibles,
    }

    return render(request, "ugacaci/pret.html", context)


def virement(request):
    return render(request, "ugacaci/operation/virement.html")


def operation(request):
    return render(request, "ugacaci/operation/operations.html")


def effectuer_virement(request):
    if request.method == "POST":
        # Récupération des numéros de téléphone saisis dans le formulaire
        telephone_debiter = request.POST.get("numero_telephone")
        telephone_crediter = request.POST.get("numero_telephone_2")

        # Recherche des clients correspondants aux numéros de téléphone
        client_debiter = Client.objects.filter(
            numero_telephone=telephone_debiter
        ).first()
        client_crediter = Client.objects.filter(
            numero_telephone=telephone_crediter
        ).first()

        context = {
            "client_debiter": client_debiter,
            "client_crediter": client_crediter,
        }
        return render(request, "ugacaci/operation/virement.html", context)

    return render(request, "home.html")


def client_details(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    compte_bancaire = client.comptes_bancaires.first()
    operations = (
        Operation.objects.filter(compte=compte_bancaire) if compte_bancaire else []
    )
    solde_actuel = compte_bancaire.solde_actuel if compte_bancaire else 0

    context = {
        "client": client,
        "compte_bancaire": compte_bancaire,
        "operations": operations,
        "solde_actuel": solde_actuel,
    }
    return render(request, "ugacaci/client_details.html", context)


def rechercher_client(request):
    clients_debiter = []
    clients_crediter = []
    if request.method == "POST":
        # Recherche pour le formulaire de débit
        numero_telephone_debiter = request.POST.get("numero_telephone_debiter")
        clients_debiter = Client.objects.filter(
            numero_telephone__contains=numero_telephone_debiter
        )

        # Recherche pour le formulaire de crédit
        numero_telephone_crediter = request.POST.get("numero_telephone_crediter")
        clients_crediter = Client.objects.filter(
            numero_telephone__contains=numero_telephone_crediter
        )

    context = {
        "clients_debiter": clients_debiter,
        "clients_crediter": clients_crediter,
    }
    return render(request, "ugacaci/virement.html", context)


def rechercher_compte_debiter(request):
    if request.method == "POST":
        numero_telephone = request.POST.get("numero_telephone_debiter")
        compte = CompteBancaire.objects.filter(
            client__numero_telephone=numero_telephone
        ).first()
        return render(request, "ugacaci/virement.html", {"client_debiter": compte})
    return render(request, "ugacaci/virement.html", {})


def rechercher_compte_crediter(request):
    if request.method == "POST":
        numero_telephone = request.POST.get("numero_telephone_crediter")
        compte = CompteBancaire.objects.filter(
            client__numero_telephone=numero_telephone
        ).first()
        return render(request, "ugacaci/virement.html", {"client_crediter": compte})
    return render(request, "ugacaci/virement.html", {})


def liste_clients(request):
    search_query = request.GET.get(
        "search", ""
    )  # Get the search query from the request
    total_clients = Client.objects.count()

    # Filter clients based on the search query for the city name
    clients = Client.objects.filter(ville__nom__icontains=search_query)

    # Count the number of clients after filtering
    nombre_resultats = clients.count()

    context = {
        "clients": clients,
        "total_clients": total_clients,
        "nombre_resultats": nombre_resultats,
    }
    return render(request, "ugacaci/liste_clients.html", context)


# Vue pour supprimer un client
@require_POST
def supprimer_client(request, client_id):
    client = Client.objects.get(id=client_id)
    client.delete()
    return redirect("liste_clients")


def modifier_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect(
                "liste_clients"
            )  # Redirige vers la liste des clients après la modification
    else:
        form = ClientForm(
            instance=client
        )  # Crée un formulaire pré-rempli avec les données du client existant
    context = {
        "form": form,
        "client": client,
    }
    return render(request, "ugacaci/modifier_client.html", context)


def operations_jour(request):
    if request.method == "POST":
        lieu_operation = request.POST.get("lieu_operation")
        today = datetime.now().date()
        operations = Operation.objects.filter(
            date_operation__date=today, lieu_operation=lieu_operation
        )
        return render(
            request, "ugacaci/operations_jour.html", {"operations": operations}
        )
    else:
        today = datetime.now().date()
        operations = Operation.objects.filter(date_operation__date=today)
        return render(
            request, "ugacaci/operations_jour.html", {"operations": operations}
        )


def operations_semaine(request):
    if request.method == "POST":
        lieu_operation = request.POST.get("lieu_operation")
        today = datetime.now().date()
        week_number = today.isocalendar()[1]  # Récupérer le numéro de la semaine
        operations = Operation.objects.filter(
            date_operation__week=week_number, lieu_operation=lieu_operation
        )
        return render(
            request, "ugacaci/operations_semaine.html", {"operations": operations}
        )
    else:
        today = datetime.now().date()
        week_number = today.isocalendar()[1]  # Récupérer le numéro de la semaine
        operations = Operation.objects.filter(date_operation__week=week_number)
        return render(
            request, "ugacaci/operations_semaine.html", {"operations": operations}
        )


def operations_mois(request):
    months = [
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre",
    ]

    selected_month = request.GET.get("mois", datetime.now().strftime("%B"))
    lieu_operation = request.GET.get(
        "lieu_operation", None
    )  # Récupérer la valeur du lieu d'opération
    recherche_lieu = request.GET.get(
        "recherche_lieu", None
    )  # Récupérer la valeur de recherche sur le lieu d'opération

    # Vérifier si 'mois' est dans la requête GET avant d'extraire l'index
    if "mois" in request.GET:
        try:
            selected_month_index = months.index(selected_month)
            today = datetime.now().date()
            start_of_requested_month = today.replace(
                month=selected_month_index + 1, day=1
            )
            start_of_requested_month.replace(
                month=start_of_requested_month.month % 12 + 1, day=1
            ) - timedelta(days=1)

            # Filtrer les opérations par mois
            operations = Operation.objects.filter(
                date_operation__month=start_of_requested_month.month
            )

            # Filtrer les opérations par lieu d'opération s'il y a une valeur de lieu d'opération
            if lieu_operation:
                operations = operations.filter(lieu_operation=lieu_operation)

            # Filtrer les opérations déjà récupérées par la recherche sur le lieu d'opération
            if recherche_lieu:
                operations = operations.filter(lieu_operation__icontains=recherche_lieu)

            if not operations.exists():
                operations = None

        except ValueError:
            # Gérer le cas où le mois sélectionné n'est pas dans la liste 'months'
            operations = None
            selected_month_index = None
    else:
        operations = None
        selected_month_index = None

    return render(
        request,
        "ugacaci/operations_mois.html",
        {
            "operations": operations,
            "months": months,
            "selected_month_index": selected_month_index,
        },
    )


def auth_required_page(request):
    error_message = None
    if request.method == "POST" and request.POST.get("delete_client") == "true":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Vérification des identifiants fournis
        if (
            username == "01Gestionnaire@Ugacaci"
            and password == "...deletteAdher@Client@"
        ):
            client_id = request.GET.get("client_id")
            client = get_object_or_404(Client, pk=client_id)
            client.delete()

            return redirect(
                "liste_clients"
            )  # Redirection vers la liste des clients après suppression

    # Gestion des erreurs d'authentification ou affichage initial
    error_message = "Identification incorrecte. Veuillez réessayer."
    return render(
        request, "ugacaci/auth_required_page.html", {"error_message": error_message}
    )


def auth_required_op(request):
    error_message = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Vérification des identifiants fournis
        if (
            username == "01Gestionnaire@Ugacaci"
            and password == "...deletteAdher@Client@"
        ):
            return redirect(
                "operation"
            )  # Redirection vers la liste des clients après suppression

    # Gestion des erreurs d'authentification ou affichage initial
    error_message = "Identification incorrecte. Veuillez réessayer."
    return render(
        request,
        "ugacaci/auth_requierd_operation.html",
        {"error_message": error_message},
    )



def auth_required_pret(request):
    error_message = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Vérification des identifiants fournis
        if (
            username == "01Gestionnaire@Ugacaci"
            and password == "...deletteAdher@Client@"
        ):
            return redirect(
                "pret"
            )  # Redirection vers la liste des clients après suppression

    # Gestion des erreurs d'authentification ou affichage initial
    error_message = "Identification incorrecte. Veuillez réessayer."
    return render(
        request,
        "ugacaci/auth_requierd_operation.html",
        {"error_message": error_message},
    )


def somme_commissions_view(request):
    # Logique pour récupérer la somme des commissions depuis le modèle
    total_commissions = CommissionClient.objects.all().aggregate(Sum("montant"))[
        "montant__sum"
    ]
    context = {"total_commissions": total_commissions}
    return render(request, "ugacaci/somme_commissions.html", context)


def check_loan_eligibility(client):  # noqa: F811
    # Vérifiez le nombre de dépôts et le montant total des dépôts
    nombre_depot = client.comptebancaire_set.aggregate(Sum("nb_depot"))["nb_depot__sum"]
    montant_total = client.comptebancaire_set.aggregate(Sum("solde_initial"))[
        "solde_initial__sum"
    ]

    # Déterminez l'éligibilité en fonction des critères
    if nombre_depot >= 14 and montant_total >= 1000:
        return True
    else:
        return False


def commissions_clients(request):
    clients = Client.objects.all()
    commissions_par_client = []

    # Récupérez les commissions pour chaque client
    for client in clients:
        commissions = client.commissions.all()
        total_commissions_client = sum(
            commission.commission.montant for commission in commissions
        )
        commissions_par_client.append(
            {
                "client": client,
                "commissions": commissions,
                "total_commissions": total_commissions_client,
            }
        )
    # Calculez la somme totale des commissions
    total_commissions = CommissionClient.objects.all().aggregate(Sum("montant"))[
        "montant__sum"
    ]

    context = {
        "commissions_par_client": commissions_par_client,
        "total_commissions": total_commissions,
    }
    return render(request, "commission.html", context)


def effectuer_operation(request):
    if request.method == "POST":
        compte_id = request.POST.get("compte_id")
        montant_operation = float(request.POST.get("montant_operation"))
        operation_type = request.POST.get("operation")

        compte_bancaire = get_object_or_404(CompteBancaire, pk=compte_id)
        client = (
            compte_bancaire.client
        )  # Récupérer le client associé au compte bancaire

        # Récupérer le lieu de l'opération depuis la session
        lieu_operation = request.session.get("collection_name", "Non spécifié")

        if operation_type == "credit":
            if montant_operation > 0:
                commission_percentage = 7
                commission_amount = (montant_operation * commission_percentage) / 100
                montant_total_credit = montant_operation - commission_amount

                operation = Operation.objects.create(
                    compte=compte_bancaire,
                    type_operation="Crédit",
                    montant=montant_total_credit,
                    commission=commission_amount,
                    date_operation=timezone.now(),  # Ajout de la date d'opératio
                    lieu_operation=lieu_operation,  # Ajout du lieu de l'opération
                )
                operation.save()

                # Mise à jour du solde et du nombre de dépôts
                compte_bancaire.solde_actuel += montant_total_credit
                compte_bancaire.nb_depot = (
                    F("nb_depot") + 1
                )  # Incrémenter le nombre de dépôts avec F() expression
                compte_bancaire.save()

                # Mettre à jour le nombre_depot du client
                Client.objects.filter(pk=client.pk).update(
                    nombre_depot=F("nombre_depot") + 1
                )

                return redirect("client_details", client_id=client.pk)
            else:
                return HttpResponse(
                    "Le montant de l'opération doit être supérieur à zéro"
                )

        elif operation_type == "debit":
            if montant_operation > 0:
                if montant_operation <= compte_bancaire.solde_actuel:
                    operation = Operation.objects.create(
                        compte=compte_bancaire,
                        type_operation="Débit",
                        montant=montant_operation,
                        commission=0,
                        date_operation=timezone.now(),  # Ajout de la date d'opération
                        lieu_operation=lieu_operation,  # Ajout du lieu de l'opération
                    )
                    operation.save()

                    # Mise à jour du solde
                    compte_bancaire.solde_actuel -= montant_operation
                    compte_bancaire.save()

                    return redirect("client_details", client_id=client.pk)
                else:
                    return HttpResponse(
                        "Solde insuffisant pour effectuer cette opération"
                    )
            else:
                return HttpResponse(
                    "Le montant de l'opération doit être supérieur à zéro"
                )

    return HttpResponse("Méthode non autorisée.")


def demande_pret(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    if request.method == "POST":
        form = PretBancaireForm(request.POST)
        if form.is_valid():
            pret = form.save(commit=False)
            pret.client = client
            pret.save()
            
            # Appel de la méthode pour confirmer le prêt
            pret.confirmer_pret()
            
            return redirect("confirmation", demande_pret_id=pret.id)
    else:
        form = PretBancaireForm()
    return render(
        request, "ugacaci/demande_pret.html", {"form": form, "client": client}
    )

def effectuer_versement(request, pret_id):
    if request.method == "POST":
        montant_versement = int(request.POST.get("montant_versement"))
        pret = get_object_or_404(PretBancaire, pk=pret_id)
        if pret.montant_rembourssement is not None:
            nouveau_montant_remboursement = pret.montant_rembourssement - montant_versement
            if nouveau_montant_remboursement >= 0:
                # Mettre à jour le montant de remboursement dans la base de données
                pret.montant_rembourssement = nouveau_montant_remboursement
                pret.save()
                return JsonResponse({"success": True, "nouveau_montant": nouveau_montant_remboursement})
            else:
                return JsonResponse({"success": False, "message": "Le montant du versement dépasse le montant du remboursement restant."})
        else:
            return JsonResponse({"success": False, "message": "Le montant de remboursement n'est pas défini."})
    return JsonResponse({"success": False, "message": "Requête non autorisée."})


def liste_prets_confirmes(request):
    prets_confirms = PretBancaire.objects.filter(statut="Succès")
    context = {"prets_confirms": prets_confirms}
    return render(request, "ugacaci/liste_pret_confirme.html", context)

def confirmation(request, demande_pret_id):
    demande_pret = get_object_or_404(PretBancaire, pk=demande_pret_id)
    client = demande_pret.client
    context = {"client": client, "demande_pret": demande_pret}
    return render(request, "ugacaci/confirmation.html", context)
