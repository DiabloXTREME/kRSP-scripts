import math
import time
import krpc

#
# velocity(reference_frame)¶
# The velocity of the center of mass of the vessel, in the given reference frame.
#
# Parameters
# :
# reference_frame (ReferenceFrame) – The reference frame that the returned velocity vector is in.
#
# Returns
# :
# The velocity as a vector. The vector points in the direction of travel, and its magnitude is the speed of the body in meters per second.
#
# Return type
# :
# tuple(float, float, float)
#
# Game Scenes
# :
# Flight
#
# rotation(reference_frame)¶
# The rotation of the vessel, in the given reference frame.
#
# Parameters
# :
# reference_frame (ReferenceFrame) – The reference frame that the returned rotation is in.
#
# Returns
# :
# The rotation as a quaternion of the form
# .
#
# Return type
# :
# tuple(float, float, float, float)
#
# Game Scenes
# :
# Flight
#
# direction(reference_frame)¶
# The direction in which the vessel is pointing, in the given reference frame.
#
# Parameters
# :
# reference_frame (ReferenceFrame) – The reference frame that the returned direction is in.
#
# Returns
# :
# The direction as a unit vector.
#
# Return type
# :
# tuple(float, float, float)
#
# Game Scenes
# :
# Flight
#
# angular_velocity(reference_frame)¶
# The angular velocity of the vessel, in the given reference frame.
#
# Parameters
# :
# reference_frame (ReferenceFrame) – The reference frame the returned angular velocity is in.
#
# Returns
# :
# The angular velocity as a vector. The magnitude of the vector is the rotational speed of the vessel, in radians per second. The direction of the vector indicates the axis of rotation, using the right-hand rule.
#
# Return type
# :
# tuple(float, float, float)
#
# Game Scenes
# :
# Flight
#
#


conn = krpc.connect(name='SSTSO')
vessel = conn.space_center.active_vessel

alt = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
fuel_amount = conn.get_call(vessel.resources.amount, 'LiquidFuel')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
flight = vessel.flight(vessel.orbit.body.reference_frame)

vessel.control.sas = False
vessel.control.rcs = False
vessel.control.throttle = 1.0

vessel.control.activate_next_stage()

vessel.auto_pilot.engage()
vessel.auto_pilot.reference_frame= vessel.surface_velocity_reference_frame
# vessel.auto_pilot.target_pitch_and_heading(10,0)

# Set target pitch angle (e.g., 10 degrees upward)
while True:
    conn.drawing.add_direction_from_com((0, 1, 0), vessel.surface_velocity_reference_frame)
    vessel.auto_pilot.target_pitch = 2
    vessel.auto_pilot.target_roll = 0
    vessel.auto_pilot.roll_threshold = 1
    vessel.auto_pilot.pitch_threshold = 1
    print(flight.speed)
    # print(flight.velocity)
    # for control_surface in vessel.parts.control_surfaces:
    #     control_surface.inverted = True
    if flight.velocity[0] > 300.0:
        print("Running")
        vessel.auto_pilot.target_pitch = 2.1
    if flight.speed > 600.0:
        vessel.auto_pilot.target_pitch = 2.2
    if flight.speed > 900.0:
        vessel.auto_pilot.target_pitch = 2.3
    if flight.speed > 1200.0:
        vessel.auto_pilot.target_pitch = 2.4
    if flight.surface_altitude > 50.0:
        vessel.control.gear = False
    # if not flight.speed>  100.0:
    #     vessel.auto_pilot.target_pitch = 45
    #     vessel.auto_pilot.target_pitch_and_heading(45,0)
