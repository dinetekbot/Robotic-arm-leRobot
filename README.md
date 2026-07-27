# 🤖 Robotic-arm-leRobot — Guide de Prise en Main (SO-ARM100)

Ce dépôt contient le code de contrôle et la configuration complète pour piloter le bras robotique **SO-ARM100 (6 axes)** avec **LeRobot v0.6.0** (Hugging Face) sans nécessiter de bras Leader physique.

---

## 🛠️ 1. Matériel Requis

- **Bras SO-ARM100** avec 6 servomoteurs Feetech STS3215 (IDs 1 à 6).
- **Carte d'interface USB-Série** (ex: Seeed Studio XIAO) branchée sur le PC (`/dev/ttyACM0`).
- **Alimentation externe 6V - 7.4V (4A recommandé)** branchée sur la carte du bras (⚠️ L'alimentation USB 5V est insuffisante pour faire tourner les moteurs).

---

## 📥 2. Installation de Zéro

### Étape 2.1 : Cloner le dépôt
```bash
cd ~/Documents
mkdir -p Hope/Robotics && cd Hope/Robotics
git clone https://github.com/dinetekbot/Robotic-arm-leRobot.git
cd Robotic-arm-leRobot
```

### Étape 2.2 : Créer l'environnement virtuel Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install lerobot[feetech]
```

### Étape 2.3 : Configurer les permissions du port USB
```bash
sudo chmod 666 /dev/ttyACM0
```

---

## 🧪 3. Diagnostic & Calibration

### Étape 3.1 : Diagnostiquer les 6 servos (Lecture seule)
```bash
python3 diagnostic_bras.py
```
*(Vérifie que les 6 servos répondent et que la tension est d'environ 6V)*.

### Étape 3.2 : Exécuter la Calibration Officielle
```bash
lerobot-calibrate --robot.type=so100_follower --robot.port=/dev/ttyACM0 --robot.id=my_arm
```
1. Placer le bras en position neutre/centre → Appuyer sur **ENTRÉE**.
2. Faire bouger **chaque articulation manuellement de son min à son max** (sans forcer sur les fils).
3. Une fois les plages enregistrées → Appuyer sur **ENTRÉE**.
4. Le fichier de calibration sera généré dans `~/.cache/huggingface/lerobot/calibration/robots/so_follower/my_arm.json`.

---

## 🕹️ 4. Utilisation

### Tester les positions calibrées en direct (° et %)
```bash
python3 test_calibrated_positions.py
```

### Lancer le Contrôleur Interactif Complexe (6 Axes)
```bash
python3 control_bras_interactif.py
```

**Commandes interactives disponibles :**
- `open` : Ouvrir la pince (100%)
- `close` : Fermer la pince (0%)
- `gripper <0-100>` : Régler l'ouverture de la pince
- `pan <degrés>` : Rotation base (`shoulder_pan`)
- `lift <degrés>` : Inclinaison épaule (`shoulder_lift`)
- `elbow <degrés>` : Flexion coude (`elbow_flex`)
- `wflex <degrés>` : Flexion poignet (`wrist_flex`)
- `wroll <degrés>` : Rotation poignet (`wrist_roll`)
- `home` : Repli en position repos de sécurité
- `status` : Afficher les angles en temps réel
- `quit` : Quitter proprement

---

## 🌐 5. Serveur TCP Réseau

Pour lancer le serveur de contrôle à distance :
```bash
python3 remote_control_server.py
```

---

*Mis à jour le 27/07/2026 — Configuration opérationnelle SO-ARM100*
