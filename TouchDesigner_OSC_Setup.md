# TouchDesigner OSC Setup For PiDog

Use this first working route:

```text
PiDog on Raspberry Pi 5 -> OSC over local network -> TouchDesigner on Mac mini
```

## 1. Find the Mac Mini IP Address

On the Mac mini:

```sh
ipconfig getifaddr en0
```

If you use Ethernet, try:

```sh
ipconfig getifaddr en1
```

Use that IP address as the bridge script `--host`.

## 2. Run the Bridge On The Raspberry Pi

Copy `scripts/pidog_touchdesigner_bridge.py` to the Raspberry Pi.

On the Raspberry Pi:

```sh
python3 pidog_touchdesigner_bridge.py --host YOUR_MAC_IP --port 9000
```

For a no-robot test:

```sh
python3 pidog_touchdesigner_bridge.py --host YOUR_MAC_IP --port 9000 --simulate --count 200
```

## 3. Add TouchDesigner OSC Input

In TouchDesigner on the Mac mini:

1. Add `OSC In CHOP`.
2. Set `Network Port` to `9000`.
3. Turn `Active` on.
4. Add a `Null CHOP` after it and name it `null_pidog_osc`.

You should see channels similar to:

```text
pidog:distance_cm
pidog:presence
pidog:contact
pidog:agitation
pidog:sound_dir
pidog:sound_present
pidog:activity
pidog:stability
pidog:attention
pidog:fragmentation
```

TouchDesigner may name OSC channels with underscores instead of colons depending on version/settings. That is okay; use the channel names that appear in your CHOP viewer.

## 4. Smooth The Incoming Values

After `null_pidog_osc`, add:

```text
Select CHOP -> Lag CHOP -> Null CHOP
```

Suggested names:

```text
select_behaviour
lag_behaviour
null_behaviour
```

Start with `Lag CHOP` settings around:

```text
Lag: 0.35
Overshoot: off
```

If the dog feels too sluggish, lower the lag. If it flickers, raise the lag.

## 5. Connect To The Particle Dog

Use the blended state channels rather than a single raw sensor:

```python
op('/project1/null_behaviour')['pidog:stability']
op('/project1/null_behaviour')['pidog:attention']
op('/project1/null_behaviour')['pidog:fragmentation']
op('/project1/null_behaviour')['pidog:activity']
```

If your channel names use underscores, adjust the expression, for example:

```python
op('/project1/null_behaviour')['pidog_activity']
```

Recommended first mappings:

```text
particle noise amplitude   <- fragmentation
particle noise speed       <- activity
particle displacement      <- fragmentation
point size                 <- attention
color/brightness           <- attention + fragmentation
return-to-body/cohesion    <- stability
```

## 6. Behaviour Interpretation

Presence:

```text
ultrasonic distance sees someone approaching
```

Contact:

```text
touch sensor detects petting or direct interaction
```

Agitation:

```text
IMU detects the physical robot being moved, tilted, or disturbed
```

Sound:

```text
ears detect directional sound and pull the dog into attention
```

The point cloud should make the robot's sensed condition visible:

```text
low activity      -> readable, calm Labrador body
moderate activity -> alert, slightly separated, brighter
high activity     -> fragmented, scattered, unstable
contact           -> can calm or gather the body again
```

## 7. Mac Mini Notes

Keep the first version light:

- Run the camera only if you need it.
- Start TouchDesigner at 30 or 60 FPS, not unlimited.
- Keep particle count moderate while wiring sensors.
- Use the OSC bridge first; add camera/AI later.
