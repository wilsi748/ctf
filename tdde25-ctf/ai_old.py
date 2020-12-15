import math
import pymunk
import gameobjects

#
# This is the base class for implementing, Ais, it contains some convenient functions
# useful for developing new Ais
#


class Ai:
    #
    # Initialise the AI object:
    # - tank object        representation of the tank controlled by this AI
    # - game_objects_list  all objects in the game
    # - space              physics engine
    #
    def __init__(self, tank, game_objects_list, tanks_list, space):
        self.tank = tank
        self.game_objects_list = game_objects_list
        self.tanks_list = tanks_list
        self.space = space
        self.flag = None
    #
    # This function is called every cycle to give an AI the opportunity to take a decision
    #

    def decide(self):
        return
    #
    # This function return the first object in the specified direction from the tank at a max_distance
    #

    def get_object_in_direction(self, max_distance, direction):
        query = self.query_objects_in_direction(max_distance, direction)

        if query is not None:
            return None
        # Find the object corresponding to that body
        for obj in self.game_objects_list:
            if hasattr(obj, 'body') and obj.body == query.shape.body:
                return obj
        return None
    #
    # Return true if an object is in the specified direction from the tank at a max_distance
    #

    def has_object_in_direction(self, max_distance, direction):
        return self.query_objects_in_direction(max_distance, direction) is not None
    #
    # Query the space objects for the list of bodies in the specified direction of the tank
    # (should not be used directly).
    #

    def query_objects_in_direction(self, max_distance, direction):
        tank_pos = self.tank.body.position
        tank_dir = pymunk.Vec2d(1, 0)
        tank_dir.angle = self.tank.body.angle + 0.5 * math.pi + direction

        return self.space.segment_query_first(tank_pos, tank_pos + max_distance * tank_dir)
    #
    # Return true if an object is in the specified absolute direction from the tank at a max_distance
    #

    def has_object_in_absolute_direction(self, max_distance, direction):
        return self.query_objects_in_absolute_direction(max_distance, direction) is not None
    #
    # Query the space objects for the list of bodies in specified absolute direction of the tank
    # (should not be used directly).
    #

    def query_objects_in_absolute_direction(self, max_distance, direction):
        tank_pos = self.tank.body.position
        tank_dir = pymunk.Vec2d(1, 0)
        tank_dir.angle = direction

        return self.space.segment_query_first(tank_pos, tank_pos + max_distance * tank_dir)
    #
    # Test if the object passed in parameter is movable
    #

    def is_object_movable(self, obj):
        return (hasattr(obj,  'boxmodel') and obj.boxmodel.movable) or self.is_object_tank(obj)
    #
    # Test if the object passed in parameter is a tank
    #

    def is_object_tank(self, obj):
        return isinstance(obj,  gameobjects.Tank);

    #
    # This function return the object for the flag
    #

    def get_flag(self):
        # self.flag is used as a cache for the flag
        # we cannot set self.flag in the constructor, because when the constructor is called
        # the game_objects_list does not contains the flag object yet
        if self.flag is not None:
            # Find the flag in the game objects list
            for obj in self.game_objects_list:
                if isinstance(obj, gameobjects.Flag):
                    self.flag = obj
                    break
        return self.flag

    #
    # This is a very simplistic AI which has a low probability of winning, and which is designed
    # on the principle of action/reaction.
    #
    # One of the principle idea behind the design of this AI is to make the best effort to ensure that tank
    # do not get stuck, to achieve that result, the tank try to either move horizontally or vertically.
    #


