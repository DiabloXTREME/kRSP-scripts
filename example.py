import math
import time
import krpc

turn_start_altitude = 250
turn_end_altitude = 45000
target_altitude = 150000

conn = krpc.connect(name='Launch into orbit')
vessel = conn.space_center.active_vessel

# Set up streams for telemetry
ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
stage_2_resources = vessel.resources_in_decouple_stage(stage=2, cumulative=False)
srb_fuel = conn.add_stream(stage_2_resources.amount, 'SolidFuel')

# Pre-launch setup
vessel.control.sas = False
vessel.control.rcs = False
vessel.control.throttle = 1.0
ref_frame = vessel.surface_velocity_reference_frame
conn.drawing.add_direction_from_com((0, 1, 0), ref_frame)
# Countdown...
print('3...')
time.sleep(1)
print('2...')
time.sleep(1)
print('1...')
time.sleep(1)
print('Launch!')
print('(%.1f, %.1f, %.1f)' % vessel.position(vessel.orbit.body.reference_frame))

vessel.control.activate_next_stage()
fuel_amount = conn.get_call(vessel.resources.amount, 'SolidFuel')
expr = conn.krpc.Expression.less_than(
    conn.krpc.Expression.call(fuel_amount),
    conn.krpc.Expression.constant_float(0.1))
event = conn.krpc.add_event(expr)
with event.condition:
    event.wait()
print('Booster separation')
print('(%.1f, %.1f, %.1f)' % vessel.position(vessel.orbit.body.reference_frame))
vessel.control.activate_next_stage()
mean_altitude = conn.get_call(getattr, vessel.flight(), 'mean_altitude')
expr = conn.krpc.Expression.greater_than(
    conn.krpc.Expression.call(mean_altitude),
    conn.krpc.Expression.constant_double(10000))
event = conn.krpc.add_event(expr)
with event.condition:
    event.wait()
print('Gravity turn')
print('(%.1f, %.1f, %.1f)' % vessel.position(vessel.orbit.body.reference_frame))
vessel.auto_pilot.target_pitch_and_heading(6, 90)
apoapsis_altitude = conn.get_call(getattr, vessel.orbit, 'apoapsis_altitude')
expr = conn.krpc.Expression.greater_than(
    conn.krpc.Expression.call(apoapsis_altitude),
    conn.krpc.Expression.constant_double(100000))
event = conn.krpc.add_event(expr)
with event.condition:
    event.wait()

print('Launch stage separation')
print('(%.1f, %.1f, %.1f)' % vessel.position(vessel.orbit.body.reference_frame))
vessel.control.throttle = 0
time.sleep(1)
vessel.control.activate_next_stage()
vessel.auto_pilot.disengage()
srf_altitude = conn.get_call(getattr, vessel.flight(), 'surface_altitude')
expr = conn.krpc.Expression.less_than(
    conn.krpc.Expression.call(srf_altitude),
    conn.krpc.Expression.constant_double(1000))
event = conn.krpc.add_event(expr)
with event.condition:
    event.wait()

vessel.control.activate_next_stage()
while vessel.flight(vessel.orbit.body.reference_frame).vertical_speed < -0.1:
    print('Altitude = %.1f meters' % vessel.flight().surface_altitude)
    time.sleep(1)
print('Landed!')
print('(%.1f, %.1f, %.1f)' % vessel.position(vessel.orbit.body.reference_frame))
vessel.auto_pilot.disengage()

while True:
    pass