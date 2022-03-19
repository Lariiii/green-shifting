#! /usr/bin/env bash
wait-for-it -s db:5432 -t 0 -- alembic upgrade heads