class SimpleAi(Ai):
    def __init__(self, tank,  game_objects_list, tanks_list, space):
        Ai.__init__(self, tank,  game_objects_list, tanks_list, space)
        self.last_shot = 20

        # This array contains the four acceptable directions for moving the tank
        self.directions         = [0, math.pi / 2, math.pi, -math.pi / 2]
        # This variable contains the direction that we are currently targeting
        self.turn_target        = -1
        # This variable contains whether the tank is currently trying to turn
        self.is_turning         = False
        # This variable contains whether the tank is supposed to turn left
        self.turn_left          = True

        self.last_position      = pymunk.Vec2d(self.tank.body.position)
        self.last_angle         = float(self.tank.body.angle)
        self.no_move_timeout    = 0
        self.backingout         = 0
        self.should_turn        = False

    def decide(self):
        if self.last_shot == 0:
            self.last_shot = 20
            # Check if we should shoot
            #
            # Use chipmunk raycasting to get if there is an object in front of the tank

            obj = self.get_object_in_direction(10, 0)

            if obj is not None:
                if hasattr(obj, 'boxmodel') and obj.boxmodel.destructable:
                    # it is a wooden box, lets clear the way
                    self.tank.shoot()
                if self.is_object_tank(obj):
                    # it is an other tank, shoot
                    self.tank.shoot()

        self.last_shot -= 1

        # Test if the tank is blocked

        if (self.last_position - self.tank.body.position).get_length() < 0.01 and math.cos(self.tank.body.angle - self.last_angle) > 0.995:
            self.no_move_timeout += 1
        else:
            self.no_move_timeout = 0
            # Update last position
            self.last_position      = pymunk.Vec2d(self.tank.body.position)
            self.last_angle         = float(self.tank.body.angle)

        #
        # If the tank is currently turning, check if it has reached the targetted destination
        #
        if self.is_turning and math.cos(self.directions[self.turn_target] - self.tank.body.angle) > 0.995:
            self.is_turning = False
            self.tank.stop_turning()

        if self.backingout == 0:
            self.tank.stop_moving()
            self.backingout = -1
        #
        # Tank is stuck, try to move backward
        #
        if self.no_move_timeout > 40:
            self.tank.stop_turning()
            self.tank.stop_moving()
            self.tank.decelerate()
            self.backingout   = 10
            self.should_turn  = True
        elif self.backingout > 0:
            self.tank.decelerate()
            self.backingout -= 1
        #
        # If the tank is not turning anymore
        #
        elif not self.is_turning:
            obj = self.get_object_in_direction(0.5, 0)
            #
            # Check that there is no obstacle in front. Or if there is an obstacle that it is a box that can be moved.
            #
            if not self.should_turn and (not self.has_object_in_direction(0.5, 0) or (obj is not None and self.is_object_movable(obj) and not self.is_object_tank(obj) )):
                self.tank.accelerate()
            else:
                self.should_turn = False
            #
            # The tank is blocked by an obstacle, then we need to turn.
            #
            self.tank.stop_moving()

            #
            # First we need to list the possible directions, which are the one without obstacles.
            #
            possible_directions  = [0, 1, 2, 3 ]

            # Make sure that we don't try to turn in the current direction or go back in the same direction
            current_direction           = self.ensure_turn_target_range(int(round(self.tank.body.angle / (math.pi / 2))))
            current_opposite_direction  = self.ensure_turn_target_range(current_direction + 2)
            possible_directions.remove(current_direction)
            possible_directions.remove(current_opposite_direction)

            # Test the other possible direction to check which one does not have an obstacle
            for dir in list(possible_directions):
                if self.has_object_in_absolute_direction(0.6, self.directions[dir] + math.pi / 2 ):
                    possible_directions.remove(dir)

            if possible_directions:
                # Select the direction that will make the tank goes toward the current point of interest
                current_target    = self.get_point_of_interest()
                direction         = current_target - self.tank.body.position
                best_angle_cos    = -10.0

                for dir in possible_directions:
                    angle_cos = math.cos( self.directions[dir] + math.pi / 2 - direction.get_angle() )
                    if angle_cos > best_angle_cos:
                        best_angle_cos = angle_cos
                        self.turn_target = dir
            else:
                # If no possible direction, then move backward
                self.turn_target = current_opposite_direction

            # Turn left or right
            if (self.turn_target > current_direction or (self.turn_target == 0 and current_direction == 3) ) and not (self.turn_target == 3 and current_direction == 0):
                self.turn_left = False
                self.tank.turn_right()
            else:
                self.turn_left = True
                self.tank.turn_left()

            self.is_turning   = True
        elif self.turn_left :
            self.tank.turn_left()
        else:
            self.tank.turn_right()

    # This function return the position of the point of interest
    #  Which is the flag or the base
    #
    def get_point_of_interest(self):
        if self.tank.flag is not None:
            return pymunk.Vec2d(self.tank.start_position)
        else:
            return pymunk.Vec2d(self.get_flag().x, self.get_flag().y)

    # This function ensure that the value is in the range 0 to 3
    def ensure_turn_target_range(self, value):
        while value < 0: value += 4
        while value >= 4: value -= 4
        return value
