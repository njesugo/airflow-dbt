select
    id_commande,
    id_client,
    montant,
    date_commande,
    _loaded_at
from {{ source('ventes', 'commandes') }}
where montant is not null
