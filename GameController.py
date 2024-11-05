import pygame
import numpy as np
from ChessBoard import ChessBoard
from ChessPiece import ChessPiece  # Import your piece class
from ChessData import ChessData



class GameController:
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen_width = 800
        self.screen_height = 620
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Chess Game")  # Adds a title to the window
        self.clock = pygame.time.Clock()
        self.chessboard = ChessBoard("Assets/Board.png")
        self.running = True
        self.pause = False
        self.game_over = False
        self.game_start_sound=pygame.mixer.Sound("Assets/game_start.mp3")
        self.piece_capture_sound=pygame.mixer.Sound("Assets/capture.mp3")
        self.piece_move_sound=pygame.mixer.Sound("Assets/move.mp3")
        self.check_mate_sound=pygame.mixer.Sound("Assets/game over checkmate.mp3")
        self.castling_sound=pygame.mixer.Sound("Assets/castling.mp3")
        self.menu_over=False
        
        
    def initialize_pieces(self):

        for pieces in self.chessboard.piece_dict.copy():
            self.chessboard.remove_piece(pieces)
        # Add pawns
        for i in range(8):
            self.chessboard.add_piece(ChessPiece(f"white_pawn{i + 1}", "white", "Assets/PawnWhite.png", [i * 100 + 20, 472.5], self.screen))
            self.chessboard.add_piece(ChessPiece(f"black_pawn{i + 1}", "black", "Assets/PawnBlack.png", [i * 100 + 20, 85], self.screen))

        # Add other pieces
        self.chessboard.add_piece(ChessPiece("white_rook1", "white", "Assets/RookWhite.png", [20, 550], self.screen))
        self.chessboard.add_piece(ChessPiece("white_rook2", "white", "Assets/RookWhite.png", [720, 550], self.screen))

        self.chessboard.add_piece(ChessPiece("white_bishop1", "white", "Assets/BishopWhite.png", [220, 550], self.screen))
        self.chessboard.add_piece(ChessPiece("white_bishop2", "white", "Assets/BishopWhite.png", [520, 550], self.screen))

        self.chessboard.add_piece(ChessPiece("white_king", "white", "Assets/KingWhite.png", [420, 550], self.screen))
        self.chessboard.add_piece(ChessPiece("white_queen", "white", "Assets/QueenWhite.png", [320, 550], self.screen))

        self.chessboard.add_piece(ChessPiece("white_knight1", "white", "Assets/KnightWhite.png", [120, 550], self.screen))
        self.chessboard.add_piece(ChessPiece("white_knight2", "white", "Assets/KnightWhite.png", [620, 550], self.screen))

        self.chessboard.add_piece(ChessPiece("black_rook1", "black", "Assets/RookBlack.png", [20,7.5], self.screen))
        self.chessboard.add_piece(ChessPiece("black_rook2", "black", "Assets/RookBlack.png", [720, 7.5], self.screen))

        self.chessboard.add_piece(ChessPiece("black_bishop1", "black", "Assets/BishopBlack.png", [220, 7.5], self.screen))
        self.chessboard.add_piece(ChessPiece("black_bishop2", "black", "Assets/BishopBlack.png", [520, 7.5], self.screen))

        self.chessboard.add_piece(ChessPiece("black_king", "black", "Assets/KingBlack.png", [420, 7.5], self.screen))
        self.chessboard.add_piece(ChessPiece("black_queen", "black", "Assets/QueenBlack.png", [320, 7.5], self.screen))

        self.chessboard.add_piece(ChessPiece("black_knight1", "black", "Assets/KnightBlack.png", [120, 7.5], self.screen))
        self.chessboard.add_piece(ChessPiece("black_knight2", "black", "Assets/KnightBlack.png", [620, 7.5], self.screen))
        
        self.game_start_sound.play()
    def run(self):
        while self.running:
            current_event=None
            if not ChessData.get_game():
                self.check_mate_sound.play()
                self.menu_over=False
                break

            for event in pygame.event.get():
                current_event=event
                if event.type == pygame.QUIT:
                    self.running = False
                
                # Handle events for each piece
                for piece in self.chessboard.pieces:
                    piece.handle_event(event)

            if ChessData.get_move_sound() and not ChessData.get_castling_side():
                self.piece_move_sound.play()
                ChessData.update_move_sound(False)


            if ChessData.get_castling_side()=="left":
                color="white"
                if ChessData.get_chess_turn()=="white":
                    color="black"
                self.chessboard.remove_piece(f"{color}_rook1")
                y=7.5
                if color=="white":
                    y=550
                self.chessboard.add_piece(ChessPiece(f"{color}_rook1", color, f"Assets/Rook{color.capitalize()}.png", [320,y], self.screen))
                ChessData.update_get_castling_side("")
                self.castling_sound.play()
            elif ChessData.get_castling_side()=="right":
                color="white"
                if ChessData.get_chess_turn()=="white":
                    color="black"
                self.chessboard.remove_piece(f"{color}_rook2")
                y=7.5
                if color=="white":
                    y=550
                self.chessboard.add_piece(ChessPiece(f"{color}_rook2", color, f"Assets/Rook{color.capitalize()}.png", [520,y], self.screen))
                ChessData.update_get_castling_side("")
                self.castling_sound.play()


            if ChessData.get_removed_piece():
                self.chessboard.remove_piece(ChessData.get_removed_piece())
                self.piece_capture_sound.play()
                ChessData.update_removed_piece("")

            
                

                
            # Update pieces
            for piece in self.chessboard.pieces:
                piece.update()

            self.screen.fill((255, 255, 255))  # Fill screen with white
            self.chessboard.draw(self.screen)  # Draw the chessboard and pieces
            
            # Show possible moves for all pieces (if any)
            for piece in self.chessboard.pieces:
                piece.show_possible_moves(current_event)

            

            pygame.display.flip()  # Update the display
            self.clock.tick(60)  # Limit to 60 frames per second
        
        
    def game_over_menu(self):
        while(not self.menu_over):
            pygame.display.flip()
            game_over_menu = pygame.image.load("Assets/wooden_board.png").convert_alpha()  # Use your own marker image here
            game_over_menu = pygame.transform.scale(game_over_menu, (300, 310)) 
            self.screen.blit(game_over_menu, (270, 162.5))
            font = pygame.font.Font(None, 40)  # Use default font and set size
            winner_text = "Black Wins!" if ChessData.get_chess_turn() == "white" else "White Wins!"
            game_over_text = font.render(winner_text, True, (0, 0, 0))  # Black text
            self.screen.blit(game_over_text, (335, 200))
            self.chessboard.display_sub_menu(self.screen,image_path="Assets/Asset 9@4x.png",text="Restart",size=(150, 50),position=(345, 240))
            self.chessboard.display_sub_menu(self.screen,image_path="Assets/Asset 9@4x.png",text="Main Menu",size=(150, 50),position=(345, 305))
            self.chessboard.display_sub_menu(self.screen,image_path="Assets/Asset 9@4x.png",text="Quit",size=(150, 50),position=(345, 370))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = False
                    self.running = False 
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()  # Get the current mouse position
            
            # Check if the mouse is over the submenu
                    if (345 <= mouse_pos[0] <= 345 + 150 and 220 <= mouse_pos[1] <= 240 + 50):  # Change these values based on your submenu position and size
                        self.running = True
                        ChessData.new_game()
                        ChessData.board_reset()
                        self.menu_over=True

                    elif (345 <= mouse_pos[0] <= 345 + 150 and 350 <= mouse_pos[1] <= 370 + 50):
                        self.menu_over=True
                        self.game_over = True  # Exit game over state
                        self.running = False  # Stop the main loop
                        pygame.mixer.stop()  # Stop all sounds
                        pygame.mixer.quit()  # Quit the mixer
                        pygame.quit()  # Quit Pygame
