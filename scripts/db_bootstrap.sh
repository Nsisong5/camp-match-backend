#!/data/data/com.termux/files/usr/bin/bash
set -e
# pkg install -y postgresql # Skip if already installed
mkdir -p "$PREFIX/var/lib/postgresql"
initdb "$PREFIX/var/lib/postgresql"
pg_ctl -D "$PREFIX/var/lib/postgresql" -l "$PREFIX/var/lib/postgresql/server.log" start
sleep 2
createuser -s -e camp_match
createdb -O camp_match camp_match_dev
pg_ctl -D "$PREFIX/var/lib/postgresql" stop
echo "Bootstrap complete. Use scripts/db_start.sh to start the server."
