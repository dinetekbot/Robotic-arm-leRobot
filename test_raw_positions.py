#!/usr/bin/env python3
"""
🧪 Test des positions BRUTES (Raw) & Tension en direct
======================================================
Ce script lit les valeurs brutes des servos sans nécessiter de calibration.
Tu peux bouger les bras à la main pour vérifier que les positions changent bien !

Usage:
  source /home/hope/Documents/Hope/Robotics/venv/bin/activate
  python3 test_raw_positions.py
"""

import time
import sys
import os

PORT = "/dev/ttyACM0"

print("=" * 60)
print("🧪 TEST POSITIONS BRUTES & ALIMENTATION 6V 4A")
print("=" * 60)

try:
    from lerobot.motors.feetech import FeetechMotorsBus
    from lerobot.motors.motors_bus import Motor, MotorNormMode, MotorCalibration
except ImportError:
    print("❌ Active d'abord l'environnement : source venv/bin/activate")
    sys.exit(1)

# Definition standard des 6 moteurs
motors = {
    "shoulder_pan":  Motor(1, "sts3215", MotorNormMode.DEGREES),
    "shoulder_lift": Motor(2, "sts3215", MotorNormMode.DEGREES),
    "elbow_flex":    Motor(3, "sts3215", MotorNormMode.DEGREES),
    "wrist_flex":    Motor(4, "sts3215", MotorNormMode.DEGREES),
    "wrist_roll":    Motor(5, "sts3215", MotorNormMode.DEGREES),
    "gripper":       Motor(6, "sts3215", MotorNormMode.RANGE_0_100),
}

# Calibration par défaut fictive (0 à 4095) pour permettre à sync_read de lire sans erreur
dummy_calibration = {
    name: MotorCalibration(
        id=m.id,
        drive_mode=0,
        homing_offset=0,
        range_min=0,
        range_max=4095
    )
    for name, m in motors.items()
}

motor_bus = FeetechMotorsBus(
    port=PORT,
    motors=motors,
    protocol_version=0,
    calibration=dummy_calibration,
)

try:
    motor_bus.connect()
    print("✅ Connecté au bus série !")
    
    # 1. Vérifier la tension
    volts = motor_bus.sync_read("Present_Voltage")
    print("\n⚡ Mesure des tensions :")
    for name, v_raw in volts.items():
        v = v_raw / 10.0 if v_raw > 30 else v_raw
        print(f"   - {name:<15}: {v:.1f}V")
        
    print("\n---------------------------------------------------------")
    print("🔄 LECTURE DES POSITIONS EN DIRECT (Bouge le bras à la main !)")
    print("Appuie sur CTRL+C pour arrêter.")
    print("---------------------------------------------------------\n")
    
    for i in range(30): # Lit pendant ~15 secondes (30 * 0.5s)
        positions = motor_bus.sync_read("Present_Position")
        pos_str = " | ".join([f"{k[:4]}:{v:6.1f}" for k, v in positions.items()])
        print(f"\r[{i+1:02d}/30] {pos_str}", end="", flush=True)
        time.sleep(0.5)
    print("\n")

except KeyboardInterrupt:
    print("\n⏹️ Arrêt par l'utilisateur.")
except Exception as e:
    print(f"\n❌ Erreur : {e}")
finally:
    motor_bus.disconnect()
    print("✅ Déconnecté proprement.")
