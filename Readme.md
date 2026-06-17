# Deployment einer Web-Applikation mit Docker

## 1. Ziel der Aufgabe

Ziel der Aufgabe ist die Einrichtung eines Linux-Servers und das Deployment einer Python-Flask-Web-App als Docker-Container.

Die Web-App basiert auf einer OpenAPI-Spezifikation und einer Python-Implementierung mit Flask. Die Anwendung wird aus einem Git-Repository geladen, in einem Docker-Image verpackt und anschließend als Container auf dem Linux-System ausgeführt.

Der Server erfüllt folgende Anforderungen:

* statische IP-Adresse im lokalen Netzwerk
* lokaler Benutzer `willi` ohne Administratorrechte
* lokaler Benutzer `fernzugriff` mit sudo-Rechten
* SSH-Zugriff für Administration
* Deployment der Web-App als Docker-Container
* automatische Wiederherstellung nach einem Neustart
* vollständige Dokumentation der Einrichtung

## 2. Verwendete Umgebung

Verwendetes System:

* Ubuntu 26.04 in einer VirtualBox-VM
* Netzwerkmodus: Netzwerkbrücke
* Zugriff über Terminal und SSH
* Docker als Containerplattform
* Flask-Web-App aus einem GitHub-Repository

GitHub-Repository:

```text
https://github.com/alexanderniehaus96-gif/flask_server
```

Wichtige Projektdateien:

```text
FlaskServer.py
OpenAPI.yaml
requirements.txt
Dockerfile
README.md
templates/
```

Finale Netzwerkdaten im Schulnetzwerk:

```text
Interface:                 enp0s3
Statische IP-Adresse:      192.168.24.113/24
Gateway:                   192.168.24.254
DNS-Server:                172.28.28.3
Alternativer DNS-Server:   8.8.8.8
```

Die Web-App ist im Schulnetzwerk erreichbar unter:

```text
http://192.168.24.113:5000/
```

## 3. System aktualisieren

Nach der Installation von Ubuntu wurde das System aktualisiert.

```bash
sudo apt update
sudo apt upgrade -y
```

Zusätzlich wurden benötigte Programme installiert.

```bash
sudo apt install -y curl nano git net-tools openssh-server
```

Erläuterung:

* `curl` wird zum Testen der Web-App verwendet.
* `nano` wird zum Bearbeiten von Konfigurationsdateien im Terminal genutzt.
* `git` wird zum Klonen und Verwalten des Git-Repositorys verwendet.
* `net-tools` stellt zusätzliche Netzwerkwerkzeuge bereit.
* `openssh-server` ermöglicht den SSH-Zugriff auf den Server.

## 4. Tastaturbelegung konfigurieren

Da die Tastaturbelegung zunächst nicht korrekt eingestellt war, wurde sie neu konfiguriert.

```bash
sudo dpkg-reconfigure keyboard-configuration
```

Ausgewählte Optionen:

```text
Keyboard model: Generic 105-key PC
Country of origin: German
Keyboard layout: German
AltGr key: The default for the keyboard layout
Compose key: No compose key
```

Anschließend wurde die Konsolenkonfiguration übernommen und das System neu gestartet.

```bash
sudo setupcon
sudo reboot
```

## 5. Benutzer anlegen

Es wurden zwei lokale Benutzer angelegt.

```bash
sudo adduser willi
sudo adduser fernzugriff
```

Der Benutzer `willi` ist ein normaler Benutzer ohne Administratorrechte.

Der Benutzer `fernzugriff` wird für die Administration per SSH genutzt. Dafür wurde er der Gruppe `sudo` hinzugefügt.

```bash
sudo usermod -aG sudo fernzugriff
```

Die Gruppenzugehörigkeit wurde anschließend geprüft.

```bash
groups fernzugriff
```

In der Ausgabe muss die Gruppe `sudo` enthalten sein.

Beispiel:

```text
fernzugriff : fernzugriff sudo
```

Für den Benutzer `willi` wurde ein Testpasswort gesetzt, damit der Benutzer während der Prüfung verwendet werden kann.

```bash
sudo passwd willi
```

Der Benutzer `willi` besitzt keine Administratorrechte. Das Passwort wird dem Prüfer separat mitgeteilt und nicht im öffentlichen Repository dokumentiert.

## 6. SSH-Dienst einrichten

Der SSH-Dienst wurde gestartet und dauerhaft aktiviert.

```bash
sudo systemctl start ssh
sudo systemctl enable ssh
```

Der Status wurde geprüft mit:

```bash
sudo systemctl status ssh
```

Die Ausgabe zeigte:

```text
Active: active (running)
Loaded: loaded (...; enabled; ...)
```

