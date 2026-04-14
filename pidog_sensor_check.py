#!/usr/bin/env python3
"""Quick PiDog hardware check for sensors and camera on the Raspberry Pi."""

from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import time


def magnitude(values: object) -> float | None:
    if not isinstance(values, (list, tuple)) or len(values) < 3:
        return None
    try:
        x, y, z = (float(values[0]), float(values[1]), float(values[2]))
    except (TypeError, ValueError):
        return None
    return math.sqrt(x * x + y * y + z * z)


def read_sensor(name: str, reader) -> str:
    try:
        value = reader()
    except Exception as exc:
        return f"{name}=ERROR({type(exc).__name__}: {exc})"
    return f"{name}={value}"


def check_camera(timeout: int) -> None:
    command = None
    for candidate in ("rpicam-hello", "libcamera-hello"):
        if shutil.which(candidate):
            command = candidate
            break

    if command is None:
        print("camera=SKIPPED(no rpicam-hello or libcamera-hello command found)")
        print("Try installing/checking Raspberry Pi camera tools on the Pi OS image.")
        return

    print(f"camera_command={command}")

    list_result = subprocess.run(
        [command, "--list-cameras"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print("camera_list:")
    print(list_result.stdout.strip() or "(no output)")

    still_result = subprocess.run(
        [command, "--timeout", str(timeout * 1000), "--nopreview"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print("camera_short_run:")
    print(still_result.stdout.strip() or "(no output)")
    print(f"camera_exit_code={still_result.returncode}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=20, help="Number of sensor samples.")
    parser.add_argument("--rate", type=float, default=2.0, help="Samples per second.")
    parser.add_argument("--camera", action="store_true", help="Also test the Raspberry Pi camera.")
    parser.add_argument("--camera-timeout", type=int, default=3, help="Camera preview test seconds.")
    args = parser.parse_args()

    print("Importing PiDog library...")
    from pidog import Pidog  # type: ignore

    print("Creating PiDog object...")
    dog = Pidog()
    delay = 1.0 / max(args.rate, 0.1)

    print("Reading sensors. Try moving your hand in front, touching the head, making sound, and gently tilting the dog.")
    for index in range(args.count):
        distance = read_sensor("distance_cm", lambda: dog.ultrasonic.read_distance())
        touch = read_sensor("touch", lambda: dog.dual_touch.read())
        sound_dir = read_sensor("sound_dir", lambda: dog.ears.read())
        acc = getattr(dog, "accData", None)
        gyro = getattr(dog, "gyroData", None)
        acc_mag = magnitude(acc)
        gyro_mag = magnitude(gyro)

        print(
            f"{index + 1:03d} "
            f"{distance} | {touch} | {sound_dir} | "
            f"acc={acc} acc_mag={acc_mag} | gyro={gyro} gyro_mag={gyro_mag}",
            flush=True,
        )
        time.sleep(delay)

    if args.camera:
        print()
        check_camera(args.camera_timeout)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
