#!/usr/bin/env python3
"""
Read SunFounder PiDog sensors on the Raspberry Pi and send behaviour channels
to TouchDesigner over OSC.

First reliable version:
  python3 pidog_touchdesigner_bridge.py --host YOUR_MAC_IP

Test without the robot:
  python3 pidog_touchdesigner_bridge.py --host 127.0.0.1 --simulate --count 20
"""

from __future__ import annotations

import argparse
import math
import random
import socket
import struct
import time
from dataclasses import dataclass


def _pad_osc(data: bytes) -> bytes:
    pad = (4 - (len(data) % 4)) % 4
    return data + (b"\x00" * pad)


def _osc_string(value: str) -> bytes:
    return _pad_osc(value.encode("utf-8") + b"\x00")


def osc_message(address: str, *values: float) -> bytes:
    tags = "," + ("f" * len(values))
    packet = _osc_string(address) + _osc_string(tags)
    for value in values:
        packet += struct.pack(">f", float(value))
    return packet


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def lerp(previous: float, current: float, amount: float) -> float:
    return previous + (current - previous) * amount


@dataclass
class BehaviourSample:
    distance_cm: float = 400.0
    presence: float = 0.0
    contact: float = 0.0
    agitation: float = 0.0
    sound_dir: float = 0.0
    sound_present: float = 0.0
    activity: float = 0.0
    stability: float = 1.0
    attention: float = 0.0
    fragmentation: float = 0.0


@dataclass
class BehaviourState:
    presence: float = 0.0
    contact: float = 0.0
    agitation: float = 0.0
    activity: float = 0.0
    stability: float = 1.0
    attention: float = 0.0
    fragmentation: float = 0.0


class PiDogReader:
    def __init__(self) -> None:
        from pidog import Pidog

        self.dog = Pidog()
        self.previous_acc = None
        self.previous_gyro = None

    def read(self) -> BehaviourSample:
        sample = BehaviourSample()

        try:
            distance = self._read_distance()
            sample.distance_cm = distance
            # 30 cm or closer is strong presence; 180 cm or farther fades out.
            sample.presence = clamp((180.0 - distance) / 150.0)
        except Exception:
            pass

        try:
            touch = self.dog.dual_touch.read()
            sample.contact = 0.0 if touch in (None, "N") else 1.0
        except Exception:
            pass

        try:
            direction = self.dog.ears.read()
            if direction is not None and 0 <= float(direction) <= 359:
                sample.sound_dir = float(direction) / 359.0
                sample.sound_present = 1.0
        except Exception:
            pass

        try:
            acc = tuple(float(v) for v in self.dog.accData)
            gyro = tuple(float(v) for v in self.dog.gyroData)
            if self.previous_acc is not None and self.previous_gyro is not None:
                acc_delta = math.sqrt(sum((a - b) ** 2 for a, b in zip(acc, self.previous_acc)))
                gyro_delta = math.sqrt(sum((a - b) ** 2 for a, b in zip(gyro, self.previous_gyro)))
                raw_motion = (acc_delta * 0.00055) + (gyro_delta * 0.03)
                sample.agitation = clamp((raw_motion - 0.08) / 0.55)
            self.previous_acc = acc
            self.previous_gyro = gyro
        except Exception:
            pass

        return sample

    def _read_distance(self) -> float:
        if hasattr(self.dog, "read_distance"):
            return float(self.dog.read_distance())
        if hasattr(self.dog, "distance"):
            return float(self.dog.distance)
        return float(self.dog.ultrasonic.read_distance())


class SimulatedReader:
    def __init__(self) -> None:
        self.t0 = time.monotonic()

    def read(self) -> BehaviourSample:
        t = time.monotonic() - self.t0
        sample = BehaviourSample()
        sample.distance_cm = 110.0 + 80.0 * math.sin(t * 0.45)
        sample.presence = clamp((180.0 - sample.distance_cm) / 150.0)
        sample.contact = 1.0 if int(t) % 11 in (6, 7) else 0.0
        sample.agitation = clamp(max(0.0, math.sin(t * 1.7) - 0.45) * 1.8)
        sample.sound_dir = (math.sin(t * 0.3) + 1.0) * 0.5
        sample.sound_present = 1.0 if int(t) % 9 in (2, 3, 4) else 0.0
        sample.presence = clamp(sample.presence + random.uniform(-0.03, 0.03))
        return sample


