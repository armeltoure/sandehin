from django.contrib import admin
from .models import Collection,CommissionClient, CompteBancaire, Depot, Operation, Pret, Client
from .forms import ClientForm



class PretInline(admin.TabularInline):
    model = Pret
    extra = 0  # Ceci supprimera le formulaire vide supplémentaire pour ajouter de nouveaux prêts


class CompteBancaireAdmin(admin.ModelAdmin):
    list_display = ('client', 'solde_initial', 'solde_actuel', 'nb_depot')  # Ajoutez 'nb_depot' ici




class VilleAdmin(admin.ModelAdmin):
    list_display = ('nom',)


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('collection_name', )


class OperationAdmin(admin.ModelAdmin):
    list_display = ('type_operation', 'montant')

    def client_info(self, obj):
        return obj.client.nom_prenoms  # Affiche le nom du client associé

    client_info.short_description = 'Nom du client'

    def operation_type(self, obj):
        return ', '.join([op.type_operation for op in obj.operations.all()])  # Affiche les types d'opérations

    operation_type.short_description = 'Types d\'opérations'


class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom_prenoms','date_naissance','lieu_naissance', 'numero_telephone', 'numero_cni', 'profession', 'localite',  'ville','nombre_depot')
    search_fields = ['nom_prenoms', 'numero_telephone', 'numero_cni', 'profession', 'localite', 'ville']

    def montant(self, obj):
        # Remplacez 'montant' par le nom correct du champ ou de la méthode que vous souhaitez afficher
        return obj.montant  # Assurez-vous que 'montant' est un champ ou une méthode dans votre modèle



# Enregistrez les classes d'administration
admin.site.register(Client, ClientAdmin)
admin.site.register(CompteBancaire, CompteBancaireAdmin)
admin.site.register(Operation, OperationAdmin)
admin.site.register(Collection, CollectionAdmin)
