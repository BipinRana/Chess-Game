import pygame
from ChessPiece import ChessPiece

screen_width = 800
screen_height = 620
class ChessBoard(pygame.sprite.Sprite):
    def __init__(self, image_file):
        super().__init__()  # Initialize the parent class
        # Load the background image
        self.bg_image = pygame.image.load('Assets/background.jpg').convert()
        self.bg_rect = self.bg_image.get_rect()
        self.image = pygame.transform.scale(self.bg_image, (800, 820))
        
        self.font = pygame.font.Font(None, 24)
        self.image = pygame.image.load(image_file).convert()
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (screen_width, screen_height))
        self.rect.topleft = (0, 100)  # Set the position of the chessboard
        self.pieces = pygame.sprite.Group()  # Group to hold all chess pieces
        self.piece_dict = {}  # Dictionary for quick access to pieces



    def add_piece(self, piece):
        self.pieces.add(piece)  # Add the piece to the sprite group
        self.piece_dict[piece.piece_type] = piece  # Store the piece using its name for quick access
  # Store piece in the dictionary

    def draw(self, screen):
        # Draw the chessboard image first
        screen.blit(self.bg_image, self.bg_rect)
        screen.blit(self.image, self.rect)  # Draw the chessboard background
        self.pieces.draw(screen)  # Draw all chess pieces

    def update(self):
        self.pieces.update()  # Call the update method for all pieces if needed

    def remove_piece(self, piece_name):
        
        if piece_name in self.piece_dict:
            piece = self.piece_dict[piece_name]
            piece.kill()  # Removes the sprite from all groups
            self.pieces.remove(piece)  # Remove from the sprite group
            del self.piece_dict[piece_name]  # Remove from the dictionary
    
    def display_sub_menu(self,screen, image_path, text, size,position):
        # Load and scale the submenu image
        sub_menu = pygame.image.load(image_path).convert_alpha()
        sub_menu = pygame.transform.scale(sub_menu, size)
        
        # Display the submenu at the specified position
        screen.blit(sub_menu, position)
        
        # Render the text
        text_surface = self.font.render(text, True, (255, 255, 255))  # White text color
        
        # Position the text within the submenu
        center_x = position[0] + size[0] / 2
        center_y = position[1] + size[1] / 2

        # Calculate the position for the text to be centered in the box
        text_pos = (center_x - text_surface.get_width() // 2, center_y - text_surface.get_height() // 2)
        
        # Blit the text onto the screen
        screen.blit(text_surface, text_pos)

        mouse_pos = pygame.mouse.get_pos()
        if (position[0] <= mouse_pos[0] <= position[0] + size[0] and position[1] <= mouse_pos[1] <= position[1] + size[1]):
        # Draw a highlight (e.g., a rectangle)
            highlight_rect = pygame.Rect(position[0] - 2, position[1] - 2, size[0] + 4, size[1] + 4)
            pygame.draw.rect(screen, (255, 255, 0), highlight_rect, 2)  # Yellow outline