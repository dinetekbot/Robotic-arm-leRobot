#!/usr/bin/env python3
"""
🤖 Séquence Automatique de Pick & Place avec Trajectoires Lisses
================================================================
Ce script exécute une démonstration complète autonome :
  1. Position Repos (Home)
  2. Approche zone A (au-dessus de l'objet)
  3. Descente et Ouverture pince
  4. Saisie (Fermeture pince)
  5. Élévation de l'objet
  6. Rotation vers la zone B (Pan 60°)
  7. Descente et Dépose (Ouverture pince)
  8. Retour à la position Repos (Home)

Chaque déplacement est interpolé pour une fluidité maximale.

Usage:
  source /home/hope/Documents/Hope/Robotics/venv/bin/activate
  python3 sequence_automatique.py
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
print("✅ Connecté au bras SO-ARM100 !")
motor_bus.enable_torque()

motor_bus.configure_motors(
    return_delay_time=0,
    maximum_acceleration=80,
    acceleration=80
)

# --- DÉFINITION DES WAYPOINTS (Positions clés) ---
WAYPOINTS = [
    {
        "name": "1. Position Repos (Home)",
        "pos": {"shoulder_pan": 0.0, "shoulder_lift": -90.0, "elbow_flex": 90.0, "wrist_flex": -90.0, "wrist_roll": 0.0, "gripper": 100.0},
        "pause": 1.0
    },
    {
        "name": "2. Approche Zone A (au-dessus de l'objet)",
        "pos": {"shoulder_pan": 0.0, "shoulder_lift": -45.0, "elbow_flex": 45.0, "wrist_flex": -45.0, "wrist_roll": 0.0, "gripper": 100.0},
        "pause": 0.5
    },
    {
        "name": "3. Descente vers l'objet & Ouverture pince",
        "pos": {"shoulder_pan": 0.0, "shoulder_lift": -20.0, "elbow_flex": 30.0, "wrist_flex": -30.0, "wrist_roll": 0.0, "gripper": 100.0},
        "pause": 0.5
    },
    {
        "name": "4. Saisie de l'objet (Fermeture pince)",
        "pos": {"shoulder_pan": 0.0, "shoulder_lift": -20.0, "elbow_flex": 30.0, "wrist_flex": -30.0, "wrist_roll": 0.0, "gripper": 0.0},
        "pause": 1.0
    },
    {
        "name": "5. Remonter avec l'objet",
        "pos": {"shoulder_pan": 0.0, "shoulder_lift": -60.0, "elbow_flex": 60.0, "wrist_flex": -60.0, "wrist_roll": 0.0, "gripper": 0.0},
        "pause": 0.5
    },
    {
        "name": "6. Pivoter vers Zone B (Pan -> 60°)",
        "pos": {"shoulder_pan": 60.0, "shoulder_lift": -60.0, "elbow_flex": 60.0, "wrist_flex": -60.0, "wrist_roll": 0.0, "gripper": 0.0},
        "pause": 0.5
    },
    {
        "name": "7. Descente Zone B & Libération objet (Ouverture pince)",
        "pos": {"shoulder_pan": 60.0, "shoulder_lift": -20.0, "elbow_flex": 30.0, "wrist_flex": -30.0, "wrist_roll": 0.0, "gripper": 100.0},
        "pause": 1.0
    },
    {
        "name": "8. Retour Position Repos (Home)",
        "pos": {"shoulder_pan": 0.0, "shoulder_lift": -90.0, "elbow_flex": 90.0, "wrist_flex": -90.0, "wrist_roll": 0.0, "gripper": 100.0},
        "pause": 1.0
    }
]

def interpolate_and_move(start_pos, target_pos, steps=20, dt=0.04):
    """Calcule une trajectoire lissée entre la position actuelle et le waypoint cible."""
    for step in range(1, steps + 1):
        alpha = step / steps # De 0.0 à 1.0
        # Interpolation linéaire pour chaque joint
        interp_cmd = {}
        for joint in target_pos:
            start_val = start_pos.get(joint, target_pos[joint])
            end_val = target_pos[joint]
            interp_cmd[joint] = start_val + alpha * (end_val - start_val)
        
        motor_bus.sync_write("Goal_Position", interp_cmd)
        time.sleep(dt)

print("\n" + "="*60)
print("🎬 DÉMARRAGE DE LA SÉQUENCE AUTOMATIQUE PICK & PLACE")
print("="*60 + "\n")

try:
    current_positions = motor_bus.sync_read("Present_Position")
    
    for wp in WAYPOINTS:
        print(f"▶️ Executing: {wp['name']}...")
        interpolate_and_move(current_positions, wp["pos"], steps=25, dt=0.04)
        current_positions = wp["pos"]
        time.sleep(wp["pause"])

    print("\n✅ Séquence Pick & Place terminée avec succès !")

except KeyboardInterrupt:
    print("\nArrêt par l'utilisateur.")
except Exception as e:
    print(f"\n⚠️ Erreur pendant la séquence : {e}")
finally:
    print("📌 Positionnement repos final...")
    try:
        motor_bus.sync_write("Goal_Position", WAYPOINTS[0]["pos"])
        time.sleep(1.0)
        motor_bus.disconnect()
    except Exception:
        pass
    print("✅ Déconnecté proprement.")
