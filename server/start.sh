#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python init_db.py
python main.py
