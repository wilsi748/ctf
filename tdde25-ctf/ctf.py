from pygame.locals import *
import pymunk as pm
import math
import os
from menu import *


def ctf_game(mode, selected_map):
    """
    main game function, takes selected map and gamemode arguments
    """

    # ----- Initialisation ----- #
    # -- Initialise the display and sounds
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_mode()
    main_dir = os.path.split(os.path.abspath(__file__))[0]

    # -- Initialise the clock
    clock = pygame.time.Clock()

    # -- Initialise the physics engine
    space = pm.Space()
    space.gravity = (0.0,  0.0)

    # -- Import from the ctf framework
    import ai_new
    import boxmodels
    import images
    import gameobjects
    import maps

    # -- Constants
    framerate = 50

    # -- Variables
    #   Define the current level
    # select map with added map input
    current_map = maps.map0
    if selected_map == 0:
        current_map = maps.map0
    elif selected_map == 1:
        current_map = maps.map1
    elif selected_map == 2:
        current_map = maps.map2

    # List of all game objects
    game_objects_list = []
    tanks_list = []
    ai_list = []
    gun = []
    starttime = []
    bullet_list = []
    box_list = []
    point_list = []
    explosion_list = []

    # Load in all sounds
    cheer_sound = pygame.mixer.Sound(images.load_sound('cheer.wav'))
    explosion_sound = pygame.mixer.Sound(images.load_sound('explosion.wav'))
    music_sound = pygame.mixer.Sound(images.load_sound('music.wav'))
    music_sound.set_volume(0.1)

    # -- Resize the screen to the size of the current level
    screen = pygame.display.set_mode(current_map.rect().size)

    # -- Generate the background
    background = pygame.Surface(screen.get_size())

    # Copy the grass tile all over the level area
    for x in range(0, current_map.width):
        for y in range(0, current_map.height):
            # The call to the function "blit" will copy the image
            # contained in "images.grass" into the "background"
            # image at the coordinates given as the second argument
            background.blit(images.grass, (x*images.TILE_SIZE, y*images.TILE_SIZE))

    # -- Create the boxes
    for x in range(0, current_map.width):
        for y in range(0, current_map.height):
            # Get the type of boxes
            box_type = current_map.boxAt(x, y)
            box_model = boxmodels.get_model(box_type)
            if box_model is not None:
                if not box_model.destructable and not box_model.movable:
                    # Create a "Box" using the model "box_model" at the
                    # coordinate (x, y) (an offset of 0.5 is added since
                    # the constructor of the Box object expects to know
                    # the centre of the box, have a look at the coordinate
                    # systems section for more explanations).

                    box = gameobjects.Box(x + 0.5, y + 0.5, box_model, space)
                    bottom = pm.Segment(space.static_body, (x, y), (x+1, y), 0.1)
                    left = pm.Segment(space.static_body, (x, y), (x, y+1), 0.1)
                    right = pm.Segment(space.static_body, (x+1, y), (x+1, y+1), 0.1)
                    top = pm.Segment(space.static_body, (x, y+1), (x+1, y+1), 0.1)
                    space.add(bottom, left, right, top)
                    game_objects_list.append(box)
                    box_list.append(box)
                else:
                    box = gameobjects.Box(x + 0.5, y + 0.5, box_model, space)
                    game_objects_list.append(box)
                    box_list.append(box)

    # -- Create the tanks
    for i in range(0, len(current_map.start_positions)):
        # Get the starting position of the tank "i"
        pos = current_map.start_positions[i]
        # Create the tank, images.tanks contains the image representing the tank
        tank = gameobjects.Tank(pos[0], pos[1], pos[2], images.tanks[i], space)
        # Give the tank a name, currently numerically increasing
        tank.name = i
        # Add the tank to the list of objects to display
        game_objects_list.append(tank)
        # Add the tank to the lists of tanks
        tanks_list.append(tank)
        # Set start time for the tank
        starttime.append(0)
        # Set points
        point_list.append(0)

    # -- Create the flag
    flag = gameobjects.Flag(current_map.flag_position[0], current_map.flag_position[1])
    game_objects_list.append(flag)

    # -- Create the bases
    for i in range(0, len(current_map.start_positions)):
        base_pos = current_map.start_positions[i]
        base = gameobjects.GameVisibleObject(base_pos[0], base_pos[1], images.bases[i])
        game_objects_list.append(base)

    # -- Creating a barrier
    # Creating a body
    static_body = space.static_body
    # Creating a Top, Bottom, Left and Right barriers
    top = pm.Segment(static_body, (0, 0), (current_map.width, 0), 0)
    bottom = pm.Segment(static_body, (0, current_map.height), (current_map.width, current_map.height), 0)
    left = pm.Segment(static_body, (0, 0), (0, current_map.height), 0)
    right = pm.Segment(static_body, (current_map.width, 0), (current_map.width, current_map.height), 0)

    #  Add barriers to physics engine called space
    space.add(top, bottom, left, right)

    def explosion(bullet):
        """
        Function for explosion object
        """
        exp = gameobjects.Explosion(bullet.body.position[0], bullet.body.position[1])
        game_objects_list.append(exp)
        explosion_list.append(exp)
        explosion_sound.play()

    # Create a gun state for each tank
    for i in range(len(tanks_list)):
        status = False
        gun.append(status)

    # Creates a bullet on position of tank and uses tank
    # positional values to place the bullet slightly ahead of tank
    # using trigonometric calculations from the trig variable
    def create_bullet(tank_object):
        """
        Creating bullets function
        """
        trig = [0.7*math.sin(tank_object.body.angle), 0.7*math.cos(tank_object.body.angle)]
        bullet = gameobjects.Bullet(tank_object.body.position[0] - trig[0],
                                    tank_object.body.position[1] + trig[1],
                                    math.degrees(tank_object.body.angle),
                                    images.bullet, space)
        bullet.owner = tank_object.name  # Assigning a owner to each bullet
        bullet.parent = bullet
        game_objects_list.append(bullet)
        bullet_list.append(bullet)

    def print_points():
        """
        Prints the scoreboard
        """
        print("=====Score:======")
        for p in range(len(point_list)):
            print("| Player", p+1, ":", point_list[p])

    # -- Creating functions to handle collision events

    def collision_bullet_tank(arbiter, _space, data):
        """
        Handles collision between bullet and tank
        """
        _bullet = arbiter.shapes[0]
        _tank = arbiter.shapes[1]
        # Create a explosion
        explosion(_bullet)
        # Reduces health
        _tank.parent.hp -= 1

        if _tank.parent.hp <= 0:
            _tank.body.position = _tank.parent.start_position
            _tank.parent.hp = 3
            # Awards points
            point_list[_bullet.parent.owner] += 5
            # If tank has flag we drop it and award additional points
            if _tank.parent.flag == flag:
                gameobjects.Tank.drop_flag(_tank.parent, flag)
                point_list[_bullet.parent.owner] += 5
            print_points()
        if _bullet.parent in game_objects_list:
            bullet_list.remove(_bullet.parent)
            game_objects_list.remove(_bullet.parent)
        space.remove(_bullet, _bullet.body)
        return False

    handler = space.add_collision_handler(7, 1)
    handler.pre_solve = collision_bullet_tank

    def collision_bullet_box(arbiter, _space, data):
        """
        Handles collision between bullet and box
        """
        _bullet = arbiter.shapes[0]
        _box = arbiter.shapes[1]
        # Create a explosion
        explosion(_bullet.parent)
        if _box.parent.boxmodel.destructable:
            # If the bos is destructable reduce HP
            _box.parent.hp -= 1
        if _box.parent.hp <= 0:
            # If HP reaches 0, remove box
            space.remove(_box, _box.body)
            game_objects_list.remove(_box.parent)
            # Award point
            point_list[_bullet.parent.owner] += 1
            print_points()
        if _bullet.parent in game_objects_list:
            bullet_list.remove(_bullet.parent)
            game_objects_list.remove(_bullet.parent)
            space.remove(_bullet, _bullet.body)
        return False

    handler = space.add_collision_handler(7, 2)
    handler.pre_solve = collision_bullet_box

    def collision_bullet_barrier(arbiter, _space, data):
        """
        Handles collision between bullet and barrier
        """
        _bullet = arbiter.shapes[0]
        # Create explosion
        explosion(_bullet.parent)
        if _bullet.parent in game_objects_list:
            bullet_list.remove(_bullet.parent)
            game_objects_list.remove(_bullet.parent)
        space.remove(_bullet, _bullet.body)
        return False

    handler = space.add_collision_handler(7, 3)
    handler.pre_solve = collision_bullet_barrier

    def collision_bullet_bullet(arbiter, _space, data):
        """
        Handles collision between bullet and another bullet
        """
        _bullet = arbiter.shapes[0]
        # Create explosion
        explosion(_bullet.parent)
        if _bullet.parent in game_objects_list:
            bullet_list.remove(_bullet.parent)
            game_objects_list.remove(_bullet.parent)
        space.remove(_bullet, _bullet.body)
        return False

    handler = space.add_collision_handler(7, 0)
    handler.pre_solve = collision_bullet_bullet

    def player1():
        """
        Define controls for player 1
        """
        # Handles acceleration and deceleration, back or forwards input is given the tank stops
        if pygame.key.get_pressed()[pygame.K_UP] != 0:
            gameobjects.Tank.accelerate(tanks_list[0])
        elif pygame.key.get_pressed()[pygame.K_DOWN] != 0:
            gameobjects.Tank.decelerate(tanks_list[0])
        else:
            gameobjects.Tank.stop_moving(tanks_list[0])
        # Handles steering, if no steering input is given the tank stops turning
        if pygame.key.get_pressed()[pygame.K_LEFT] != 0:
            gameobjects.Tank.turn_left(tanks_list[0])
        elif pygame.key.get_pressed()[pygame.K_RIGHT] != 0:
            gameobjects.Tank.turn_right(tanks_list[0])
        else:
            gameobjects.Tank.stop_turning(tanks_list[0])

        # Shoot
        if event.type == KEYDOWN and event.key == K_SPACE:
            tanks_list[0].shoot()

    def player2():
        """
        Define controls for player 2
        """
        # Handles acceleration and deceleration, back or forwards input is given the tank stops
        if pygame.key.get_pressed()[pygame.K_w] != 0:
            gameobjects.Tank.accelerate(tanks_list[1])
        elif pygame.key.get_pressed()[pygame.K_s] != 0:
            gameobjects.Tank.decelerate(tanks_list[1])
        else:
            gameobjects.Tank.stop_moving(tanks_list[1])
        # Handles steering, if no steering input is given the tank stops turning
        if pygame.key.get_pressed()[pygame.K_a] != 0:
            gameobjects.Tank.turn_left(tanks_list[1])
        elif pygame.key.get_pressed()[pygame.K_d] != 0:
            gameobjects.Tank.turn_right(tanks_list[1])
        else:
            gameobjects.Tank.stop_turning(tanks_list[1])

        # Shoot
        if event.type == KEYDOWN and event.key == K_TAB:
            tanks_list[1].shoot()

    # -- Creating the AIs and adding them to a list
    if mode == "singleplayer":
        for i in range(1, len(tanks_list)):
            ai_list.append(ai_new.SimpleAi(tanks_list[i], game_objects_list, tanks_list, space, current_map))
    elif mode == "multiplayer":
        for i in range(2, len(tanks_list)):
            ai_list.append(ai_new.SimpleAi(tanks_list[i], game_objects_list, tanks_list, space, current_map))
    else:
        for i in range(0, len(tanks_list)):
            ai_list.append(ai_new.SimpleAi(tanks_list[i], game_objects_list, tanks_list, space, current_map))

    # ----- Main Loop ----- #

    # -- Control whether the game run
    running = True
    skip_update = 0

    while running:

        # plays background music
        if not music_sound.play():
            music_sound.play()

        # -- Handle the events
        for event in pygame.event.get():
            # Check if we receive a QUIT event (for instance, if the user press the
            # close button of the window) or if the user press the escape key.
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                music_sound.stop()  # Stop music if exit game
                running = False

            # Get controls from player functions
            if mode == "singleplayer":
                player1()
            if mode == "multiplayer":
                player1()
                player2()

        # Getting AI decisions
        for i in range(len(ai_list)):
            ai_new.SimpleAi.decide(ai_list[i])

        # -- Update physics
        if skip_update == 0:
            # Loop over all the game objects and update their speed in function of their
            # acceleration.
            for obj in game_objects_list:
                obj.update()
                skip_update = 5
        else:
            skip_update -= 1

        # Check collisions and update the objects position
        space.step(1 / framerate)

        # Update object that depends on an other object position (for instance a flag)
        for obj in game_objects_list:
            obj.post_update()

        # Function to see if a tank can grab the flag and if it can, it grabs the flag
        for i in range(len(tanks_list)):
            gameobjects.Tank.try_grab_flag(tanks_list[i], game_objects_list[game_objects_list.index(flag)])

        # Function to see if a tank has reached the base with the flag if so the tank score point
        for i in range(len(tanks_list)):
            if tanks_list[i].has_won():
                gameobjects.Tank.drop_flag(tanks_list[i], flag)
                game_objects_list[game_objects_list.index(flag)].x = current_map.flag_position[0]
                game_objects_list[game_objects_list.index(flag)].y = current_map.flag_position[1]
                point_list[i] += 100
                print_points()
                cheer_sound.play()

        # Handles tank shooting functionality
        for i in range(0, len(tanks_list)):
            if tanks_list[i].is_shooting:
                if not gun[i]:
                    starttime[i] = pygame.time.get_ticks()  # Starttime for reload
                    create_bullet(tanks_list[i])
                    gun[i] = True
                else:
                    tanks_list[i].is_shooting = False
                # After 1500 gameticks reload is over
                if gun[i] and pygame.time.get_ticks() - starttime[i] >= 1500:
                    gun[i] = False
                    tanks_list[i].is_shooting = False

        # Shows explosion graphic and removes it
        if explosion_list is not []:
            for i in explosion_list:
                if i.delete_this == 1:
                    game_objects_list.pop(game_objects_list.index(i))
                    explosion_list.remove(i)

        # -- Update Display
        # Display the background on the screen
        screen.blit(background, (0, 0))

        # Update the display of the game objects on the screen
        for obj in game_objects_list:
            # For each object, simply call the "update_screen" function
            obj.update_screen(screen)

        # Redisplay the entire screen (see double buffer technique)
        pygame.display.flip()

        # Control the game framerate
        clock.tick(framerate)
