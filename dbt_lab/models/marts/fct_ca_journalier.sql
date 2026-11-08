select
    date_commande,
    count(*) as nb_commandes,
    sum(montant) as ca
from {{ ref('stg_commandes') }}
group by 1