Damit ist der Server per SSH erreichbar und der SSH-Dienst startet automatisch nach einem Neustart.

SSH-Verbindung vom Host-System:

```bash
ssh fernzugriff@192.168.24.113
```

## 7. Netzwerkkonfiguration prüfen

Zur Anzeige der aktuellen IP-Adresse wurde folgender Befehl verwendet:

```bash
hostname -I
```

Die Netzwerkinterfaces wurden mit folgendem Befehl geprüft:

```bash
ip a
```

Die Routing-Tabelle wurde mit folgendem Befehl geprüft:

```bash
ip route
```

Der DNS-Server wurde geprüft mit:

```bash
resolvectl status
```

Aus den Ausgaben wurden folgende Werte für das Schulnetzwerk ermittelt:

```text
Interface:  enp0s3
Gateway:    192.168.24.254
DNS:        172.28.28.3
```

## 8. Statische IP-Adresse konfigurieren

Die Netzwerkkonfiguration erfolgt über Netplan.

Die Konfigurationsdatei befindet sich unter:

```text
/etc/netplan/01-network-manager-all.yaml
```

Die Datei wurde bearbeitet mit:

```bash
sudo nano /etc/netplan/01-network-manager-all.yaml
```

Es wurde folgende statische IP-Konfiguration eingetragen:

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: no
      addresses:
        - 192.168.24.113/24
      routes:
        - to: default
          via: 192.168.24.254
      nameservers:
        addresses:
          - 172.28.28.3
          - 8.8.8.8
```

Die Berechtigungen der Netplan-Datei wurden angepasst.

```bash
sudo chmod 600 /etc/netplan/01-network-manager-all.yaml
```

Erläuterung:

Mit `chmod 600` darf nur der Besitzer der Datei diese lesen und bearbeiten. Andere Benutzer haben keine Rechte auf diese Datei.

Die Netzwerkkonfiguration wurde anschließend übernommen.

```bash
sudo netplan apply
```

Die Konfiguration wurde geprüft mit:

```bash
ip a
ip route
hostname -I
```

Die Erreichbarkeit des Netzwerks wurde getestet mit:

```bash
ping 8.8.8.8
ping archive.ubuntu.com
```

`ping 8.8.8.8` prüft die Internetverbindung.

`ping archive.ubuntu.com` prüft zusätzlich die DNS-Auflösung.

Die Ping-Befehle können mit `Strg + C` beendet werden.

## 9. Docker installieren

Docker wurde über die Paketverwaltung installiert.

```bash
sudo apt install -y docker.io
```

Der Docker-Dienst wurde gestartet und dauerhaft aktiviert.

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

Der Status wurde geprüft mit:

```bash
sudo systemctl status docker
```

Die Ausgabe zeigte:

```text
Active: active (running)
Loaded: loaded (...; enabled; ...)
```

Damit ist Docker aktiv und startet automatisch nach einem Neustart.

## 10. Docker-Installation testen

Die Docker-Installation wurde mit dem offiziellen Test-Container geprüft.

```bash
sudo docker run hello-world
```

Dieser Befehl lädt das Image `hello-world` herunter und startet einen Testcontainer. Die erfolgreiche Ausgabe bestätigt, dass Docker funktioniert und Images heruntergeladen sowie Container gestartet werden können.

Installierte Docker-Images wurden angezeigt mit:

```bash
sudo docker images
```

## 11. Git-Repository klonen

Das Projekt wurde aus dem GitHub-Repository geklont.

```bash
cd ~
git clone https://github.com/alexanderniehaus96-gif/flask_server.git
cd flask_server
```

Die Projektdateien wurden geprüft mit:

```bash
ls -la
```

Vorhandene wichtige Dateien:

```text
FlaskServer.py
OpenAPI.yaml
requirements.txt
Dockerfile
README.md
templates/
```

## 12. Dockerfile

Für das Deployment wird ein Dockerfile verwendet.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "FlaskServer.py"]
```

Erläuterung:

* `FROM python:3.12-slim` verwendet ein schlankes Python-Basisimage.
* `WORKDIR /app` legt das Arbeitsverzeichnis im Container fest.
* `COPY requirements.txt .` kopiert die Abhängigkeitsliste in das Image.
* `RUN pip install --no-cache-dir -r requirements.txt` installiert die benötigten Python-Bibliotheken im Image.
* `COPY . .` kopiert die restlichen Projektdateien in das Image.
* `EXPOSE 5000` dokumentiert, dass die Anwendung Port 5000 verwendet.
* `CMD ["python", "FlaskServer.py"]` startet die Flask-Anwendung.

