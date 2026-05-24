#!/bin/sh

# Tenta migrate normal; se falhar por histórico inconsistente, ignora e sobe mesmo assim
python manage.py migrate --noinput --fake-initial || true

exec "$@"
