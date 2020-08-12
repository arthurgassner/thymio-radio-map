import dbus
import dbus.mainloop.glib
from gi.repository import GObject as gobject
import math
import time
import copy
import pickle
import os

SPEED = 100
TIMESTEP = 10 # [ms]
WHEEL_RADIUS = 1.91 # [cm]
AXLE_LENGTH = 10.1 # [cm] distance between each wheel  TODO CHANGE THIS TO THE REAL VALUE
SPEED_UNIT_TO_RADS_CONVERTION = 9.53/500 # 500 in motor speed corresponds to 9.53 [rad/s] according to https://cyberbotics.com/doc/guide/thymio2 # TODO is this really correct ?
MOTOR_LEFT_TRESH = 300
MOTOR_RIGHT_TRESH = 300
P_GAIN = 1.0

class Thymio(object):
    def __init__(self, initial_position, distance_to_travel, positions_filename, dest_folderpath):
        """Initialize the Thymio instance with its initial position

        Arguments:
            initial_position {List of 2 floats} -- (x,y) coordinates of the initial position
            distance_to_travel (float): distance [cm] forward the Thymio must travel
            positions_filename (str): filename of the .txt holding the Thymio's past locations where it stopped
            dest_folderpath (str): folderpath where to store {positions_filename}.txt
        """

        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        bus = dbus.SessionBus()

        self.network = dbus.Interface(bus.get_object('ch.epfl.mobots.Aseba', '/'), dbus_interface='ch.epfl.mobots.AsebaNetwork')

        # Schedule controller
        gobject.timeout_add(TIMESTEP, self.followLine)

        # Ensure {dest_folderpath}/ exists
        if not os.path.isdir(dest_folderpath):
            os.mkdir(dest_folderpath)

        # Ensure {dest_folderpath/positions_filename}.txt exists
        self.positions_filepath = os.path.join(dest_folderpath, '{}.txt'.format(positions_filename))
        if not os.path.isfile(self.positions_filepath):
            with open(self.positions_filepath, 'w') as _:
                pass

        self.ground_sensors = [0, 0]
        self.last_stopped_position = copy.copy(initial_position) # position when the Thymio last stopped
        self.current_position = copy.copy(initial_position)
        self.current_heading = 0.0 # start with 0 heading
        self.distance_to_travel = distance_to_travel

    def run(self):
        self.loop = gobject.MainLoop()
        self.loop.run()

    def followLine(self):
        """Follow the line for one TIMESTEP"""

        if self.hasReachedDistance():
            self.saveCurrentPosition(self.positions_filepath)

            self.network.SetVariable("thymio-II", "motor.left.target", [0])
            self.network.SetVariable("thymio-II", "motor.right.target", [0])
            self.loop.quit()
            return

        self.updateGroundSensors()

        motor_left_target = SPEED
        motor_right_target = SPEED
        if self.ground_sensors[0] > MOTOR_LEFT_TRESH:
            delta_speed = abs(self.ground_sensors[0] - 900) * P_GAIN
            delta_speed = min(delta_speed, 100)
            motor_left_target += delta_speed
            motor_right_target -= delta_speed
        elif self.ground_sensors[1] > MOTOR_RIGHT_TRESH:
            delta_speed = abs(self.ground_sensors[1] - 950) * P_GAIN * 2 # TODO clean this x2  
            delta_speed = min(delta_speed, 100)
            motor_left_target -= delta_speed
            motor_right_target += delta_speed

        self.network.SetVariable("thymio-II", "motor.left.target", [motor_left_target])
        self.network.SetVariable("thymio-II", "motor.right.target", [motor_right_target])

        self.updatePose(motor_left_target, motor_right_target)

        return True

    def updatePose(self, motor_left_target, motor_right_target):
        # Convert motor speeds to [rad/s]
        motor_left_target_rads = motor_left_target * SPEED_UNIT_TO_RADS_CONVERTION
        motor_right_target_rads = motor_right_target * SPEED_UNIT_TO_RADS_CONVERTION

        # Compute relative speed (with respect to the current heading) (xR_dot [cm/s] and heading_dot [rad/s])
        xR_dot = WHEEL_RADIUS * (motor_left_target_rads + motor_right_target_rads) / 2 # note that yR_dot == 0
        heading_dot = WHEEL_RADIUS / (4*AXLE_LENGTH) * (motor_left_target_rads - motor_right_target_rads)

        # Move to absolute reference frame
        xI_dot = math.cos(self.current_heading) * xR_dot
        yI_dot = math.sin(self.current_heading) * xR_dot

        # Update current pose
        self.current_position[0] += xI_dot * TIMESTEP / 1e3 # /1e3 since TIMESTEP is in [ms]
        self.current_position[1] += yI_dot * TIMESTEP / 1e3
        self.current_heading += heading_dot * TIMESTEP / 1e3

    def updateGroundSensors(self):
        self.network.GetVariable("thymio-II", 'prox.ground.delta', reply_handler=self.variablesReply, error_handler=self.variablesError)

    def variablesReply(self, r):
        # print('Reply:', r)
        self.ground_sensors = list(map(int, r))

    def variablesError(self, e):
        print('Error:', e)

    def dbusReply(self, r):
        pass

    def dbusError(self, e):
        print('DBUS Error:', e)

    def hasReachedDistance(self):
        last_stopped_x, last_stopped_y = self.last_stopped_position
        current_x, current_y = self.current_position

        distance_covered = math.sqrt((current_x - last_stopped_x)**2 + (current_y - last_stopped_y)**2)

        return distance_covered > self.distance_to_travel

    def getCurrentPosition(self):
        return self.current_position

    def saveCurrentPosition(self, filepath):
        positions = []
        with open(filepath, 'r') as fp:
            positions = [line.rstrip() for line in fp.readlines()]

        with open(filepath, 'w') as fp:
            x, y = self.current_position
            positions.append([float(x), float(y)])
            fp.writelines("{}\n".format(position) for position in positions)
