"""
Datenbankeinstellungen für die RitterDigitalAuswertung-Anwendung.
Enthält Verbindungsparameter für die SQL Server Datenbank.
"""

# SQL Server Verbindungsparameter
DATABASE_CONFIG = {
    'server': '116.202.224.248',  # Direkte IP ohne Instanzname
    'database': 'RdRaumbuch',
    'username': 'sa',
    'password': 'YJ5C19QZ7ZUW!',
    'driver': '{ODBC Driver 17 for SQL Server}',
    'trusted_connection': 'no',
    'timeout': 30
}

# Default ID für den Standort, falls nicht explizit angegeben
DEFAULT_STANDORT_ID = 1

# SQL-Query für die Raumbuch-Auswertung
RAUMBUCH_QUERY = """
SELECT
  Raumbuch.ID
 ,Raumbuch.Raumnummer
 ,Bereich.Bezeichnung Bereich
 ,Gebaeudeteil.Bezeichnung Gebaeudeteil
 ,Etage.Bezeichnung Etage
 ,Raumbuch.Bezeichnung
 ,Reinigungsgruppe.Bezeichnung RG
 ,Raumbuch.qm
 ,Raumbuch.Anzahl
 ,Reinigungsintervall.Bezeichnung Intervall
 ,ReinigungsintervallTage.Reinigungstage RgJahr
 ,ROUND(ReinigungsintervallTage.Reinigungstage * 4.33333 / 52,2) RgMonat
 ,ROUND(Raumbuch.qm * ReinigungsintervallTage.Reinigungstage * 4.33333 / 52,2) qmMonat
 ,CASE WHEN Raumbuch.Anzahl = 7 THEN ROUND((Raumbuch.qm / Raumbuch.qmStunde * ReinigungsintervallTage.Reinigungstage * Standort.Preis7Tage ) / 12,2) ELSE ROUND((Raumbuch.qm / Raumbuch.qmStunde * ReinigungsintervallTage.Reinigungstage * Standort.Preis ) / 12,2) END WertMonat
 ,ROUND(Raumbuch.qm/Raumbuch.qmStunde,3) StundenTag
 ,ROUND(ROUND(ReinigungsintervallTage.Reinigungstage * 4.33333 / 52,2) * ROUND(Raumbuch.qm/Raumbuch.qmStunde,3),2) StundenMonat
 ,CASE WHEN Raumbuch.Anzahl = 7 THEN ROUND((Raumbuch.qm / Raumbuch.qmStunde * ReinigungsintervallTage.Reinigungstage * Standort.Preis7Tage ) / 12,2) * 12 ELSE ROUND((Raumbuch.qm / Raumbuch.qmStunde * ReinigungsintervallTage.Reinigungstage * Standort.Preis ) / 12,2) * 12 END WertJahr
 ,Raumbuch.qmStunde
 ,ReinigungsTage.Bezeichnung Reinigungstage
 ,Raumbuch.Bemerkung
 ,Raumbuch.Reduzierung
FROM BIRD.Raumbuch WITH (NOLOCK)
INNER JOIN BIRD.Standort WITH (NOLOCK) ON Standort.ID = Raumbuch.Standort_ID
INNER JOIN BIRD.Bereich WITH (NOLOCK) ON Bereich.ID = Raumbuch.Bereich_ID AND Bereich.Standort_ID = Raumbuch.Standort_ID
INNER JOIN BIRD.Gebaeudeteil WITH (NOLOCK) ON Gebaeudeteil.ID = Raumbuch.Gebaeudeteil_ID AND Gebaeudeteil.Standort_ID = Raumbuch.Standort_ID
INNER JOIN BIRD.Etage WITH (NOLOCK) ON Etage.ID = Raumbuch.Etage_ID  AND Etage.Standort_ID = Raumbuch.Standort_ID
INNER JOIN BIRD.Reinigungsgruppe WITH (NOLOCK) ON Reinigungsgruppe.ID = Raumbuch.Reinigungsgruppe_ID
INNER JOIN BIRD.Reinigungsintervall WITH (NOLOCK) ON Reinigungsintervall.ID = Raumbuch.Reinigungsintervall_ID
LEFT OUTER JOIN BIRD.ReinigungsTage WITH (NOLOCK) ON ReinigungsTage.ID = Raumbuch.ReinigungsTage_ID
LEFT OUTER JOIN BIRD.ReinigungsintervallTage WITH (NOLOCK) ON ReinigungsintervallTage.Reinigungsintervall_ID = Raumbuch.Reinigungsintervall_ID
  AND ReinigungsintervallTage.Anzahl = Raumbuch.Anzahl
WHERE Raumbuch.Standort_ID = ?
ORDER BY
  Gebaeudeteil.Bezeichnung
 ,Etage.Bezeichnung
 ,Bereich.Bezeichnung
 ,Raumbuch.Raumnummer
 ,Raumbuch.Bezeichnung
"""

# Query, um alle verfügbaren Standorte zu bekommen
STANDORTE_QUERY = """
SELECT ID, Bezeichnung 
FROM BIRD.Standort 
ORDER BY Bezeichnung
"""