Die Python-Abhängigkeiten werden nicht direkt auf dem Ubuntu-System installiert, sondern beim Bauen des Docker-Images innerhalb des Images.

Wichtig ist außerdem, dass die Flask-Anwendung im Python-Code auf `0.0.0.0` und Port `5000` lauscht, damit sie aus dem Container heraus erreichbar ist.

Beispiel:

```python
app.run(host="0.0.0.0", port=5000)
```

## 13. Docker-Image bauen

Das Docker-Image wurde im Projektordner gebaut.

```bash
sudo docker build -t flask-server .
```

Die erfolgreiche Ausgabe enthielt:

```text
Successfully built ...
Successfully tagged flask-server:latest
```

Danach wurde geprüft, ob das Image vorhanden ist.

```bash
sudo docker images
```

In der Ausgabe war unter anderem sichtbar:

```text
flask-server:latest
```

## 14. Container starten

Der Container wurde aus dem Image gestartet.

```bash
sudo docker run -p 5000:5000 -d --restart unless-stopped --name flask-server flask-server
```

Erläuterung:

* `-p 5000:5000` leitet Port 5000 des Hosts auf Port 5000 im Container weiter.
* `-d` startet den Container im Hintergrund.
* `--restart unless-stopped` sorgt dafür, dass der Container nach einem Neustart automatisch wieder startet, sofern er nicht manuell gestoppt wurde.
* `--name flask-server` vergibt den Containernamen `flask-server`.
* `flask-server` ist der Name des verwendeten Docker-Images.

## 15. Laufenden Container prüfen

Laufende Container wurden angezeigt mit:

```bash
sudo docker ps
```

Die Ausgabe zeigte den laufenden Container:

```text
NAMES: flask-server
PORTS: 0.0.0.0:5000->5000/tcp
STATUS: Up
```

Alle Container, auch beendete, können angezeigt werden mit:

```bash
sudo docker ps -a
```

## 16. Restart-Policy prüfen

Die Restart-Policy des Containers wurde geprüft mit:

```bash
sudo docker inspect flask-server --format='{{.HostConfig.RestartPolicy.Name}}'
```

Die Ausgabe lautete:

```text
unless-stopped
```

Damit ist sichergestellt, dass der Container nach einem Neustart automatisch wieder gestartet wird, solange er nicht manuell gestoppt wurde.

## 17. Web-App lokal testen

Die Web-App wurde direkt auf der VM getestet.

```bash
curl http://localhost:5000/
```

Die Ausgabe lieferte HTML der Flask-Web-App zurück. Damit ist bestätigt, dass die Anwendung im Container läuft und über Port 5000 erreichbar ist.

## 18. Web-App vom Host-System testen

Die Web-App wurde anschließend vom Host-System im Browser geöffnet.

```text
http://192.168.24.113:5000/
```

Die Seite war im Browser erreichbar. Damit ist bestätigt, dass die Portweiterleitung funktioniert und die Web-App auch außerhalb der VM erreichbar ist.

## 19. Neustart-Test

Das System wurde neu gestartet.

```bash
sudo reboot
```

Nach dem Neustart wurde geprüft, ob Docker aktiv ist.

```bash
sudo systemctl status docker
```

Außerdem wurde geprüft, ob der Container wieder läuft.

```bash
sudo docker ps
```

Die Ausgabe zeigte den laufenden Container `flask-server`.

Zusätzlich wurde die Anwendung erneut getestet.

```bash
curl http://localhost:5000/
```

Damit ist bestätigt, dass die Anwendung auch nach einem Neustart wieder verfügbar ist.

## 20. Nützliche Docker-Befehle zur Verwaltung

Container stoppen:

```bash
sudo docker stop flask-server
```

Container starten:

```bash
sudo docker start flask-server
```

Container entfernen:

```bash
sudo docker rm flask-server
```

Logs anzeigen:

```bash
sudo docker logs flask-server
```

Image neu bauen:

```bash
sudo docker build -t flask-server .
```

Container neu erstellen:

```bash
sudo docker stop flask-server
sudo docker rm flask-server
sudo docker run -p 5000:5000 -d --restart unless-stopped --name flask-server flask-server
```

## 21. Nützliche Netzwerkbefehle

IP-Adressen anzeigen:

```bash
hostname -I
```

Alle Netzwerkinterfaces anzeigen:

```bash
ip a
```

Routing-Tabelle anzeigen:

```bash
ip route
```

DNS-Status anzeigen:

```bash
resolvectl status
```

Netplan-Konfiguration bearbeiten:

```bash
sudo nano /etc/netplan/01-network-manager-all.yaml
```

Netplan-Dateirechte korrigieren:

```bash
sudo chmod 600 /etc/netplan/01-network-manager-all.yaml
```

