from django.urls import path

import ugacaci

from . import views

app_name: "ugacaci"

urlpatterns = [
    path("", views.home, name="home"),
    path("collection/<str:collection_name>/", views.collection_view, name="login"),
    path("ugacaci", views.gestionpage, name="gestionpage"),
    path("adherent", views.adherent, name="adherent"),
    path("adherent/", views.adherent_view, name="adherent"),
    path("ugacaci/", views.search_clients, name="search_client"),
    path(
        "client-details/<int:client_id>/", views.client_details, name="client_details"
    ),
    path("operation", views.operation, name="operation"),
    path(
        "operation/debiter", views.rechercher_compte_debiter, name="rechercher_debiter"
    ),
    path(
        "operation/crediter",
        views.rechercher_compte_crediter,
        name="rechercher_crediter",
    ),
    path("rechercher-client/", views.virement, name="rechercher_client"),
    path("effectuer-virement/", views.effectuer_virement, name="effectuer_virement"),
    path("clients/", views.liste_clients, name="liste_clients"),
    path("clients/<int:client_id>/", views.modifier_client, name="modifier_client"),
    path(
        "clients/supprimer/<int:client_id>/",
        views.supprimer_client,
        name="supprimer_client",
    ),
    path("operations-jour/", views.operations_jour, name="operations_jour"),
    path("operations-semaine/", views.operations_semaine, name="operations_semaine"),
    path("operations-mois/", views.operations_mois, name="operations_mois"),
    path("auth-required-page/", views.auth_required_page, name="auth_required_page"),
    path("auth_required_op/", views.auth_required_op, name="auth_required_op"),
    path("auth_required_pret/", views.auth_required_pret, name="auth_required_pret"),
    path("pret/", views.clients_eligibles, name="pret"),
    path("effectuer-operation/", views.effectuer_operation, name="effectuer_operation"),
    path("commissions/", views.commissions_clients, name="commissions_clients"),
    path("prets-confirmes/", views.liste_prets_confirmes, name="liste_prets_confirmes"),
    path(
        "clients/<int:client_id>/demande-pret/", views.demande_pret, name="demande_pret"
    ),
    path(
        "confirmation/<int:demande_pret_id>/", views.confirmation, name="confirmation"
    ),
    path('effectuer_versement/<int:pret_id>/', views.effectuer_versement, name='effectuer_versement'),
]
