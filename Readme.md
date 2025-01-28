# Discord Wetter Status

Dieses Programm aktualisiert deinen Discord-Status mit dem aktuellen Wetter und der aktuellen Uhrzeit für einen bestimmten Ort. Es ruft Wetterdaten von der WeatherAPI ab und aktualisiert deinen Discord-Status jede Minute.

## Funktionen

- Ruft aktuelle Wetterdaten von der WeatherAPI ab.
- Aktualisiert den Discord-Status mit Wetter-Emoji und aktueller Uhrzeit.
- Konfigurierbarer Standort über Umgebungsvariablen.

## Umgebungsvariablen

Die folgenden Umgebungsvariablen müssen gesetzt werden:

- `DISCORD_TOKEN`: Dein Discord-Token.
- `WEATHER_API_KEY`: Dein WeatherAPI-Schlüssel.
- `LATITUDE`: Breitengrad des Standorts für Wetterdaten.
- `LONGITUDE`: Längengrad des Standorts für Wetterdaten.

## Installation

### Mit Coolify

1. **Erstelle eine neue Anwendung in Coolify**:
    - Gehe zu deinem Coolify-Dashboard.
    - Klicke auf "Neu" und wähle "Öffentliche Repository".
    - Gib https://github.com/PermanentlyBanned/Discord-Weather-Status.git ein.
    - Als Build Pack wähle "Docker Compose".

2. **Konfiguriere Umgebungsvariablen**:
    - In der Coolify-Anwendungskonfiguration setze die folgenden Umgebungsvariablen:
        - `DISCORD_TOKEN`: Dein Discord-Token.
        - `WEATHER_API_KEY`: Dein WeatherAPI-Schlüssel.
        - `LATITUDE`: Breitengrad des Standorts für Wetterdaten.
        - `LONGITUDE`: Längengrad des Standorts für Wetterdaten.

3. **Deploy die Anwendung**:
    - Klicke auf "Deploy", um die Anwendung zu starten.
    - Coolify wird das Docker-Image bauen und den Container starten.

## Koordinaten herausfinden
Um deine eigenen Koordinaten (Breiten- und Längengrad) zu erhalten, kannst du beispielsweise
[Google Maps](https://maps.google.com) oder [latlong.net](https://www.latlong.net/) verwenden.

## Lokal ausführen

1. **Repository klonen**: Klone dieses Repository auf deinen lokalen Rechner.

    ```sh
    git clone https://github.com/PermanentlyBanned/Discord-Weather-Status.git
    cd Discord-Weather-Status
    ```

2. **Umgebungsvariablen setzen**: Erstelle eine `.env`-Datei im Projektverzeichnis und füge die erforderlichen Umgebungsvariablen hinzu.

    ```env
    DISCORD_TOKEN=dein_discord_token
    WEATHER_API_KEY=dein_weather_api_key
    LATITUDE=dein_lat
    LONGITUDE=dein_long
    ```

3. **Docker-Container bauen und ausführen**:

    ```sh
    docker-compose up --build
    ```

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.
