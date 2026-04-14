# TouchDesigner Dog Behaviour Interface

Project intention:

> A behavioural interface in which sensed human activity drives the internal state of a robotic agent, visualised through a point-cloud body that shifts between stability, attention, and fragmentation.

The dog should not behave like a generic audio-reactive particle system. Treat the physical PiDog and the point-cloud Labrador as one feedback system: human interaction perturbs the robot, the robot senses its own condition, and the particle body visualises that behavioural feedback.

- `stability`: the robot is calm, untouched, and physically steady
- `attention`: someone approaches, speaks, or enters the robot's perceptual field
- `fragmentation`: the robot is overloaded, startled, moved, tilted, or intensely stimulated

## Recommended Network Structure

Keep the existing FBX-to-particles dog network intact. Add one new control system beside it:

```text
/project1
  /dog_particles_existing
  /sensor_input
  /activity_analysis
  /state_machine
  /particle_state_driver
  /ui_debug
```

If your current particle system is already inside `/project1`, do not move everything at first. Add these networks as Base COMPs next to it, then connect channels into the existing parameters.

## PiDog Feedback Layer

Use the Raspberry Pi 5 as the sensor bridge. The PiDog reads its own sensors and sends TouchDesigner behaviour channels over OSC:

```text
PiDog sensors -> Python OSC bridge -> TouchDesigner OSC In CHOP
```

First sensor set:

- ultrasonic distance: approach and withdrawal
- dual touch: direct contact, petting, reassurance
- IMU: movement, tilt, shaking, physical disturbance
- sound direction: attention and orientation
- camera: optional version 2, after the OSC loop is stable

The bridge script in this folder is:

```text
scripts/pidog_touchdesigner_bridge.py
```

Use `TouchDesigner_OSC_Setup.md` for the exact TouchDesigner OSC setup.

## Optional Camera Layer

For a webcam-based or Pi camera version, build this only after the core PiDog OSC loop is working:

```text
videoDeviceIn1
  -> level1              # optional contrast/gain
  -> cache1              # cache previous frame
  -> difference1         # current frame minus previous frame
  -> mono1
  -> blur1               # reduce sensor noise
  -> analyze1            # average brightness / motion amount
  -> null_motion_raw
```

Then convert the motion signal to CHOP if needed:

```text
null_motion_raw TOP -> TOP to CHOP -> math_activity -> filter_activity -> lag_activity -> null_activity
```

Suggested CHOP settings:

- `Math CHOP`: normalize raw activity to `0-1`
- `Filter CHOP`: smooth fast flicker, start around `0.15`
- `Lag CHOP`: separate rise/fall if you want a more animal-like response
- `Limit CHOP`: clamp to `0-1`

Rename the final channel to:

```text
activity
```

## Activity Analysis For OSC Input

The Raspberry Pi bridge sends these OSC channels:

```text
distance_cm
presence
contact
agitation
sound_dir
sound_present
activity
stability
attention
fragmentation
```

Keep this conceptual route:

```text
raw robot sensor -> normalize -> behaviour channel -> particle body
```

## State Machine

The Python bridge already sends blended state channels, so the first TouchDesigner version does not need a complicated state machine. Use this CHOP chain:

```text
OSC In CHOP -> Select CHOP -> Lag CHOP -> Null CHOP
```

Final behaviour channels:

```text
stability       0 to 1
attention       0 to 1
fragmentation   0 to 1
activity        0 to 1
```

If the state flickers, increase `Lag CHOP` slightly before editing the Python thresholds.

## Particle State Driver

Create `/particle_state_driver` with channels that describe behaviour, not sensor input:

```text
cohesion
displacement
noise_amp
noise_speed
point_size
color_heat
reset_force
```

Suggested mappings:

| Behaviour | Stability | Attention | Fragmentation |
| --- | --- | --- | --- |
| cohesion | 1.00 | 0.75 | 0.25 |
| displacement | 0.02 | 0.16 | 0.75 |
| noise_amp | 0.01 | 0.12 | 0.65 |
| noise_speed | 0.05 | 0.35 | 1.20 |
| point_size | 2.0 | 2.8 | 1.4 |
| color_heat | 0.15 | 0.55 | 1.00 |

This is the main conceptual move:

```text
human interaction changes the robot's sensed condition
the robot's sensed condition drives the point-cloud body
```

Not:

```text
one raw sensor directly shakes random particles
```

## Expressions To Use On Particle Parameters

If the final driver channels are in:

```text
/project1/particle_state_driver/null_driver
```

you can reference them from parameters like this:

```python
op('/project1/particle_state_driver/null_driver')['noise_amp']
```

Examples:

```python
op('/project1/particle_state_driver/null_driver')['displacement']
```

```python
op('/project1/particle_state_driver/null_driver')['point_size']
```

```python
op('/project1/particle_state_driver/null_driver')['noise_speed']
```

Use these expressions on existing parameters such as:

- particle turbulence amplitude
- noise amount
- force strength
- point size
- feedback opacity
- geometry displacement
- color ramp lookup
- instancing scale

The exact parameter names depend on how your FBX particle network is built.

## Visual Language

Stability:

- Dog point cloud is coherent and readable.
- Points stay close to the Labrador body.
- Slow breathing or subtle idle motion.
- Cooler, calm color.
- Low noise.

Attention:

- Dog still remains readable.
- Head/torso or outline seems more alert.
- Points separate slightly from the surface.
- A brighter edge or pulse can appear.
- Moderate noise and faster motion.

Fragmentation:

- Dog body begins to break apart.
- Points scatter, jitter, or trail.
- Shape is still partially recoverable, not pure random soup.
- Hotter color or sharper contrast.
- After intensity drops, the body reassembles slowly.

## Debug UI

Add a small debug panel so you can trust the system:

```text
activity: 0.00-1.00
state: stability / attention / fragmentation
sensor connected: yes / no
fps
```

Keep the debug UI visible while building. Hide it only for final presentation.

## Fallback Test Mode

Make a manual fallback using `Constant CHOP` or `Mouse In CHOP`:

```text
manual_activity
```

Use a `Switch CHOP`:

```text
sensor_activity
manual_activity
  -> switch_activity_source
```

This lets the project work even when the sensor is not connected.

## Build Order

1. Open `FBXToParticles.DOG.toe` in TouchDesigner.
2. Save a copy before editing, for example `FBXToParticles.DOG.behaviour_v01.toe`.
3. Add a manual `Constant CHOP` called `activity` and test the three states first.
4. Connect state driver channels to visible particle parameters.
5. Tune stability, attention, and fragmentation visually.
6. Add the real sensor input.
7. Normalize and smooth the sensor signal.
8. Replace manual activity with sensor activity using a `Switch CHOP`.
9. Add a debug UI.
10. Save a final copy.

## First Reliable Version

For the first version, only drive 3-5 parameters:

- noise amplitude
- noise speed
- point size
- color/brightness
- displacement or force strength

Once that works, add more nuance like different behaviour for head/body/tail regions.
