# Backtrader-optuna
Estrategia básica para trading con backtrader y optuna.
Script escrito para Python 3.7, utiliza las librerías backtrader y optuna para encontrar porcentajes de ganancia y perdidas optimos para tendencias alcista y bajistas.
Utiliza un algoritmo evolutivo de maximización para encontrarlos.
Los datos necesarios son descargados desde el exchange Binance.
En la primera ejecución se descargará y guardará el archivo CSV con los datos.

## Instalar dependencias
python pip install -r requirements.txt

## Uso
python criptofind.py -s SLP/USDT -t 2h -hora "02/05/2021 00:00:00" -cash 100 -cycle 100

## Ayuda
python criptofind.py

## A mejorar
No tengo mas tiempo que dedicarle a este proyecto, así que debo avisar de que durante la primera ejecución se descargan los datos en formato CSV, y no es hasta la segunda ejecución que una vez comprobado que se han descargado los datos pasa a realizar el proceso de analisis y búsqueda.
