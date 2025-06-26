Connected Repo: https://github.com/AsaTyr2018/MyLora

# Desktop-Client-Agent

Dieser Task beschreibt die Erstellung einer Desktop-Anwendung, die die Funktionen des MyLora Webinterfaces mittels der REST-API nachbildet. Die Anwendung soll in Python umgesetzt werden und kann auf beliebige GUI-Frameworks wie Tkinter oder PyQt zurückgreifen.

## Ziele

* Vollständige Darstellung der LoRA-Datenbank in einem Desktop-Programm.
* Nutzung der vorhandenen REST-Endpunkte (`/search`, `/grid_data`, `/categories`) sowie statische Pfade (`/uploads`).
* Download und Anzeige der Preview-Bilder und Safetensors-Dateien.
* Suchen, Filtern nach Kategorien und Detailansichten analog zur Web-Galerie.

## Arbeitsschritte

1. **Projektsetup**
   - Python-Umgebung mit den benötigten Bibliotheken (z. B. `requests`, gewähltes GUI-Toolkit).
   - Konfigurierbare Angabe der Serveradresse (Standard: `http://localhost:5000`).

2. **API-Kommunikation**
   - Wrapper-Modul erstellen, das die JSON-Endpunkte aufruft und die Antworten als Python-Objekte bereitstellt.
   - Endpunkte:
     - `GET /search`: Suche nach LoRA-Dateien.
     - `GET /grid_data`: Liefert Metadaten, Kategorien und ein Preview-Bild.
     - `GET /categories`: Liste aller Kategorien.
     - `GET /uploads/<datei>`: Zugriff auf Bilder und Modelle.

3. **GUI-Design**
   - Hauptfenster mit Listen- oder Kachelansicht für die Grid-Daten.
   - Suchfeld und Kategorieauswahl zur Filterung.
   - Anzeige eines zufälligen Preview-Bildes pro Eintrag (wie im Web-Gird).
   - Bei Auswahl eines Eintrags: Detailfenster mit allen zugehörigen Previews, Metadaten und Downloadmöglichkeit der `.safetensors`-Datei.

4. **Download- und Cache-Strategie**
   - Preview-Bilder bei Bedarf herunterladen und lokal cachen, um Ladezeiten zu verringern.
   - Downloadfunktion für Modelldateien inkl. Fortschrittsanzeige.

5. **Optionale Erweiterungen**
   - Mehrsprachiges Interface.
   - Offline-Nutzung mit lokaler Datenbankkopie.
   - Automatische Erkennung neuer Einträge (Polling oder WebSockets, falls ergänzt).

---

Die Desktop-Anwendung soll die Bedienung der MyLora-Datenbank für Nutzer erleichtern, die ihre Modelle ohne Browser verwalten möchten. Bei der Umsetzung ist darauf zu achten, dass alle Funktionen über die vorhandene REST-API abgedeckt werden, da keine zusätzlichen Endpunkte bereitstehen.
