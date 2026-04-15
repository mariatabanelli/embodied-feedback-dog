# Embodied Feedback Dog

An interactive robotics and real-time visual system using a SunFounder PiDog, Raspberry Pi, OSC, and TouchDesigner. The physical robot acts as a sensing body, while a particle-based Labrador visualises the robot's behavioural condition in real time.

Rather than treating a person as a direct trigger for visual effects, the project frames the physical PiDog and the digital particle dog as one feedback system:

```text
human interaction -> robot sensory/body feedback -> visible behavioural condition
```

## Project Summary

Embodied Feedback Dog explores how a robotic animal can become a physical interface for a digital body. Human interaction perturbs the PiDog: approaching it changes its sense of presence, touching it creates contact and reassurance, and moving or tilting it creates agitation. A Python bridge on the Raspberry Pi reads these sensor states and sends shaped behaviour values over OSC to TouchDesigner, where they drive a point-cloud Labrador.

The result is a live interaction loop where the digital dog shifts between calm, attentive, and fragmented states according to the physical robot's sensed condition.

## Demo

Add a short video or GIF here when documenting the final installation:

```text
VIDEO PLACEHOLDER
PiDog interaction + TouchDesigner particle Labrador reaction
```

Suggested documentation shots:

- Wide shot showing the PiDog and the TouchDesigner output together.
- Screen capture showing OSC channels changing live in TouchDesigner.
- Close-up of touch/proximity/movement interaction with the robot.

## System Diagram

```text
SunFounder PiDog / Raspberry Pi
  ultrasonic distance
  dual touch sensor
  IMU accelerometer + gyroscope
  sound direction sensor, tested but optional
  camera, tested as face-tracking extension
        |
        v
Python behaviour bridge
  sensor reads
  behaviour shaping
  OSC messages
        |
        v
Wi-Fi / local network
        |
        v
TouchDesigner
  OSC In CHOP
  Select CHOP
  Lag CHOP
  Null CHOP
        |
        v
FBX Labrador particle system
  brightness / presence
  turbulence / fragmentation
  drag / contact calming
```

## Interaction Mapping

| Physical Interaction | PiDog Signal | Behaviour Channel | TouchDesigner Response |
| --- | --- | --- | --- |
| A person approaches the dog | Ultrasonic distance | `presence`, `attention` | The particle dog becomes more visible and attentive. |
| The dog is touched or petted | Dual touch sensor | `contact`, `stability` | Particles calm down through reduced turbulence and increased drag. |
| The dog is tilted, lifted, or disturbed | IMU accelerometer/gyroscope | `agitation`, `fragmentation` | The particle body becomes less coherent and more disturbed. |
| Sound direction | PiDog ears | `sound_dir`, `sound_present` | Tested as an optional attention/orientation layer. |
| Camera | PiDog camera | Face tracking extension | Tested as a separate camera stream/head-tracking demo. |

## Materials And Tools

- SunFounder PiDog
- Raspberry Pi, used as the robot-side sensor bridge
- MacBook or Mac mini running TouchDesigner
- TouchDesigner
- Python
- OSC over Wi-Fi
- FBX Labrador model converted into a particle system
- PiDog ultrasonic distance sensor
- PiDog dual touch sensor
- PiDog IMU accelerometer/gyroscope
- PiDog sound direction sensor, tested as optional input
- PiDog camera, tested as a separate face-tracking extension

## Repository Contents

```text
scripts/pidog_touchdesigner_bridge.py
```

Reads PiDog sensor values, shapes them into behaviour channels, and sends OSC messages to TouchDesigner.

```text
scripts/pidog_sensor_check.py
```

Utility script for testing PiDog sensors and camera detection on the Raspberry Pi.

```text
scripts/7_face_track_no_ears.py
```

Camera stream and face-tracking demo adapted from the SunFounder face-tracking example. This version removes sound-direction/ears input to avoid `GPIO busy` conflicts while keeping the camera stream and gentle head tracking.

```text
TouchDesigner_OSC_Setup.md
```

Step-by-step TouchDesigner OSC setup notes.

```text
TouchDesigner_Dog_Behaviour_Interface.md
```

Concept, behaviour mapping, and TouchDesigner network planning notes.

The TouchDesigner `.toe` file and large model/cache assets can be kept out of Git if they are too large or include third-party assets. A portfolio repository can still document the system clearly with the scripts, screenshots, videos, and setup notes.

## OSC Channels

The Python bridge sends the following OSC channels:

```text
/pidog/distance_cm
/pidog/presence
/pidog/contact
/pidog/agitation
/pidog/sound_dir
/pidog/sound_present
/pidog/activity
/pidog/stability
/pidog/attention
/pidog/fragmentation
```

The final TouchDesigner receiver uses:

```text
OSC In CHOP -> Select CHOP -> Lag CHOP -> Null CHOP
```

The final behaviour output node is named:

```text
null_behaviour
```

## Running The Live Bridge

Find the TouchDesigner computer's local IP address:

```sh
ipconfig getifaddr en0
```

Copy the bridge to the Raspberry Pi if needed:

