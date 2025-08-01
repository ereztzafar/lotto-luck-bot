name: AstroLotto Forecast Bot

on:
  workflow_dispatch:   # מאפשר הרצה ידנית דרך GitHub Actions
  schedule:
    - cron: '0 5-22/3 * * *'  # מריץ כל 3 שעות בין 05:00 ל־22:00

jobs:
  run-astrolotto:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run forecast bot
      run: python run.py


