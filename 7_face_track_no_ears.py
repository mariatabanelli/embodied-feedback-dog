#!/usr/bin/env python3
"""Camera + face tracking demo for PiDog without sound-direction/ears input.

The stock SunFounder face-tracking example also reads the ears/sound-direction
sensor. On this build that can raise a GPIO busy error, so this version keeps
camera streaming, face detection, RGB feedback, and gentle head tracking while
leaving the ears sensor alone.
"""

from time import sleep

from pidog import Pidog
from vilib import Vilib


STREAM_URL = "http://192.168.0.111:9000/mjpg"


my_dog = Pidog()
sleep(0.1)


def face_track_no_ears() -> None:
    Vilib.camera_start(vflip=False, hflip=False)
    Vilib.display(local=False, web=True)
    Vilib.face_detect_switch(True)
    sleep(0.2)

    print("Camera stream:")
    print(STREAM_URL)
    print("Face tracking without ears/sound direction. Press Ctrl+C to stop.")

    yaw = 0
    pitch = 0

    my_dog.do_action("sit", speed=50)
    my_dog.head_move([[yaw, 0, pitch]], pitch_comp=-40, immediately=True, speed=80)
    my_dog.wait_all_done()
    sleep(0.5)

    while True:
        people = Vilib.detect_obj_parameter["human_n"]
        ex = Vilib.detect_obj_parameter["human_x"] - 320
        ey = Vilib.detect_obj_parameter["human_y"] - 240

        if people > 0:
            my_dog.rgb_strip.set_mode("breath", "pink", bps=1)

            if ex > 15 and yaw > -80:
                yaw -= 0.5 * int(ex / 30.0 + 0.5)
            elif ex < -15 and yaw < 80:
                yaw += 0.5 * int(-ex / 30.0 + 0.5)

            if ey > 25:
                pitch -= int(ey / 50.0 + 0.5)
                if pitch < -30:
                    pitch = -30
            elif ey < -25:
                pitch += int(-ey / 50.0 + 0.5)
                if pitch > 30:
                    pitch = 30

            my_dog.head_move([[yaw, 0, pitch]], pitch_comp=-40, immediately=True, speed=80)
        else:
            my_dog.rgb_strip.set_mode("breath", "white", bps=0.5)

        print(
            f"people={people} ex={ex} ey={ey} yaw={round(yaw, 2)} pitch={round(pitch, 2)}",
            end="\r",
            flush=True,
        )
        sleep(0.08)


if __name__ == "__main__":
    try:
        face_track_no_ears()
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print(f"\033[31mERROR: {exc}\033[m")
    finally:
        Vilib.camera_close()
        my_dog.close()
        print("\nQuit")
