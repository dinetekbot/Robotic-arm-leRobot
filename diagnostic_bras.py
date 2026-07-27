#!/usr/bin/env python3
"""
🔍 Script de Diagnostic - Bras SO-ARM100
==========================================
Ce script teste la connexion avec le bras SANS le bouger.
Il vérifie :
  1. Que le port série est accessible
  2. Que les 6 servos STS3215 répondent
  3. Lit les positions actuelles
  4. Lit la température et la tension

Usage:
  source /home/hope/Documents/Hope/Robotics/venv/bin/activate
  python3 diagnostic_bras.py

⚠️ IMPORTANT : Les servos doivent être alimentés (6-7.4V) pour répondre,
   même si on ne leur envoie aucune commande de mouvement.
"""

import sys
import os
import json

# === CONFIGURATION ===
PORT = "/dev/ttyACM0"
PROTOCOL_VERSION = 0
CALIBRATION_PATH = None

# === ÉTAPE 0 : Vérifier le port USB ===
print("=" * 60)
print("🔍 DIAGNOSTIC DU BRAS ROBOTIQUE SO-ARM100")
print("=" * 60)

print(f"\n📌 Étape 0 : Vérification du port USB...")

import glob
ports = glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*")
if ports:
    print(f"   ✅ Ports détectés : {', '.join(ports)}")
else:
    print("   ❌ Aucun port /dev/ttyACM* ou /dev/ttyUSB* détecté !")
    print("   → Vérifie que le bras est branché en USB")
    print("   → Vérifie que les servos sont alimentés")
    sys.exit(1)

if PORT not in ports:
    print(f"   ⚠️  Le port configuré ({PORT}) n'est pas dans la liste !")
    PORT = ports[0]
    print(f"   → Utilisation de : {PORT}")

if not os.access(PORT, os.R_OK | os.W_OK):
    print(f"   ❌ Pas de permissions sur {PORT}")
    print(f"   → Exécute : sudo chmod 666 {PORT}")
    sys.exit(1)
else:
    print(f"   ✅ Permissions OK sur {PORT}")

# === ÉTAPE 1 : Importer LeRobot ===
print(f"\n📌 Étape 1 : Import de LeRobot...")
try:
    from lerobot.motors.feetech import FeetechMotorsBus
    from lerobot.motors.motors_bus import Motor, MotorNormMode
    print("   ✅ LeRobot importé avec succès")
except ImportError as e:
    print(f"   ❌ Erreur d'import : {e}")
    print("   → As-tu activé le venv ? source venv/bin/activate")
    sys.exit(1)

# === ÉTAPE 2 : Définir les moteurs ===
print(f"\n📌 Étape 2 : Configuration des 6 moteurs...")
motors = {
    "shoulder_pan":  Motor(1, "sts3215", MotorNormMode.DEGREES),
    "shoulder_lift": Motor(2, "sts3215", MotorNormMode.DEGREES),
    "elbow_flex":    Motor(3, "sts3215", MotorNormMode.DEGREES),
    "wrist_flex":    Motor(4, "sts3215", MotorNormMode.DEGREES),
    "wrist_roll":    Motor(5, "sts3215", MotorNormMode.DEGREES),
    "gripper":       Motor(6, "sts3215", MotorNormMode.RANGE_0_100),
}
print("   ✅ 6 moteurs configurés (IDs 1-6)")

# === ÉTAPE 3 : Connexion au bus ===
print(f"\n📌 Étape 3 : Connexion au bus série ({PORT})...")
try:
    motor_bus = FeetechMotorsBus(
        port=PORT,
        motors=motors,
        protocol_version=PROTOCOL_VERSION,
    )
    motor_bus.connect()
    print(f"   ✅ Connecté : {motor_bus.is_connected}")
except Exception as e:
    print(f"   ❌ Erreur de connexion : {e}")
    print("   → Vérifie le câblage USB")
    print("   → Vérifie que les servos sont alimentés (6-7.4V)")
    print("   → Vérifie les IDs des moteurs (doivent être 1-6)")
    sys.exit(1)

# === ÉTAPE 4 : Lire les positions ===
print(f"\n📌 Étape 4 : Lecture des positions actuelles...")
try:
    positions = motor_bus.sync_read("Present_Position")
    print("   ✅ Positions lues avec succès :")
    print("   " + "-" * 45)
    print(f"   {'Moteur':<20} {'Position':>10}")
    print("   " + "-" * 45)
    for name, pos in positions.items():
        print(f"   {name:<20} {pos:>10.1f}")
    print("   " + "-" * 45)
except Exception as e:
    print(f"   ❌ Erreur de lecture : {e}")

# === ÉTAPE 5 : Lire les températures ===
print(f"\n📌 Étape 5 : Lecture des températures...")
try:
    temps = motor_bus.sync_read("Present_Temperature")
    print("   ✅ Températures :")
    for name, temp in temps.items():
        status = "🟢" if temp < 50 else ("🟡" if temp < 65 else "🔴")
        print(f"   {status} {name:<20} {temp}°C")
except Exception as e:
    print(f"   ⚠️  Lecture température échouée : {e}")

# === ÉTAPE 6 : Lire les tensions ===
print(f"\n📌 Étape 6 : Lecture des tensions d'alimentation...")
try:
    volts = motor_bus.sync_read("Present_Voltage")
    print("   ✅ Tensions :")
    for name, volt in volts.items():
        v = volt / 10 if volt > 30 else volt
        status = "🟢" if 6.0 <= v <= 8.0 else "🔴"
        print(f"   {status} {name:<20} {v:.1f}V")
except Exception as e:
    print(f"   ⚠️  Lecture tension échouée : {e}")

# === NETTOYAGE ===
print(f"\n📌 Déconnexion...")
motor_bus.disconnect()
print("   ✅ Bus déconnecté proprement")

print("\n" + "=" * 60)
print("✅ DIAGNOSTIC TERMINÉ — Le bras est opérationnel !")
print("=" * 60)
print("\nProchaine étape : Calibrer le bras avec :")
print(f"  lerobot-calibrate --robot.type=so100_follower --robot.port={PORT} --robot.id=my_arm")
