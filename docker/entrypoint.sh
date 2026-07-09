#!/usr/bin/env sh
set -e

# Wait for the database to accept connections when using Postgres.
if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for database..."
    python - <<'PY'
import os, time, sys
import dj_database_url
import psycopg

cfg = dj_database_url.parse(os.environ["DATABASE_URL"])
dsn = (
    f"host={cfg['HOST']} port={cfg.get('PORT') or 5432} "
    f"dbname={cfg['NAME']} user={cfg['USER']} password={cfg['PASSWORD']}"
)
for _ in range(30):
    try:
        psycopg.connect(dsn).close()
        print("Database is ready.")
        sys.exit(0)
    except Exception:
        time.sleep(1)
print("Database not reachable, continuing anyway.")
PY
fi

echo "Applying migrations..."
python manage.py migrate --noinput

exec "$@"
