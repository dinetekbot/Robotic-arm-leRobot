import socket
import json
import time
from lerobot.motors.feetech import FeetechMotorsBus
from lerobot.motors.motors_bus import Motor
from lerobot.motors.motors_bus import MotorCalibration
from lerobot.motors.motors_bus import MotorNormMode

HOST = "0.0.0.0"
PORT = 5003

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)


motors={
    "shoulder_pan": Motor(1, "sts3215", MotorNormMode.DEGREES),
    "shoulder_lift": Motor(2, "sts3215", MotorNormMode.DEGREES),
    "elbow_flex": Motor(3, "sts3215", MotorNormMode.DEGREES),
    "wrist_flex": Motor(4, "sts3215", MotorNormMode.DEGREES),
    "wrist_roll": Motor(5, "sts3215", MotorNormMode.DEGREES),
    "gripper": Motor(6, "sts3215", MotorNormMode.RANGE_0_100),
}

motor_names = list(motors.keys())

# Create motor bus
port = "/dev/ttyACM0"  # Linux
# port = "COM3"  # Windows
# port = "/dev/cu.usbserial-*"  # macOS

calibration_path = "/home/brouhane/.cache/huggingface/lerobot/calibration/teleoperators/so_leader/my_follower.json"

with open(calibration_path, "r") as f:
    calib_data = json.load(f)

calibration = {}

for name, data in calib_data.items():
    calibration[name] = MotorCalibration(
        id=data["id"],
        drive_mode=data["drive_mode"],
        homing_offset=data["homing_offset"],
        range_min=data["range_min"],
        range_max=data["range_max"],
    )

motor_bus = FeetechMotorsBus(
    port=port,
    motors=motors,
    protocol_version=0,  # Use 0 or 1 depending on your motors
    calibration=calibration,
)

# Connect and verify motors are present
motor_bus.connect()
print(f"Connected: {motor_bus.is_connected}")

if motor_bus.is_calibrated:
    print("✓ Motors are properly calibrated")
else:
    print("✗ Calibration verification failed")

# Configure motors with optimal settings
motor_bus.configure_motors(
    return_delay_time=0,      # Minimize response delay (2µs)
    maximum_acceleration=254,  # Maximum acceleration
    acceleration=254          # Current acceleration
)

print("Waiting for connection...")
conn, addr = server.accept()
print(f"Connected from {addr}")

buffer = ""


buffer = ""

try:
    while True:
        data = conn.recv(1024)

        if not data:
            print("Client disconnected")
            break

        buffer += data.decode()

        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)

            try:
                positions = json.loads(line)

                # DEBUG (optionnel)
                # print("Received:", positions)

                motor_bus.sync_write("Goal_Position", positions)

            except json.JSONDecodeError:
                print("JSON error, message ignoré")
            
            except Exception as e:
                print("Erreur moteur:", e)

except Exception as e:
    print("Erreur générale:", e)

finally:
    conn.close()
    server.close()
    motor_bus.disconnect()