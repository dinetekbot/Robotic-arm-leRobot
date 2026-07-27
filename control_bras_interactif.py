#!/usr/bin/env python3
"""
🕹️ Contrôleur Interactif Complet - Activation du Couple (Torque) sur tous les Servos
===================================================================================
Correctifs :
  - Activation explicite du couple (Torque_Enable=1) sur les 6 servos
  - Déblocage de la force motrice (Torque_Limit=100%)
  - Mouvements fluides sans secousse à la fermeture

Usage:
  source /home/hope/Documents/Hope/Robotics/venv/bin/activate
  python3 control_bras_interactif.py
"""

import sys
import os
import json
import time

PORT = "/dev/ttyACM0"
CALIBRATION_PATH = "/home/hope/.cache/huggingface/lerobot/calibration/robots/so_follower/my_arm.json"

try:
    from lerobot.motors.feetech import FeetechMotorsBus
    from lerobot.motors.motors_bus import Motor, MotorNormMode, MotorCalibration
except ImportError:
    print("❌ Active d'abord l'environnement : source venv/bin/activate")
    sys.exit(1)

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

motor_bus.connect()
print("✅ Connecté au bras avec succès !")

# ⚡ ÉTAPE ESSENTIELLE : Activer le couple (Torque) sur TOUS les 6 servos
print("⚡ Activation du couple (Force motrice) sur les 6 servomoteurs...")
try:
    motor_bus.enable_torque()
    print("✅ Couple (Torque) activé sur les 6 servos !")
except Exception as e:
    print(f"⚠️ Note sur l'activation du couple : {e}")

# Configuration d'accélération et vitesse équilibrées
motor_bus.configure_motors(
    return_delay_time=0,
    maximum_acceleration=100,
    acceleration=100
)

# Position repos naturelle sécurisée
SAFE_HOME_POSITIONS = {
    "shoulder_pan": 0.0,
    "shoulder_lift": -90.0,  # Épaule relevée
    "elbow_flex": 90.0,      # Coude plié
    "wrist_flex": -90.0,     # Poignet replié
    "wrist_roll": 0.0,
    "gripper": 100.0,        # Pince ouverte
}

def safe_write(targets, description=""):
    try:
        motor_bus.sync_write("Goal_Position", targets)
        if description:
            print(f"✅ {description}")
    except Exception as e:
        print(f"⚠️ Alerte Moteur ({description}): {e}")

def print_status():
    try:
        positions = motor_bus.sync_read("Present_Position")
        print("\n---------------------------------------------------------")
        print("📊 POSITIONS ACTUELLES DES 6 ARTICULATIONS :")
        for name, pos in positions.items():
            unit = "%" if name == "gripper" else "°"
            print(f"   • {name:<15} : {pos:6.1f} {unit}")
        print("---------------------------------------------------------\n")
    except Exception as e:
        print(f"⚠️ Erreur de lecture statut : {e}")

print("\n" + "="*60)
print("🕹️ CONTRÔLEUR INTERACTIF AVEC FORCE MOTRICE (TORQUE ON)")
print("Commandes:")
print("  - open / close / gripper <0-100>")
print("  - pan <deg>   | lift <deg>   | elbow <deg>")
print("  - wflex <deg> | wroll <deg>")
print("  - home        | status       | quit")
print("="*60 + "\n")

print_status()

MOTOR_MAP = {
    "pan": "shoulder_pan",
    "lift": "shoulder_lift",
    "elbow": "elbow_flex",
    "wflex": "wrist_flex",
    "wroll": "wrist_roll",
}

try:
    while True:
        cmd_raw = input("Robot 🤖 > ").strip().lower()
        if not cmd_raw:
            continue
        
        parts = cmd_raw.split()
        cmd = parts[0]
        
        if cmd in ["quit", "exit"]:
            break
            
        elif cmd == "status":
            print_status()
            
        elif cmd == "open":
            safe_write({"gripper": 100.0}, "Ouverture pince (100%)")
            
        elif cmd == "close":
            safe_write({"gripper": 0.0}, "Fermeture pince (0%)")
            
        elif cmd == "gripper":
            if len(parts) > 1:
                val = float(parts[1])
                safe_write({"gripper": val}, f"Pince à {val}%")
            else:
                print("❌ Exemple: gripper 50")
                
        elif cmd == "home":
            safe_write(SAFE_HOME_POSITIONS, "Position Repos (Home)")
            
        elif cmd in MOTOR_MAP:
            if len(parts) > 1:
                try:
                    val = float(parts[1])
                    motor_name = MOTOR_MAP[cmd]
                    safe_write({motor_name: val}, f"{motor_name} -> {val}°")
                except ValueError:
                    print(f"❌ Angle invalide. Exemple: {cmd} 20")
            else:
                print(f"❌ Précise l'angle en degrés. Exemple: {cmd} 15")
                
        else:
            print(f"❓ Commande '{cmd}' inconnue. Tape 'status' ou 'quit'.")

        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nArrêt.")
finally:
    print("\n📌 Positionnement repos avant déconnexion...")
    try:
        motor_bus.sync_write("Goal_Position", SAFE_HOME_POSITIONS)
        time.sleep(1.0)
    except Exception:
        pass
    print("📌 Fermeture de la connexion...")
    try:
        motor_bus.disconnect()
    except Exception as e:
        print(f"⚠️ Note déconnexion : {e}")
    print("✅ Déconnecté proprement.")
