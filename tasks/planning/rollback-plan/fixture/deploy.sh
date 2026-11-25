#!/bin/bash
# Current deployment script (simple restart-based)
set -e

echo "Stopping service..."
systemctl stop orders-service

echo "Running migrations..."
psql "$DATABASE_URL" -f migrate.sql

echo "Starting service..."
systemctl start orders-service

echo "Done."