def derive_behaviour(sample: BehaviourSample, state: BehaviourState) -> BehaviourSample:
    if sample.distance_cm <= 0:
        target_presence = state.presence
    else:
        target_presence = sample.presence

    target_contact = sample.contact
    target_agitation = sample.agitation

    sample.presence = lerp(state.presence, target_presence, 0.12)
    sample.contact = lerp(state.contact, target_contact, 0.35 if target_contact > state.contact else 0.12)
    sample.agitation = lerp(state.agitation, target_agitation, 0.3 if target_agitation > state.agitation else 0.08)

    raw_activity = max(
        sample.presence * 0.75,
        sample.contact * 0.22,
        sample.agitation,
        sample.sound_present * 0.18,
    )
    sample.activity = lerp(state.activity, clamp(raw_activity), 0.12)

    target_attention = clamp((sample.presence * 0.85) + (sample.sound_present * 0.15))
    target_fragmentation = clamp((sample.agitation - 0.28) / 0.72)
    target_stability = clamp(1.0 - (target_fragmentation * 0.95) + (sample.contact * 0.25))

    # Shaped values for performance: smooth presence, threshold real movement,
    # and let touch calm rather than accidentally fragment the dog.
    sample.attention = lerp(state.attention, target_attention, 0.12)
    sample.fragmentation = lerp(
        state.fragmentation,
        target_fragmentation,
        0.22 if target_fragmentation > state.fragmentation else 0.06,
    )
    sample.stability = lerp(state.stability, target_stability, 0.14)
    return sample


def send_sample(sock: socket.socket, target: tuple[str, int], sample: BehaviourSample) -> None:
    channels = {
        "/pidog/distance_cm": sample.distance_cm,
        "/pidog/presence": sample.presence,
        "/pidog/contact": sample.contact,
        "/pidog/agitation": sample.agitation,
        "/pidog/sound_dir": sample.sound_dir,
        "/pidog/sound_present": sample.sound_present,
        "/pidog/activity": sample.activity,
        "/pidog/stability": sample.stability,
        "/pidog/attention": sample.attention,
        "/pidog/fragmentation": sample.fragmentation,
    }
    for address, value in channels.items():
        sock.sendto(osc_message(address, value), target)


def main() -> int:
    parser = argparse.ArgumentParser(description="Send PiDog behaviour channels to TouchDesigner over OSC.")
    parser.add_argument("--host", required=True, help="Mac mini IP address running TouchDesigner.")
    parser.add_argument("--port", type=int, default=9000, help="TouchDesigner OSC In CHOP port.")
    parser.add_argument("--rate", type=float, default=20.0, help="Samples per second.")
    parser.add_argument("--count", type=int, default=0, help="Stop after this many samples. 0 means run forever.")
    parser.add_argument("--simulate", action="store_true", help="Generate fake sensor data without PiDog hardware.")
    args = parser.parse_args()

    if args.simulate:
        reader = SimulatedReader()
    else:
        reader = PiDogReader()

    target = (args.host, args.port)
    delay = 1.0 / max(args.rate, 1.0)
    state = BehaviourState()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Sending PiDog behaviour OSC to {args.host}:{args.port}")

    try:
        sent = 0
        while True:
            sample = reader.read()
            sample = derive_behaviour(sample, state)
            state.presence = sample.presence
            state.contact = sample.contact
            state.agitation = sample.agitation
            state.activity = sample.activity
            state.stability = sample.stability
            state.attention = sample.attention
            state.fragmentation = sample.fragmentation
            send_sample(sock, target, sample)
            sent += 1
            print(
                "activity={:.2f} stability={:.2f} attention={:.2f} fragmentation={:.2f} "
                "distance={:.1f} contact={:.0f} agitation={:.2f}".format(
                    sample.activity,
                    sample.stability,
                    sample.attention,
                    sample.fragmentation,
                    sample.distance_cm,
                    sample.contact,
                    sample.agitation,
                ),
                end="\r",
                flush=True,
            )
            if args.count and sent >= args.count:
                print("\nDone.")
                return 0
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
