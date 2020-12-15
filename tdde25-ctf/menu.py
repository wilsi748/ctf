import pygame
import ctf 


def menu():
    """
    Define menu function
    """

    pygame.init()

    framerate = 50
    display_width = 800
    display_height = 600
    
    #Define colors
    black = (0, 0, 0)
    white = (255, 255, 255)
    green = (0, 255, 0)
    red = (255, 0, 0)
    blue = (0, 0, 255)
    brown = (205, 133, 63)
    grey = (169, 169, 169)
    # add default map value
    selected_map = 0
    # Display screen
    display = pygame.display.set_mode((display_width,  display_height), pygame.RESIZABLE)
    pygame.display.set_caption('Capture the Flag!')
    clock = pygame.time.Clock()

    # Define maps image
    m1 = [[0, 1, 0, 0, 0, 0, 0, 1, 0],
           [0, 1, 0, 2, 0, 2, 0, 1, 0], 
           [0, 2, 0, 1, 0, 1, 0, 2, 0], 
           [0, 0, 0, 1, 0, 1, 0, 0, 0], 
           [1, 1, 0, 3, 0, 3, 0, 1, 1], 
           [0, 0, 0, 1, 0, 1, 0, 0, 0], 
           [0, 2, 0, 1, 0, 1, 0, 2, 0], 
           [0, 1, 0, 2, 0, 2, 0, 1, 0], 
           [0, 1, 0, 0, 0, 0, 0, 1, 0]]
        
    m2 = [[0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0],
            [0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0],
            [0, 1, 0, 3, 1, 1, 0, 0, 0, 1, 1, 3, 0, 1, 0],
            [0, 2, 0, 0, 3, 0, 0, 2, 0, 0, 3, 0, 0, 2, 0],
            [2, 1, 0, 1, 1, 0, 1, 3, 1, 0, 1, 1, 0, 1, 2],
            [1, 1, 3, 0, 3, 2, 3, 0, 3, 2, 3, 0, 3, 1, 1],
            [2, 1, 0, 1, 1, 0, 1, 3, 1, 0, 1, 1, 0, 1, 2],
            [0, 2, 0, 0, 3, 0, 0, 2, 0, 0, 3, 0, 0, 2, 0],
            [0, 1, 0, 3, 1, 1, 0, 0, 0, 1, 1, 3, 0, 1, 0],
            [0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0],
            [0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0]]
        
    m3 = [[0, 2, 0, 2, 0, 0, 2, 0, 2, 0],
           [0, 3, 0, 1, 3, 3, 1, 0, 3, 0],
           [0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
           [0, 3, 0, 1, 3, 3, 1, 0, 3, 0],
           [0, 2, 0, 2, 0, 0, 2, 0, 2, 0]]
    
    def text_objects(text, font):
        """
        Creating text objects
        """
        text_surface = font.render(text, True, (255, 255, 255))
        return text_surface, text_surface.get_rect()

    def display_text(text, x, y, size):
        """
        Displaying text to the screen
        """
        font = pygame.font.Font('freesansbold.ttf', size)
        text_surf, text_rect = text_objects(text, font)
        text_rect.center = (x, y)
        display.blit(text_surf, text_rect)

    def button(msg, font_size, x, y, w, h, color, action):
        """
        Creating clickable buttons on the screen
        """
        mouse = pygame.mouse.get_pos() # Grabbing cursor position
        click = pygame.mouse.get_pressed() # Mouse button status
        
        # Check if cursor is on the button
        if x + w > mouse[0] > x and y + h > mouse[1] > y:
            # Draw the button
            pygame.draw.rect(display, color, (x, y, w, h)) 
            
            # Check if we have clicked on the button
            if click[0] == 1 and action is not None:
                
                # Run singleplayer mode
                if action == "Play S": 
                    mode = "singleplayer" # set mode
                    ctf.ctf_game(mode, selected_map)
                
                # Run multiplayer mode
                if action == "Play M":
                    mode = "multiplayer" # set mode
                    ctf.ctf_game(mode, selected_map)
                
                # Quit
                if action == "Quit":
                    pygame.quit()
                    quit()
                
                # Demo
                if action == "Demo":
                    mode = "demo"
                    ctf.ctf_game(mode, selected_map)
                    
                # set display
                pygame.display.set_mode((display_width,  display_height), pygame.RESIZABLE)
        
        # Displaying text on the button
        font = pygame.font.Font('freesansbold.ttf', font_size)
        text_surf, text_rect = text_objects(msg, font)
        text_rect.center = ((x+(w/2)), (y+(h/2)))
        display.blit(text_surf, text_rect)
        
    def draw_maps(m, y, x):
        """
        Drawing the maps to the screen
        """
        original_x = x  # Saving the orignal value of x coordinate
        
        # Loop through the map
        for j in m: 
            y += 10  # Increase y coordinate with 10
            x = original_x  # Reset x coordinate
            if isinstance(j, list):
                # Draw a color depending on value in map
                for i in j: 
                    if i == 0:
                        pygame.draw.rect(display, green, (x, y, 10, 10))
                        x += 10
                    elif i == 1:
                        pygame.draw.rect(display, grey, (x, y, 10, 10))
                        x += 10
                    elif i == 2:
                        pygame.draw.rect(display, brown, (x, y, 10 , 10))
                        x += 10
                    elif i == 3:
                        pygame.draw.rect(display, white, (x, y, 10, 10))
                        x += 10

    def select_maps(x, y, w, h, _selected_map, current_map):
        """
        Making it possible to select the maps
        """
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        # Checking where the cursor is
        if x + w > mouse[0] > x and y + h > mouse[1] > y:
            if click[0] == 1:
                if _selected_map >= 0:
                    return _selected_map
        return current_map

    # --- Main Loop ---#
    # -- Controls whether the menu run

    mainloop = True
    while mainloop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainloop = False
        
        # Drawing background
        display.fill(black)
        
        # Drawing menu header and buttons
        display_text("Capture the Flag!", 400, 50, 60)
        button("Singleplayer", 40, 265, 120, 280, 45, red, "Play S")
        button("Multiplayer", 40, 265, 180, 280, 45, green, "Play M")
        button("Quit", 40, 265, 240, 280, 45, blue, "Quit")
        button("Demo", 40, 265, 300, 280, 45, grey, "Demo")
        
        # Displaying map names
        display_text("Map 1", 100, 550, 25)
        display_text("Map 2", 400, 550, 25)
        display_text("Map 3", 700, 550, 25)
        
        # Calling functions for selecting maps
        selected_map = select_maps(50, 350, 110, 110, 0, selected_map)
        selected_map = select_maps(320, 350, 170, 130, 1, selected_map)
        selected_map = select_maps(640, 350, 120, 70, 2, selected_map)
        
        # Drawing graphics when a map is selected
        if selected_map == 0:
            pygame.draw.rect(display, red, (50, 350, 110, 110))
        if selected_map == 1:
            pygame.draw.rect(display, red, (320, 350, 170, 130))
        if selected_map == 2:
            pygame.draw.rect(display, red, (640, 350, 120, 70))
        
        # Drawing the maps
        draw_maps(m1, 350, 60)
        draw_maps(m2, 350, 330)
        draw_maps(m3, 350, 650)

        # Update display
        pygame.display.update()
        clock.tick(framerate)

    pygame.quit()
    quit()


if __name__ == '__main__':
    menu()
