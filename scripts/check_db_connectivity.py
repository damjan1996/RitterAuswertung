#!/usr/bin/env python
"""
Einfaches Skript zum Testen der SQL Server-Verbindung.
Direkt ausführbar, nicht für PyTest gedacht.
"""

import pyodbc
import sys
import time
import os

# Füge das Hauptverzeichnis zum Pythonpfad hinzu
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sys.path.insert(0, project_dir)

# Importiere die Datenbankkonfiguration
from config.database import DATABASE_CONFIG


def check_connection(server, database, username, password, driver):
    """
    Testet eine einzelne Verbindungskonfiguration und gibt das Ergebnis aus
    """
    print(f"\nTeste Verbindung mit:")
    print(f"  Server: {server}")
    print(f"  Datenbank: {database}")
    print(f"  Benutzer: {username}")
    print(f"  Treiber: {driver}")

    # Verbindungsstring erstellen
    conn_str = (
        f"DRIVER={driver};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"Trusted_Connection=no;"
        f"Connection Timeout=30;"
    )

    try:
        print("Verbindungsaufbau...")
        start_time = time.time()
        conn = pyodbc.connect(conn_str)
        end_time = time.time()
        duration = end_time - start_time
        print(f"✓ Verbindung erfolgreich hergestellt (in {duration:.2f} Sekunden)")

        # Eine einfache Abfrage ausführen
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        print(f"✓ SQL Server-Version: {row[0][:60]}...")

        # Prüfen, ob die angegebene Datenbank existiert
        cursor.execute("SELECT DB_NAME()")
        db_name = cursor.fetchone()[0]
        print(f"✓ Verbunden mit Datenbank: {db_name}")

        # Tabellen auflisten
        print("\nVerfügbare Tabellen in BIRD-Schema:")
        cursor.execute(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'BIRD' ORDER BY TABLE_NAME")
        tables = cursor.fetchall()
        if tables:
            for i, table in enumerate(tables, 1):
                print(f"  {i}. {table[0]}")
        else:
            print("  Keine Tabellen im BIRD-Schema gefunden.")

        # Verbindung schließen
        cursor.close()
        conn.close()
        print("\n✓ Test erfolgreich abgeschlossen")
        return True

    except pyodbc.Error as e:
        print(f"✗ Fehler: {e}")
        return False


def list_drivers():
    """Listet alle verfügbaren ODBC-Treiber auf"""
    print("\nVerfügbare ODBC-Treiber:")
    drivers = pyodbc.drivers()
    if drivers:
        for i, driver in enumerate(drivers, 1):
            print(f"  {i}. {driver}")
    else:
        print("  Keine ODBC-Treiber gefunden.")
    return drivers


def main():
    print("=== SQL Server Verbindungstest ===")

    # Verfügbare Treiber anzeigen
    drivers = list_drivers()

    # Verbindungsdaten aus der Konfiguration laden
    config = DATABASE_CONFIG
    server = config['server']
    database = config['database']
    username = config['username']
    password = config['password']
    driver = config['driver']

    print(f"\nVerwendete Konfiguration aus config/database.py:")
    print(f"  Server: {server}")
    print(f"  Datenbank: {database}")
    print(f"  Benutzer: {username}")
    print(f"  Treiber: {driver}")

    # Standard-Verbindungstest
    print("\n------- Test 1: Standardkonfiguration -------")
    success = check_connection(server, database, username, password, driver)

    # Wenn der erste Test fehlschlägt, weitere Optionen versuchen
    if not success:
        print("\n------- Test 2: Ohne Instanzname -------")
        server_ip = server.split('\\')[0]
        check_connection(server_ip, database, username, password, driver)

        print("\n------- Test 3: Mit explizitem Port 1433 -------")
        check_connection(f"{server_ip},1433", database, username, password, driver)

        # Andere SQL Server Treiber versuchen
        for alt_driver in drivers:
            if "SQL Server" in alt_driver and alt_driver != driver:
                print(f"\n------- Test mit alternativem Treiber: {alt_driver} -------")
                check_connection(server, database, username, password, alt_driver)

    print("\nTests abgeschlossen.")


if __name__ == "__main__":
    main()