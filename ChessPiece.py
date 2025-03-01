import pygame
import math
import numpy as np
import random
from ChessData import ChessData
import time

points = []
for i in range(8):  # For rows (Y values)
    for j in range(8):  # For columns (X values)
        x = 50 + j * 100  # X values: 50, 150, 250, ..., 750
        y = 155 + i * 75   # Y values: 55, 130, 205, ..., up to 8th term
        points.append((x, y))
class ChessPiece(pygame.sprite.Sprite):
    def __init__(self, piece_type, color, image_file, position, screen):
        super().__init__()
        self.piece_type = piece_type
        self.color = color
        self.screen = screen
        self.updated_flag = False
        self.dragging = False  # Flag to check if the piece is being dragged
        self.load_image(image_file)
        self.set_position(position)
        self.load_markers()
        self.bot = ChessData.get_bot()

    def load_image(self, image_file):
        self.image = pygame.image.load(image_file).convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()

    def set_position(self, position):
        self.rect.topleft = position

    def load_markers(self):
        self.move_marker = pygame.image.load("Assets/direction.png").convert_alpha()  # Use your own marker image here
        self.takes_marker = pygame.image.load("Assets/direction2.png").convert_alpha()  # Use your own marker image here
        self.takes_marker = pygame.transform.scale(self.takes_marker, (100, 77.6))  # Scale the marker to fit your grid
        self.move_marker = pygame.transform.scale(self.move_marker, (100, 77.6))

    def update(self):
        if self.dragging and ChessData.get_dragging_flag():
            # Update the position of the piece to follow the mouse cursor
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.rect.center = (mouse_x, mouse_y)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN :
            x, y = find_closest_point(event.pos)
            x = int((x - 50) / 100)
            y = int((y - 155) / 75)
            piece_name = ChessData.get_chess_board()[x][y]
            if ChessData.get_chess_turn() in piece_name and ((ChessData.get_multiplayer_flag() and ChessData.get_game_color() == ChessData.get_chess_turn()) or not ChessData.get_multiplayer_flag()):  # Ensure turn matches the piece clicked
                ChessData.update_active_piece(piece_name)
            else:
                return

            if self.rect.collidepoint(event.pos) and not ChessData.get_dragging_flag() and self.piece_type == ChessData.get_active_piece():
                self.dragging = True  # Start dragging the piece
                ChessData.update_dragging_flag(True)

        if event.type == pygame.MOUSEBUTTONUP:
            self.updated_flag = False
            if self.dragging:
                self.dragging = False  # Stop dragging the piece
                ChessData.update_dragging_flag(False)
                released_position = find_closest_point(event.pos)
                x, y = released_position
                x = int((x - 50) / 100)
                y = int((y - 155) / 75)
                released_position = np.array([x, y])

                if self.piece_type == ChessData.get_active_piece():
                    for moves in ChessData.get_outline_moves():
                        x, y = moves
                        x, y = int(x), int(y)
                        moves = np.array([x, y])

                        if np.array_equal(released_position, moves):
                            new_x, new_y = released_position
                            x_position = int(new_x) * 100 + 20
                            y_position = int(new_y) * 77.5 + 107.5
                            self.rect.topleft = (x_position, y_position)
                            self.updated_flag = True
                            piece_position = ChessData.get_chess_board()
                            old_x, old_y = np.argwhere(ChessData.get_chess_board() == ChessData.get_active_piece())[0]
                            if ChessData.get_chess_board()[new_x][new_y] != ".":  # If there is a piece in the target square
                                captured_piece = ChessData.get_chess_board()[new_x][new_y]  # Get the captured piece
                                ChessData.update_removed_piece(captured_piece)  # Update removed pieces list
                                ChessData.handle_removed_pieces_pixels(captured_piece)
                            else:
                                ChessData.update_move_sound(True)

                            if 'king' in ChessData.get_active_piece():
                                if new_x == 6 and self.is_right_castling_available():
                                    piece_position[5][new_y] = ChessData.get_chess_turn() + "_rook2"
                                    piece_position[7][new_y] = "."
                                    ChessData.update_get_castling_side("right")
                                if new_x == 2 and self.is_left_castling_available():
                                    piece_position[3][new_y] = ChessData.get_chess_turn() + "_rook1"
                                    piece_position[0][new_y] = "."
                                    ChessData.update_get_castling_side("left")
                            if ('black_pawn' in ChessData.get_active_piece() and new_y == 3 and old_y == 1) or ('white_pawn' in ChessData.get_active_piece() and new_y == 4 and old_y == 6):
                                ChessData.update_en_passant_piece(int(new_x), int(new_y))
                            promotion = 0 if (ChessData.get_chess_turn() == "black" and ChessData.get_game_color() =='black') or (ChessData.get_chess_turn() == "white" and ChessData.get_game_color() =='white') else 7
                            if 'pawn' in ChessData.get_active_piece() and new_y == promotion:
                                ChessData.update_promotion_piece((int(new_x), int(new_y)), ChessData.get_active_piece())
                            if ChessData.get_en_passant_piece():
                                if 'pawn' in ChessData.get_active_piece() and np.all(np.isclose((new_x, new_y), (ChessData.get_en_passant_piece()['final'][0], ChessData.get_en_passant_piece()['final'][1]))):
                                    ChessData.update_removed_piece(ChessData.update_removed_piece(ChessData.get_chess_board()[new_x][old_y]))
                                    ChessData.add_moves_to_history({"piece": ChessData.get_active_piece(), "old": [old_x, old_y], "new": [new_x, new_y], "castle": ChessData.get_castling_side(), "promotion": ChessData.get_promotion_piece(),'enpassant':True, "removed": ChessData.get_chess_board()[new_x][old_y]})
                                    new_board = ChessData.get_chess_board()
                                    new_board[new_x][old_y] = '.'
                                    ChessData.update_chess_board(new_board)
                            else:
                                ChessData.add_moves_to_history({"piece": ChessData.get_active_piece(), "old": [old_x, old_y], "new": [new_x, new_y], "castle": ChessData.get_castling_side(), "promotion": ChessData.get_promotion_piece(),'enpassant':False, "removed": ChessData.get_chess_board()[new_x][new_y]})
                            
                            piece_position[old_x][old_y] = "."
                            piece_position[new_x][new_y] = ChessData.get_active_piece()
                            ChessData.update_chess_board(piece_position)
                            ChessData.false_outline_flag()
                            ChessData.update_chess_turn()
                            ChessData.update_has_piece_moved(ChessData.get_active_piece())

                            king_location = np.argwhere(ChessData.get_chess_board() == (ChessData.get_chess_turn() + "_king"))[0]
                            if is_piece_in_check(ChessData.get_chess_turn(), ChessData.get_chess_board(), king_location):
                                if is_it_checkmate():
                                    ChessData.game_over()
                            ChessData.update_enpassant_count('-')
                            if not ChessData.get_removed_piece():
                                ChessData.update_active_piece("")
                            ChessData.update_suggested_moves(None)
                            if ChessData.get_multiplayer_flag():
                                ChessData.update_multiplayer_move_flag(True)
                    if not self.updated_flag:
                        active_piece = ChessData.get_active_piece()
                        x, y = np.argwhere(ChessData.get_chess_board() == active_piece)[0]
                        x_position = x * 100 + 20
                        y_position = y * 77.5 + 107.5
                        self.rect.topleft = (x_position, y_position)
                
                    

            #if position is not available go back to previous position
            #else if the ending position is true , set new position

    @classmethod
    def get_possible_moves(self,piece, chess_board_arg):
        """
        Generates all possible moves for a piece without considering king safety.
        """
        
        current_position = np.argwhere(chess_board_arg == piece)
        possible_moves = np.empty((0, 2), dtype=int)

        if "pawn" in piece:
            possible_moves = self.handle_pawn_moves(piece, current_position, chess_board_arg)
        elif "knight" in piece:
            possible_moves = self.handle_knight_moves(piece, current_position, chess_board_arg)
        elif "rook" in piece:
            possible_moves = self.handle_rook_moves(piece, current_position, chess_board_arg)
        elif "bishop" in piece:
            possible_moves = self.handle_bishop_moves(piece, current_position, chess_board_arg)
        elif "queen" in piece:
            possible_moves = self.handle_queen_moves(piece, current_position, chess_board_arg)
        elif "king" in piece:
            possible_moves = self.handle_king_moves(piece, current_position, chess_board_arg)

        return possible_moves
    

    def add_castling_moves(self,moves,piece, chess_board):
        """
        Adds castling moves to the king's list of moves if available.
        """
        king_location = np.argwhere(chess_board == (ChessData.get_chess_turn() + "_king"))[0]
        if piece == ChessData.get_chess_turn() + "_king" and not ChessData.get_has_piece_moved(piece) and not is_piece_in_check(ChessData.get_chess_turn(), ChessData.get_chess_board(), king_location):
            y = 7 if (ChessData.get_chess_turn() == "white" and ChessData.get_game_color()=='white') or (ChessData.get_chess_turn() == "black" and ChessData.get_game_color()=='black')  else 0
            if ChessPiece.is_right_castling_available() and ChessData.get_chess_board()[5][y] == "." and ChessData.get_chess_board()[6][y] == "." and not is_piece_in_check(ChessData.get_chess_turn(), ChessData.get_chess_board(), [5,y]) and not is_piece_in_check(ChessData.get_chess_turn(), ChessData.get_chess_board(), [6,y]):
                moves = np.append(moves, [[6, y]], axis=0)
            if ChessPiece.is_left_castling_available() and ChessData.get_chess_board()[3][y] == "." and ChessData.get_chess_board()[2][y] == "." and ChessData.get_chess_board()[1][y] == "." and not is_piece_in_check(ChessData.get_chess_turn(), ChessData.get_chess_board(), [2,y]) and not is_piece_in_check(ChessData.get_chess_turn(), ChessData.get_chess_board(), [3,y]):
                moves = np.append(moves, [[2, y]], axis=0)
        return moves


    def handle_pawn_moves(piece, current_position, chess_board_arg):
        """
        Handles move generation for pawns.
        """
        # Implementation of pawn-specific logic goes here
        
        current_position = np.argwhere(chess_board_arg == piece)
        possible_moves = np.empty((0, 2),dtype=int)
        x_coord,y_coord=current_position[0]
        x_coord,y_coord=int(x_coord),int(y_coord)
        if ChessData.get_en_passant_piece() and [x_coord, y_coord] in ChessData.get_en_passant_piece()['initial']:

            possible_moves = np.append(possible_moves, [ChessData.get_en_passant_piece()['final']], axis=0)
        
        
        pawn_takes_one,pawn_takes_two=np.array([[-1,-1]]),np.array([[1,-1]])
        pawn_takes_color="black"
        if("black" in piece):
            pawn_takes_one,pawn_takes_two=np.array([[-1,1]]),np.array([[1,1]])
            pawn_takes_color="white"

        if ChessData.get_game_color() == 'black':
            pawn_takes_one,pawn_takes_two=np.array([[-1,1]]),np.array([[1,1]])
            if("black" in piece):
                pawn_takes_one,pawn_takes_two=np.array([[-1,-1]]),np.array([[1,-1]])


        pawn_takes_one_x,pawn_takes_one_y= pawn_takes_one[0]
        pawn_takes_two_x,pawn_takes_two_y= pawn_takes_two[0]
        if (current_position[0][0] + pawn_takes_one_x <= 7 and
            current_position[0][0] + pawn_takes_one_x >= 0 and
            current_position[0][1] + pawn_takes_one_y <= 7 and
            current_position[0][1] + pawn_takes_one_y >= 0 and
            pawn_takes_color in chess_board_arg[current_position[0][0] + pawn_takes_one_x][current_position[0][1] + pawn_takes_one_y]):
                possible_moves = np.append(possible_moves, current_position[0] + pawn_takes_one, axis=0)
        if (current_position[0][0] + pawn_takes_two_x <= 7 and
            current_position[0][0] + pawn_takes_two_x >= 0 and
            current_position[0][1] + pawn_takes_two_y <= 7 and
            current_position[0][1] + pawn_takes_two_y >= 0 and
            pawn_takes_color in chess_board_arg[current_position[0][0] + pawn_takes_two_x][current_position[0][1] + pawn_takes_two_y]):
            possible_moves = np.append(possible_moves, current_position + pawn_takes_two, axis=0)

        first_move=np.array([[0, -1]])
        if (("black" in piece and not ChessData.get_game_color() =='black') or ("white" in piece and not ChessData.get_game_color() =='white')): 
            first_move=np.array([[0, 1]])

        if (y_coord+first_move[0][1]<8 and y_coord+first_move[0][1]>=0 and "." in chess_board_arg[x_coord][y_coord+first_move[0][1]]):
            possible_moves = np.append(possible_moves, current_position + first_move, axis=0)
        else:
            return possible_moves   
        second_move=np.empty((0,2))
        if (y_coord==6 and "white" in piece and ChessData.get_game_color()=='white') or (y_coord==6 and 'black' in piece and ChessData.get_game_color()=='black'):
            second_move = np.array([[0, -2]])
        elif (y_coord==1 and "white" in piece and ChessData.get_game_color()=='black' or (y_coord==1 and 'black' in piece and ChessData.get_game_color()=='white')):
            second_move = np.array([[0, 2]])  
        else:
            return possible_moves                
        if ("." in chess_board_arg[x_coord][y_coord+second_move[0][1]]):
            possible_moves = np.append(possible_moves, current_position + second_move, axis=0)

        return possible_moves


    def handle_knight_moves(piece, current_position, chess_board_arg):
        """
        Handles move generation for knights.
        """
        current_position = np.argwhere(chess_board_arg == piece)
        possible_moves = np.empty((0, 2),dtype=int)
        move_offsets = np.array([[2, 1], [2, -1], [-2, 1], [-2, -1],[1, 2], [1, -2], [-1, 2], [-1, -2]])
        knight_cannot_move = "black" if "black" in piece else "white"
        # Loop through each offset and append the possible moves
        for offset in move_offsets:
            new_move = current_position + offset
            x,y = new_move[0]
            if x<0 or x>7 or y>7 or y<0:
                continue
            possible_moves = np.append(possible_moves, new_move, axis=0)
                
        new_possible_moves=np.empty((0, 2))
        for position in possible_moves:
                
                
            x_coord,y_coord=position
            x_coord,y_coord=int(x_coord),int(y_coord)
            new_position=np.array([[x_coord,y_coord]])
                
            if (not knight_cannot_move in chess_board_arg[x_coord][y_coord]):
                new_possible_moves=np.append(new_possible_moves,new_position,axis=0)
                   
            
        possible_moves= new_possible_moves
        # Implementation of knight-specific logic goes here
        return possible_moves


    def handle_rook_moves(piece, current_position, chess_board_arg):
        """
        Handles move generation for rooks.
        """
        current_position = np.argwhere(chess_board_arg == piece)
        possible_moves = np.empty((0, 2),dtype=int)
        # Implementation of rook-specific logic goes here
        x_coord, y_coord = current_position[0]
        rook_takes = "black" if "white" in piece else "white"

            # Moving left, right, up, and down
        possible_moves = add_moves_in_direction(x_coord - 1, y_coord, -1, 0, possible_moves, rook_takes,chess_board_arg)
        possible_moves = add_moves_in_direction(x_coord + 1, y_coord, 1, 0, possible_moves, rook_takes,chess_board_arg)
        possible_moves = add_moves_in_direction(x_coord, y_coord - 1, 0, -1, possible_moves, rook_takes,chess_board_arg)
        possible_moves = add_moves_in_direction(x_coord, y_coord + 1, 0, 1, possible_moves, rook_takes,chess_board_arg)
        return possible_moves


    def handle_bishop_moves(piece, current_position, chess_board_arg):
        """
        Handles move generation for bishops.
        """
        current_position = np.argwhere(chess_board_arg == piece)
        possible_moves = np.empty((0, 2),dtype=int)
        # Implementation of bishop-specific logic goes here
        x_coord, y_coord = current_position[0]
        bishop_takes = "black" if "white" in piece else "white"
            # Moving diagonally in all four directions
        possible_moves = add_moves_in_direction(x_coord - 1, y_coord - 1, -1, -1, possible_moves, bishop_takes,chess_board_arg)  # top-left
        possible_moves = add_moves_in_direction(x_coord + 1, y_coord - 1, 1, -1, possible_moves, bishop_takes,chess_board_arg)   # top-right
        possible_moves = add_moves_in_direction(x_coord - 1, y_coord + 1, -1, 1, possible_moves, bishop_takes,chess_board_arg)   # bottom-left
        possible_moves = add_moves_in_direction(x_coord + 1, y_coord + 1, 1, 1, possible_moves, bishop_takes,chess_board_arg)     # bottom-right
        return possible_moves


    def handle_queen_moves(piece, current_position, chess_board_arg):
        """
        Handles move generation for queens.
        """
        current_position = np.argwhere(chess_board_arg == piece)
        possible_moves = np.empty((0, 2),dtype=int)
    # Implementation of queen-specific logic goes here
        x_coord, y_coord = current_position[0]
        queen_takes = "black" if "white" in piece else "white"

            # Rook-like moves (horizontal and vertical)
        possible_moves = add_moves_in_direction(x_coord - 1, y_coord, -1, 0, possible_moves, queen_takes,chess_board_arg)  # left
        possible_moves = add_moves_in_direction(x_coord + 1, y_coord, 1, 0, possible_moves, queen_takes,chess_board_arg)   # right
        possible_moves = add_moves_in_direction(x_coord, y_coord - 1, 0, -1, possible_moves, queen_takes,chess_board_arg)  # up
        possible_moves = add_moves_in_direction(x_coord, y_coord + 1, 0, 1, possible_moves, queen_takes,chess_board_arg)   # down

    # Bishop-like moves (diagonal)
        possible_moves = add_moves_in_direction(x_coord - 1, y_coord - 1, -1, -1, possible_moves, queen_takes,chess_board_arg)  # top-left
        possible_moves = add_moves_in_direction(x_coord + 1, y_coord - 1, 1, -1, possible_moves, queen_takes,chess_board_arg)   # top-right
        possible_moves = add_moves_in_direction(x_coord - 1, y_coord + 1, -1, 1, possible_moves, queen_takes,chess_board_arg)   # bottom-left
        possible_moves = add_moves_in_direction(x_coord + 1, y_coord + 1, 1, 1, possible_moves, queen_takes,chess_board_arg)     # bottom-right
        return possible_moves


    def handle_king_moves(piece, current_position, chess_board_arg):
        """
        Handles move generation for kings.
        """
    # Implementation of king-specific logic goes here
        x_coord, y_coord = current_position[0]
        possible_moves = np.empty((0, 2),dtype=int)
        king_takes = "black" if "white" in piece else "white"
    
    # Possible directions the king can move (dx, dy)
        directions = [(-1, -1),(-1, 0), (-1, 1), (0, -1),(0, 1),(1, -1),(1, 0),(1, 1)]

        for dx, dy in directions:
            new_x = x_coord + dx
            new_y = y_coord + dy
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                if king_takes in chess_board_arg[new_x][new_y] or ChessData.get_chess_board()[new_x][new_y] == ".":
                    possible_moves = np.append(possible_moves, [[new_x, new_y]], axis=0)
        return possible_moves


    
    def show_possible_moves(self, event):
        if (event != None and event.type== pygame.MOUSEBUTTONDOWN and 0<=pygame.mouse.get_pos()[0]<=800 and 100<=pygame.mouse.get_pos()[1]<=720):
            ChessData.true_outline_flag()

            if (not ChessData.get_chess_turn() in ChessData.get_active_piece()):
                ChessData.false_outline_flag()
                return
            outline_moves=ChessPiece.get_possible_moves(ChessData.get_active_piece(),ChessData.get_chess_board())
            removed_king_in_check=np.empty((0,2))
            # Get the current chessboard state
            current_chessboard = ChessData.get_chess_board()

            # Initialize the array to store valid moves
            removed_king_in_check = np.empty((0, 2))

            # Get the position of the active piece
            old_x, old_y = np.argwhere(current_chessboard == ChessData.get_active_piece())[0]

            # Iterate through possible new positions for the active piece
            for moves in outline_moves:  # Assume possible_new_positions is defined elsewhere
                new_x, new_y = moves
                new_x, new_y = int(new_x), int(new_y)

                # Save the original values of the affected squares
                original_target = current_chessboard[new_x][new_y]  # Save the piece at the new position (if any)
                original_source = current_chessboard[old_x][old_y]  # Save the piece being moved

                # Apply the move
                current_chessboard[new_x][new_y] = ChessData.get_active_piece()
                current_chessboard[old_x][old_y] = "."

                # Find the king's location
                king_location = np.argwhere(current_chessboard == (ChessData.get_chess_turn() + "_king"))[0]

                # Check if the king is in check after the move
                if not is_piece_in_check(ChessData.get_chess_turn(), current_chessboard, king_location):
                    removed_king_in_check = np.append(removed_king_in_check, [[new_x, new_y]], axis=0)

                # Revert the changes to restore the original chessboard state
                current_chessboard[new_x][new_y] = original_target
                current_chessboard[old_x][old_y] = original_source

            # Now `removed_king_in_check` contains the valid moves where the king is not in check


            outline_moves=removed_king_in_check
            outline_moves = self.add_castling_moves(outline_moves,ChessData.get_active_piece(),ChessData.get_chess_board())

            ChessData.update_outline_moves(outline_moves)
        if ChessData.get_outline_flag() :
        # Check if the mouse is over the piece
            takes_color="black"
            if "black" in ChessData.get_active_piece():
                takes_color="white"
        
            for i in ChessData.get_outline_moves():
                x, y = i
                x,y=int(x),int(y)
                x2 = x * 100   # Adjust x to fit the grid
                y2 = 100+y * 77.6   # Adjust y to fit the grid
                if takes_color in ChessData.get_chess_board()[x][y]:
                    self.screen.blit(self.takes_marker, (x2, y2))
                else:
                    self.screen.blit(self.move_marker, (x2, y2))
    
    @classmethod
    def is_right_castling_available(cls):
        color='white'
        if ChessData.get_chess_turn()=="black":
            color = 'black'
        return not ChessData.get_has_piece_moved(f'{color}_king') and not ChessData.get_has_piece_moved(f'{color}_rook2')
            
    @classmethod    
    def is_left_castling_available(cls):
        color='white'
        if ChessData.get_chess_turn()=="black":
            color = 'black'
        return not ChessData.get_has_piece_moved(f'{color}_king') and not ChessData.get_has_piece_moved(f'{color}_rook1')

    
     
            


