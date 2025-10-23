NO-INSTALL MODE (Python 3.13 compatible)
===========================================

Dieses Minimal-Set benötigt KEINE Zusatz-Installation.
Es nutzt NUR die Standardbibliothek (keine externen Pakete).

Was es macht:
- Fragt dich im Terminal nach: Verticals, Länder, Mindest-Visits, Titel-Regex
- Generiert Demo-Firmendaten (Similarweb-Mock)
- Simuliert Salesforce-Check & ZoomInfo-Personas
- Schreibt CSV-Dateien in data/outputs/: 
  - final_companies.csv
  - final_leads.csv
  - sn_accounts_upload.csv
  - needs_salesnav.csv

So startest du es (Windows PowerShell):
1) In den Ordner wechseln:
   cd "C:\Users\thorothe1\OneDrive - Publicis Groupe\Documents\Ai agent outreach Oc 2025\ai-sales-agent-poc-noinstall"

2) Script ausführen (Python 3.13):
   py -3.13 minimal_run.py
   (oder)
   python minimal_run.py

3) CSV-Dateien findest du danach in data\outputs\
   Diese lassen sich direkt mit Excel öffnen.

Hinweis: Kein XLSX in diesem Modus (dafür wäre ein zusätzliches Paket nötig).