Netplan-Konfiguration anwenden:

```bash
sudo netplan apply
```

## 22. Änderungen ins GitHub-Repository übertragen

Damit das GitHub-Repository alle für das Deployment notwendigen Dateien enthält, wurden die neu erstellten beziehungsweise angepassten Dateien in das Repository übertragen.

Zuerst wurde im Projektordner der Git-Status geprüft.

```bash
cd ~/flask_server
git status
```

Falls Git noch keinen Namen und keine E-Mail-Adresse für Commits kennt, müssen diese einmalig gesetzt werden.

```bash
git config --global user.name "Alexander Niehaus"
git config --global user.email "alexanderniehaus96@gmail.com"
```

Anschließend wurden die geänderten Dateien zum Commit hinzugefügt.

```bash
git add Dockerfile README.md
```

Der Commit wurde erstellt mit:

```bash
git commit -m "Dockerfile und Deployment-Dokumentation hinzugefuegt"
```

Da GitHub bei Git-Operationen über HTTPS kein normales Passwort mehr akzeptiert, wurde für den direkten Zugriff von der VM auf GitHub ein SSH-Key erstellt.

```bash
ssh-keygen -t ed25519 -C "alexanderniehaus96@gmail.com"
```

Der öffentliche Schlüssel wurde anschließend angezeigt.

```bash
cat ~/.ssh/id_ed25519.pub
```

Dieser öffentliche Schlüssel wurde im GitHub-Konto unter folgendem Menüpunkt hinterlegt:

```text
GitHub → Settings → SSH and GPG keys → New SSH key
```

Danach wurde das Git-Repository von HTTPS auf SSH umgestellt.

```bash
git remote set-url origin git@github.com:alexanderniehaus96-gif/flask_server.git
```

Die SSH-Verbindung zu GitHub wurde getestet.

```bash
ssh -T git@github.com
```

Beim ersten Verbindungsaufbau wurde GitHub als bekannter Host bestätigt.

```text
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
```

Die erfolgreiche Ausgabe lautete sinngemäß:

```text
Hi alexanderniehaus96-gif/flask_server! You've successfully authenticated, but GitHub does not provide shell access.
```

Beim ersten `git push` wurde der Push abgelehnt, weil im entfernten Repository bereits Änderungen vorhanden waren, die lokal noch nicht vorhanden waren.

```text
! [rejected] main -> main (fetch first)
```

Deshalb wurden zuerst die entfernten Änderungen übernommen.

```bash
git pull --rebase origin main
```

Anschließend konnten die lokalen Änderungen in das GitHub-Repository übertragen werden.

```bash
git push
```

Damit befinden sich die Deployment-Dateien, insbesondere `Dockerfile` und `README.md`, im GitHub-Repository.

## 23. Finaler Testablauf

Folgende Befehle dienen als abschließender Nachweis.

IP-Adresse prüfen:

```bash
hostname -I
```

Erwartete relevante Ausgabe:

```text
192.168.24.113
```

SSH-Status prüfen:

```bash
sudo systemctl status ssh
```

Docker-Status prüfen:

```bash
sudo systemctl status docker
```

Docker-Images anzeigen:

```bash
sudo docker images
```

Laufende Container anzeigen:

```bash
sudo docker ps
```

Restart-Policy prüfen:

```bash
sudo docker inspect flask-server --format='{{.HostConfig.RestartPolicy.Name}}'
```

Erwartete Ausgabe:

```text
unless-stopped
```

Web-App lokal testen:

```bash
curl http://localhost:5000/
```

Web-App im Browser testen:

```text
http://192.168.24.113:5000/
```

## 24. Ergebnis

Die Flask-Web-App wurde erfolgreich als Docker-Container auf dem Linux-System bereitgestellt.

Erfüllte Anforderungen:

* Linux-System eingerichtet
* statische IP-Adresse `192.168.24.113/24` eingerichtet
* Benutzer `willi` angelegt
* Benutzer `fernzugriff` mit sudo-Rechten angelegt
* SSH-Dienst aktiviert
* Docker installiert
* Docker mit `hello-world` getestet
* Git-Repository geklont
* Docker-Image aus dem Projekt gebaut
* Flask-Web-App als Container gestartet
* Port 5000 nach außen freigegeben
* Restart-Policy `unless-stopped` gesetzt
* Web-App lokal per `curl` erreichbar
* Web-App vom Host-System im Browser erreichbar
* Funktion nach Neustart geprüft
* Dockerfile und Dokumentation in das GitHub-Repository übertragen

Die Anwendung ist im Schulnetzwerk erreichbar unter:

```text
http://192.168.24.113:5000/
```
