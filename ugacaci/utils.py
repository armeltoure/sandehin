# utils.py
from .models import Client

def check_loan_eligibility(client):
    """
    Vérifie si un client est éligible à un prêt en fonction de certains critères.
    Cette fonction peut être personnalisée en fonction de vos critères d'éligibilité.

    Args:
    - client: Instance du modèle Client.

    Returns:
    - bool: True si le client est éligible, False sinon.
    """
    if client.nombre_depot >= 14 and client.montant >= 1000:
        return True
    else:
        return False
