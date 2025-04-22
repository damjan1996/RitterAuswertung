#!/usr/bin/env python
"""
Erweitertes Skript zum Testen der SQL Server-Verbindung.
Testet verschiedene Konfigurationen und Treiber.
"""

import pyodbc
import sys
import time
import os
import socket
import subprocess
from contextlib import closing

# Füge das Hauptverzeichnis zum Pythonpfad hinzu
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sys.path.insert(0, project_dir)


def is_port_open(host, port):
    """Überprüft, ob ein Port auf einem Host erreichbar ist"""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(5)
        try:
            result = sock.connect_ex((host, port))
            return result == 0
        except socket.error:
            return False


def check_connection(server, database, username, password, driver, show_conn_string=False):
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
        f"Connection Timeout=10;"
    )

    if show_conn_string:
        # Passwort maskieren für die Ausgabe
        masked_conn_str = conn_str.replace(password, "********")
        print(f"  Verbindungsstring: {masked_conn_str}")

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
        try:
            print("\nVerfügbare Tabellen in BIRD-Schema:")
            cursor.execute(
                "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'BIRD' ORDER BY TABLE_NAME")
            tables = cursor.fetchall()
            if tables:
                for i, table in enumerate(tables, 1):
                    print(f"  {i}. {table[0]}")
            else:
                print("  Keine Tabellen im BIRD-Schema gefunden.")
        except pyodbc.Error as e:
            print(f"  Warnung: Konnte Tabellen nicht auflisten: {e}")

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
    sql_drivers = [driver for driver in drivers if "SQL Server" in driver]

    if sql_drivers:
        for i, driver in enumerate(sql_drivers, 1):
            print(f"  {i}. {driver}")
    else:
        print("  Keine SQL Server ODBC-Treiber gefunden!")
    return sql_drivers


def check_network():
    """Prüft die Netzwerkverbindung zum SQL Server"""
    server = "116.202.224.248"
    print(f"\nPrüfe Netzwerkverbindung zu {server}:")

    # Ping testen
    print(f"  Ping-Test zu {server}...")
    try:
        ping_output = subprocess.run(
            ["ping", "-n", "3", server],
            capture_output=True,
            text=True,
            check=False
        )
        if "Received = 0" in ping_output.stdout:
            print(f"✗ Ping fehlgeschlagen: Server antwortet nicht auf ICMP")
        else:
            print(f"✓ Ping erfolgreich")
            print(f"  {ping_output.stdout.splitlines()[-1]}")
    except Exception as e:
        print(f"✗ Ping-Befehl konnte nicht ausgeführt werden: {e}")

    # Standard SQL Server Port testen
    port = 1433
    print(f"  Prüfe Port {port} (SQL Server Standard)...")
    if is_port_open(server, port):
        print(f"✓ Port {port} ist offen und erreichbar")
    else:
        print(f"✗ Port {port} ist nicht erreichbar")

    # Browser Service Port testen
    port = 1434
    print(f"  Prüfe Port {port} (SQL Server Browser)...")
    if is_port_open(server, port):
        print(f"✓ Port {port} ist offen und erreichbar")
    else:
        print(f"✗ Port {port} ist nicht erreichbar")


def main():
    print("=== SQL Server Verbindungstest ===")

    # Netzwerk checken
    check_network()

    # Verfügbare Treiber anzeigen
    sql_drivers = list_drivers()
    if not sql_drivers:
        print("\nERROR: Keine SQL Server ODBC-Treiber gefunden. Bitte installieren Sie einen SQL Server ODBC-Treiber.")
        return

    # Verbindungsdaten
    server = "116.202.224.248\\SQLEXPRESS"
    database = "RdRaumbuch"
    username = "sa"
    password = "YJ5C19QZ7ZUW!"

    # Standard-Verbindungstest mit jedem verfügbaren SQL Server Treiber
    success = False

    print("\n--------- Test mit Standard-Server-Angabe ---------")
    for driver in sql_drivers:
        print(f"\n------- Test mit Treiber: {driver} -------")
        if check_connection(server, database, username, password, driver):
            success = True
            print(f"✓ Verbindung mit {driver} erfolgreich!")
            break

    # Wenn kein Erfolg, versuche mit nur der IP
    if not success:
        print("\n--------- Test mit nur der IP-Adresse ---------")
        server_ip = server.split('\\')[0]
        for driver in sql_drivers:
            print(f"\n------- Test mit Treiber: {driver} -------")
            if check_connection(server_ip, database, username, password, driver):
                success = True
                print(f"✓ Verbindung mit {driver} erfolgreich!")
                break

    # Wenn immer noch kein Erfolg, versuche mit IP und Port
    if not success:
        print("\n--------- Test mit IP und Port 1433 ---------")
        for driver in sql_drivers:
            print(f"\n------- Test mit Treiber: {driver} -------")
            if check_connection(f"{server_ip},1433", database, username, password, driver):
                success = True
                print(f"✓ Verbindung mit {driver} erfolgreich!")
                break

    # Wenn immer noch kein Erfolg, versuche mit anderen häufigen Ports
    if not success:
        for port in [1434, 14330, 14331, 14333, 14334, 1401, 1402]:
            print(f"\n--------- Test mit Port {port} ---------")
            if check_connection(f"{server_ip},{port}", database, username, password, sql_drivers[0]):
                success = True
                print(f"✓ Verbindung über Port {port} erfolgreich!")
                break

    if not success:
        print("\n✗ Alle Verbindungsversuche fehlgeschlagen.")
        print("\nMögliche Probleme:")
        print("1. Der SQL Server ist nicht erreichbar (Firewall, VPN benötigt?)")
        print("2. Der SQL Server akzeptiert keine Remoteverbindungen")
        print("3. Die Benutzeranmeldedaten sind ungültig")
        print("4. Die SQL Server-Instanz läuft nicht oder lauscht nicht auf den erwarteten Ports")

    print("\nTests abgeschlossen.")


if __name__ == "__main__":
    main()