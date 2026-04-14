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
  camera, tested as future extension
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
| Camera | PiDog camera | Future extension | Not used in the main live loop; intended for later face/gaze/gesture experiments. |

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
- PiDog camera, tested separately as future extension

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
9. Tested the camera separately; the camera was not detected on the current hardware setup and was left as a future extension.

## Known Limitations

- The PiDog camera was tested but not used in the final live loop because the Raspberry Pi did not detect a camera module during development.
- The sound direction sensor produced a `GPIO busy` error during some tests, so the main live system focuses on distance, touch, and IMU values.
- The TouchDesigner `.toe` file is binary and may not be ideal for GitHub review. For public documentation, screenshots, video, and setup notes are more useful.

## Future Development

- Repair or reconnect the camera ribbon cable and add face/gaze detection.
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
