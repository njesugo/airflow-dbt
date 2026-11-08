import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

import duckdb

parser = argparse.ArgumentParser()
parser.add_argument("--stale", action="store_true", help="simule une source en retard (2 jours)")
args = parser.parse_args()

loaded_at = datetime.now(timezone.utc).replace(tzinfo=None)
if args.stale:
    loaded_at -= timedelta(days=2)

db_path = Path(__file__).resolve().parent.parent / "warehouse.duckdb"
con = duckdb.connect(str(db_path))
con.execute("create schema if not exists raw")
con.execute(f"""
    create or replace table raw.commandes as
    select i as id_commande,
           (i % 5) + 1 as id_client,
           round(10 + random() * 90, 2) as montant,
           date '2026-11-01' + cast(i % 7 as integer) as date_commande,
           timestamp '{loaded_at:%Y-%m-%d %H:%M:%S}' as _loaded_at
    from range(1, 51) t(i)
""")
print(f"50 lignes chargées, _loaded_at = {loaded_at}")