def add_moves_in_direction(x, y, dx, dy, possible_moves, capture_color,chess_board_arg):
    while 0 <= x < 8 and 0 <= y < 8:
        if capture_color in chess_board_arg[x][y]:
            possible_moves = np.append(possible_moves, [[x, y]], axis=0)
            break
        if chess_board_arg[x][y] != ".":  
            break
        possible_moves = np.append(possible_moves, [[x, y]], axis=0)
        x += dx
        y += dy
    return possible_moves

def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

# Function to find the closest point
def find_closest_point(event_pos):
    closest_point = min(points, key=lambda point: distance(point, event_pos))
    return closest_point


    
def is_piece_in_check(color, chess_board,piece_location):
        
        opponent_color = "white" if color == "black" else "black"
    
        opponent_pieces = [piece for piece in chess_board.flatten() if opponent_color in piece]

        for each_piece in opponent_pieces:
            each_piece_possible_moves = ChessPiece.get_possible_moves(each_piece,chess_board)
            for takes_move in each_piece_possible_moves:
                takes_move_x, takes_move_y = map(int, takes_move)
                if np.isclose([takes_move_x, takes_move_y], piece_location).all():
                    return True 
        return False

def is_it_checkmate():
    for piece in ChessData.get_chess_board().flatten():
        if ChessData.get_chess_turn() in piece:
            each_possible_move = ChessPiece.get_possible_moves(piece, ChessData.get_chess_board())
            for moves in each_possible_move:
                new_x, new_y = moves
                new_x, new_y = int(new_x), int(new_y)
                
                # Get the current chessboard
                current_chessboard = ChessData.get_chess_board().copy()  # Create a copy to avoid modifying the original

                # Find the old position of the piece being moved
                old_x, old_y = np.argwhere(current_chessboard == piece)[0]

                # Save the original values of the affected squares
                original_target = current_chessboard[new_x][new_y]  # Save the piece at the new position (if any)
                original_source = current_chessboard[old_x][old_y]  # Save the piece being moved

                # Apply the move
                current_chessboard[new_x][new_y] = piece
                current_chessboard[old_x][old_y] = "."

                # Find the king's location
                king_location = np.argwhere(current_chessboard == (ChessData.get_chess_turn() + "_king"))[0]

                # Check if the king is in check after the move
                if not is_piece_in_check(ChessData.get_chess_turn(), current_chessboard, king_location):
                    # Revert the changes if not in check
                    current_chessboard[new_x][new_y] = original_target
                    current_chessboard[old_x][old_y] = original_source
                    return False

                # Revert the changes if in check
                current_chessboard[new_x][new_y] = original_target
                current_chessboard[old_x][old_y] = original_source

    print("Game is over")
    return True