```sh
scp "scripts/pidog_touchdesigner_bridge.py" aidog@mariadog.local:~/pidog_touchdesigner_bridge.py
```

Run the bridge on the Raspberry Pi:

```sh
python3 ~/pidog_touchdesigner_bridge.py --host YOUR_TOUCHDESIGNER_COMPUTER_IP --port 9000
```

Example:

```sh
python3 ~/pidog_touchdesigner_bridge.py --host 192.168.0.110 --port 9000
```

To test without the physical PiDog sensors, run the simulation mode:

```sh
python3 scripts/pidog_touchdesigner_bridge.py --host 127.0.0.1 --port 9000 --simulate --count 200
```

## Camera And Face Tracking

The PiDog camera was repaired and tested successfully. Camera detection on the Raspberry Pi showed an `ov5647` camera module:

```text
0 : ov5647 [2592x1944 10-bit GBRG]
```

The stock SunFounder `7_face_track.py` example started the camera stream, but then hit a `GPIO busy` error because it also uses the ears/sound-direction sensor. To keep the camera test stable, this repository includes a simplified version:

```text
scripts/7_face_track_no_ears.py
```

This version keeps:

- PiDog camera stream
- face detection
- gentle head tracking
- RGB strip feedback

and removes:

- ears/sound-direction reads

Copy it to the PiDog:

```sh
scp "scripts/7_face_track_no_ears.py" aidog@mariadog.local:~/pidog/examples/7_face_track_no_ears.py
```

Run it on the Raspberry Pi:

```sh
sudo python3 ~/pidog/examples/7_face_track_no_ears.py
```

Open the camera stream from a browser on the same network:

```text
http://192.168.0.111:9000/mjpg
```

Use the PiDog's current IP address if it changes:

```sh
hostname -I
```

The camera/face-tracking script is intentionally kept separate from the TouchDesigner sensor bridge so the project can avoid hardware conflicts and keep each demonstration reliable.

## TouchDesigner Mapping

The live channels are mapped to the particle Labrador through parameter expressions. Example mappings used during development:

```python
op('null_behaviour')['pidog/presence'][0]
```

```python
op('null_behaviour')['pidog/fragmentation'][0]
```

```python
op('null_behaviour')['pidog/contact'][0]
```

Conceptually:

- `presence` controls how attentive/readable the particle dog feels.
- `fragmentation` controls disturbance, turbulence, and loss of coherence.
- `contact` acts as reassurance, reducing turbulence and increasing drag.

## Behaviour Shaping

The live PiDog sensors are noisier than simulated values, so the bridge includes a behaviour-shaping layer. This prevents the visual system from reacting to every tiny sensor fluctuation.

The bridge:

- smooths presence values from the ultrasonic sensor
- thresholds IMU movement so fragmentation only rises on meaningful disturbance
- treats touch as a calming signal rather than a fragmentation trigger
- sends blended behaviour values instead of raw sensor data

This design decision makes the installation read as a behavioural system rather than a set of raw sensor effects.

## Development Process

1. Built a first TouchDesigner particle Labrador from an FBX model.
2. Created a simulated OSC bridge to tune the visual behaviour before relying on hardware.
3. Added a TouchDesigner OSC receiver network using `OSC In CHOP`, `Select CHOP`, `Lag CHOP`, and `Null CHOP`.
4. Mapped behaviour channels to brightness, turbulence, drag, and particle movement.
5. Connected the real PiDog over SSH and Wi-Fi.
6. Tested the ultrasonic distance sensor, dual touch sensor, and IMU.
7. Updated the bridge to match the installed PiDog Python API.
8. Added behaviour shaping so live robot data felt smooth and legible in TouchDesigner.
9. Repaired and tested the PiDog camera.
10. Adapted the face-tracking example to remove sound-direction input and avoid a `GPIO busy` conflict.

## Known Limitations

- The camera works as a separate stream/face-tracking extension, but it is not merged into the TouchDesigner live bridge yet.
- The sound direction sensor produced a `GPIO busy` error during some tests, so the main live system focuses on distance, touch, and IMU values.
- The original SunFounder face-tracking example also reads the ears sensor; this repository includes a no-ears variant to avoid that conflict.
- The TouchDesigner `.toe` file is binary and may not be ideal for GitHub review. For public documentation, screenshots, video, and setup notes are more useful.

## Future Development

- Send camera-derived values such as `face_present`, `face_x`, and `motion_amount` over OSC.
- Add bidirectional feedback so TouchDesigner can trigger PiDog LEDs, sounds, or small body actions.
- Package the TouchDesigner OSC network as a reusable `.tox` component.
- Add a small on-screen debug panel for live exhibitions.

## Skills Demonstrated

- Real-time interaction design
- Robotics prototyping
- Sensor integration
- Python scripting
- OSC networking
- TouchDesigner CHOP/TOP workflow
- Hardware/software debugging
- Behaviour mapping and data shaping
- Interactive installation documentation

## Credits

Created by Maria Tabanelli.

Built with SunFounder PiDog, Raspberry Pi, Python, OSC, and TouchDesigner.
