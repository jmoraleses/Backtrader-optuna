# Backtrader-optuna
Estrategia básica para trading con backtrader y optuna.
Script escrito para Python 3.7, utiliza las librerías backtrader y optuna para encontrar máximos beneficios y mínimas perdidas. Utiliza un algoritmo evolutivo de maximización para encontrarlos.
Los datos necesarios son descargados desde el exchange Binance. Requiere clave API en archivo criptofind.py.

## Instalar dependencias
python pip install -r requirements.txt

## Uso
python criptofind.py -s SLP/USDT -t 2h -hora "02/05/2021 00:00:00" -cash 100 -cycle 100
python criptofind.py -s BTC/USDT -t 30m -hora "02/05/2021 00:00:00" -cash 100 -cycle 1000

## Ayuda
python criptofind.py
