# Airflow + dbt Core : contrôler la fraîcheur des données avant de construire

Mini-projet local qui montre comment **empêcher un pipeline de produire des chiffres périmés** : avant chaque `dbt build`, Airflow vérifie la fraîcheur de la source avec `dbt source freshness`. Si les données sont trop vieilles, le pipeline s'arrête.

## Le principe

```
ingest  ->  source_freshness  ->  dbt_build
(charge     (dbt source           (dbt build :
 les         freshness)            models + tests)
 données)
```

- `ingest` charge une


 une table brute `raw.commandes` dans DuckDB, avec une colonne `_loaded_at`.
- `source_freshness` compare `max(_loaded_at)` à l'heure actuelle. Seuils : avertissement à 12 h, erreur à 24 h.
- `dbt_build` construit les models et lance les tests, seulement si la fraîcheur est valide.

Si la fraîcheur est en erreur, la commande dbt retourne un code de sortie non nul : la tâche Airflow échoue et `dbt_build` n'est pas exécuté (état « échec en amont »).

## Stack

| Outil | Rôle |
|---|---|
| DuckDB | Entrepôt local (un simple fichier) |
| dbt Core + dbt-duckdb | Transformation, tests, fraîcheur des sources |
| Apache Airflow 3 (`standalone`) | Orchestration |
| WSL + VS Code | Environnement de développement |

## Structure

```
airflow-dbt-lab/
├── airflow_home/dags/pipeline_dbt.py   # DAG Airflow
├── scripts/ingest.py                   # génère la table brute (option --stale)
├── dbt_lab/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── staging/                    # source, stg_commandes, tests
│       └── marts/                      # fct_ca_journalier
└── start_airflow.sh                    # lance Airflow avec la bonne config
```

## Installation

Prérequis : Linux ou WSL, Python 3, [`uv`](https://docs.astral.sh/uv/).

Le DAG utilise le chemin `~/airflow-dbt-lab`, donc le dépôt doit être cloné dans ce dossier :

```bash
git clone git@github.com:njesugo/airflow-dbt.git ~/airflow-dbt-lab
cd ~/airflow-dbt-lab

# Environnement dbt
python3 -m venv venv-dbt
source venv-dbt/bin/activate
pip install dbt-duckdb duckdb
deactivate

# Environnement Airflow (deux venv séparés pour éviter les conflits de dépendances)
uv venv venv-airflow --python 3.12
source venv-airflow/bin/activate
AIRFLOW_VERSION=3.4.0
uv pip install "apache-airflow==${AIRFLOW_VERSION}" \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-3.12.txt"
deactivate
```

## Utilisation

### 1. Tester dbt à la main

```bash
venv-dbt/bin/python scripts/ingest.py
cd dbt_lab
../venv-dbt/bin/dbt source freshness --profiles-dir .
../venv-dbt/bin/dbt build --profiles-dir .
```

### 2. Lancer Airflow

```bash
./start_airflow.sh
```

Ouvrir `http://localhost:8080`. L'utilisateur est `admin`, et le mot de passe est affiché dans le terminal (ou dans `airflow_home/simple_auth_manager_passwords.json.generated`). Déclencher le DAG `pipeline_dbt`.

## Démonstration

**Run nominal** : les trois tâches réussissent.

![Run réussi](docs/run_ok.png)

**Source en retard** : en ajoutant `--stale` à la commande de la tâche `ingest`, les données chargées ont 2 jours. `source_freshness` échoue et `dbt_build` n'est pas exécuté.

![Run avec source périmée](docs/run_stale.png)

## Ce que ce projet illustre

- Sources dbt avec `loaded_at_field` et seuils `warn_after` / `error_after`.
- Organisation en couches (staging en vue, marts en table) et tests `unique` / `not_null`.
- Intégration de dbt dans un orchestrateur : le code de sortie de dbt pilote l'état des tâches.
- Séparation des environnements Python (dbt et Airflow).

## Pistes d'amélioration

- Utiliser un `warn_after` seul pour distinguer un avertissement d'une erreur bloquante.
- Ajouter un test qui échoue volontairement (doublon d'`id_commande`) pour voir `dbt build` s'arrêter sur la qualité.
- Rendre le chemin du projet configurable (il est écrit en dur dans le DAG).
- Ajouter des alertes (e-mail ou Slack) en cas d'échec.
- Remplacer DuckDB par BigQuery ou Snowflake.
