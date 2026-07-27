#!/usr/bin/env python3
"""
🔍 Diagnostic Complet du Bras SO-ARM100 avec Calibration Officielle
====================================================================
Ce script lit la vraie calibration générée et affiche les positions en ° / %
sans bouger le bras.

Usage:
  source /home/hope/Documents/Hope/Robotics/venv/bin/activate
  python3 test_calibrated_positions.py
"""

import os
import sys
import json

PORT = "/dev/ttyACM0"
CALIBRATION_PATH = "/home/hope/.cache/huggingface/lerobot/calibration/robots/so_follower/my_arm.json"

print("=" * 65)
print("🦾 TEST AVEC CALIBRATION OFFICIELLE SO-ARM100")
print("=" * 65)

if not os.path.exists(CALIBRATION_PATH):
    print(f"❌ Fichier de calibration introuvable : {CALIBRATION_PATH}")
    sys.exit(1)

try:
    from lerobot.motors.feetech import FeetechMotorsBus
    from lerobot.motors.motors_bus import Motor, MotorNormMode, MotorCalibration
except ImportError:
    print("❌ Active d'abord l'environnement : source venv/bin/activate")
    sys.exit(1)

# Chargement du JSON de calibration
with open(CALIBRATION_PATH, "r") as f:
    calib_json = json.load(f)

calibration = {}
for name, data in calib_json.items():
    calibration[name] = MotorCalibration(
        id=data["id"],
        drive_mode=data["drive_mode"],
        homing_offset=data["homing_offset"],
        range_min=data["range_min"],
        range_max=data["range_max"],
    )

motors = {
    "shoulder_pan":  Motor(1, "sts3215", MotorNormMode.DEGREES),
    "shoulder_lift": Motor(2, "sts3215", MotorNormMode.DEGREES),
    "elbow_flex":    Motor(3, "sts3215", MotorNormMode.DEGREES),
    "wrist_flex":    Motor(4, "sts3215", MotorNormMode.DEGREES),
    "wrist_roll":    Motor(5, "sts3215", MotorNormMode.DEGREES),
    "gripper":       Motor(6, "sts3215", MotorNormMode.RANGE_0_100),
}

motor_bus = FeetechMotorsBus(
    port=PORT,
    motors=motors,
    protocol_version=0,
    calibration=calibration,
)

try:
    motor_bus.connect()
    print(f"✅ Connecté sur {PORT} avec la calibration enregistrée !")
    print(f"✅ Status calibré : {motor_bus.is_calibrated}\n")
    
    positions = motor_bus.sync_read("Present_Position")
    print("---------------------------------------------------------")
    print(f"{'Articulation':<20} | {'Position Réelle':>15}")
    print("---------------------------------------------------------")
    for name, pos in positions.items():
        unit = "%" if name == "gripper" else "°"
        print(f"{name:<20} | {pos:>14.1f} {unit}")
    print("---------------------------------------------------------")

except Exception as e:
    print(f"❌ Erreur : {e}")
finally:
    motor_bus.disconnect()
    print("\n✅ Déconnecté proprement.")
