#!/bin/bash
set -e 


echo "Running database migrations..."
cd /app/models/db_schemes/miniragdb/
alembic upgrade head
cd /app