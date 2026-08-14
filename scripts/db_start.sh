#!/data/data/com.termux/files/usr/bin/bash
pg_ctl -D "$PREFIX/var/lib/postgresql" -l "$PREFIX/var/lib/postgresql/server.log" start
