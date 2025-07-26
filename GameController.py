import pygame
import numpy as np
from ChessBoard import ChessBoard
from ChessPiece import ChessPiece,is_piece_in_check  # Import your piece class
from ChessData import ChessData
import random
from stockfish import Stockfish
from client import ChessClient
import re

class GameController:
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen_width = 800
        self.screen_height = 820
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Chess Game")  # Adds a title to the window
        self.clock = pygame.time.Clock()
        self.chessboard = ChessBoard("Assets/Board.png")
        self.chessboard.draw(self.screen)
        self.running = True
        self.pause = False
        self.game_over = False
        self.game_start_sound=pygame.mixer.Sound("Assets/game_start.mp3")
        self.piece_capture_sound=pygame.mixer.Sound("Assets/capture.mp3")
        self.piece_move_sound=pygame.mixer.Sound("Assets/move.mp3")
        self.check_mate_sound=pygame.mixer.Sound("Assets/game over checkmate.mp3")
        self.castling_sound=pygame.mixer.Sound("Assets/castling.mp3")
        self.promotion_sound=pygame.mixer.Sound("Assets/promotion.mp3")
        self.menu_over = False
        self.singleplayer = False
        self.choose_difficulty = False
        self.bot = None
        self.piece_count= {'black_queen':1,'black_bishop':2,'black_knight':2,'black_rook':2,'white_queen':1,'white_bishop':2,'white_knight':2,'white_rook':2}
        self.prev_move_marker = pygame.image.load("Assets/previous_move.png").convert_alpha()  
        self.prev_move_marker = pygame.transform.scale(self.prev_move_marker, (100, 77.6)) 
        self.stockfish = Stockfish(path="stockfish/stockfish-windows-x86-64-avx2.exe")
        self.stockfish.set_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.suggested_move_marker = pygame.image.load("Assets/suggested_move.png").convert_alpha()  
        self.suggested_move_marker = pygame.transform.scale(self.suggested_move_marker, (100, 77.6))
        self.delay= 0 
        self.client = ChessClient()
        self.main_menu = True
        self.stalemate = False

    def initialize_pieces(self):

        for pieces in self.chessboard.piece_dict.copy():
            self.chessboard.remove_piece(pieces)
        # Add pawns
        row1 = 572.5,650
        row2= 185,107.5
        if ChessData.get_game_color() == 'black': 
            row1,row2 = row2,row1
            board = ChessData.get_chess_board().copy()
            board = board.T
            board[[0, 1, 6, 7]] = board[[7, 6, 1, 0]].copy()
            ChessData.update_chess_board(board.T)
        for i in range(8):
            self.chessboard.add_piece(ChessPiece(f"white_pawn{i + 1}", "white", "Assets/PawnWhite.png", [i * 100 + 20, row1[0]], self.screen))
            self.chessboard.add_piece(ChessPiece(f"black_pawn{i + 1}", "black", "Assets/PawnBlack.png", [i * 100 + 20, row2[0]], self.screen))

            # Add other pieces
        self.chessboard.add_piece(ChessPiece("white_rook1", "white", "Assets/RookWhite.png", [20, row1[1]], self.screen))
        self.chessboard.add_piece(ChessPiece("white_rook2", "white", "Assets/RookWhite.png", [720, row1[1]], self.screen))

        self.chessboard.add_piece(ChessPiece("white_bishop1", "white", "Assets/BishopWhite.png", [220, row1[1]], self.screen))
        self.chessboard.add_piece(ChessPiece("white_bishop2", "white", "Assets/BishopWhite.png", [520, row1[1]], self.screen))

        self.chessboard.add_piece(ChessPiece("white_king", "white", "Assets/KingWhite.png", [420, row1[1]], self.screen))
        self.chessboard.add_piece(ChessPiece("white_queen1", "white", "Assets/QueenWhite.png", [320, row1[1]], self.screen))

        self.chessboard.add_piece(ChessPiece("white_knight1", "white", "Assets/KnightWhite.png", [120, row1[1]], self.screen))
        self.chessboard.add_piece(ChessPiece("white_knight2", "white", "Assets/KnightWhite.png", [620, row1[1]], self.screen))

        self.chessboard.add_piece(ChessPiece("black_rook1", "black", "Assets/RookBlack.png", [20,row2[1]], self.screen))
        self.chessboard.add_piece(ChessPiece("black_rook2", "black", "Assets/RookBlack.png", [720, row2[1]], self.screen))

        self.chessboard.add_piece(ChessPiece("black_bishop1", "black", "Assets/BishopBlack.png", [220, row2[1]], self.screen))
        self.chessboard.add_piece(ChessPiece("black_bishop2", "black", "Assets/BishopBlack.png", [520, row2[1]], self.screen))

        self.chessboard.add_piece(ChessPiece("black_king", "black", "Assets/KingBlack.png", [420, row2[1]], self.screen))
        self.chessboard.add_piece(ChessPiece("black_queen1", "black", "Assets/QueenBlack.png", [320, row2[1]], self.screen))

        self.chessboard.add_piece(ChessPiece("black_knight1", "black", "Assets/KnightBlack.png", [120, row2[1]], self.screen))
        self.chessboard.add_piece(ChessPiece("black_knight2", "black", "Assets/KnightBlack.png", [620, row2[1]], self.screen))
        self.game_start_sound.play()


        
        
    def run(self):
        while self.running:
            self.handle_removed_pieces()
            self.check_game_over()
            current_event = None
            if not ChessData.get_game():
                self.check_mate_sound.play()
                self.menu_over = False
                break
            self.handle_bot_move()
            self.handle_opponent_move()
            for event in pygame.event.get():
                current_event = event
                if event.type == pygame.QUIT:
                    self.running = False
                    self.game_over = True
                    
                if (0<=pygame.mouse.get_pos()[0]<=800 and 100<=pygame.mouse.get_pos()[1]<=720 and event.type == pygame.MOUSEBUTTONDOWN) or event.type==pygame.MOUSEBUTTONUP:
                # Handle events for each piece
                    for piece in self.chessboard.pieces:
                        piece.handle_event(event)
                elif (0<=pygame.mouse.get_pos()[0]<=800 and 0<=pygame.mouse.get_pos()[1]<=100 and event.type == pygame.MOUSEBUTTONDOWN):
                        self.handle_side_menu_options(pygame.mouse.get_pos())

            if ChessData.get_move_sound() and not ChessData.get_castling_side():
                self.piece_move_sound.play()
                ChessData.update_move_sound(False)
            for piece in self.chessboard.pieces:
                piece.update()
            
            self.handle_castling()

            # Update pieces
            for piece in self.chessboard.pieces:
                piece.update()
            
            self.screen.fill((255, 255, 255))  # Fill screen with white
            self.chessboard.draw(self.screen)  # Draw the chessboard and pieces
            self.handle_previous_move()
            self.handle_side_menu()
            self.show_removed_pieces()
            self.handle_promotion()
            self.handle_suggested_move()
            self.send_current_move()
            # Show possible moves for all pieces (if any)
            for piece in self.chessboard.pieces:
                piece.show_possible_moves(current_event)
            
            
            
            pygame.display.flip()  # Update the display
            self.clock.tick(60)  # Limit to 60 frames per second
        if self.game_over == True:
            pygame.mixer.stop()
            pygame.mixer.quit()
            pygame.quit()

    def send_current_move(self):
        if ChessData.get_multiplayer_move_flag() and ChessData.chess_turn != ChessData.get_game_color():
            data = ChessData.board_history.get_current_state().copy()
            data['piece']=str(data['piece'])
            data['old']= [int(x) for x in data['old']]
            data['new']= [int(x) for x in data['new']]
            data['castle']= str(data['castle'])
            data['promotion']= bool(data['promotion'])
            if data['promotion']:
                x,y = data['new']
                data['promotion']= ChessData.get_chess_board()[x][y]
            data['enpassant']= data['enpassant']
            data['removed']= str(data['removed'])
            self.client.send_message(data)
            ChessData.update_multiplayer_move_flag(False)

    def handle_opponent_move(self):
        if ChessData.get_multiplayer_flag() and ChessData.get_opponent_response():
            res = ChessData.get_opponent_response()
            move,piece = res['new'],res['piece']
            x,y = move
            y = 7 -y
            move = x,y
            if move and piece :
                    self.update_board_for_move(move, piece ,res )
                    ChessData.update_opponent({})

    def handle_bot_move(self):
        if ChessData.get_bot() == "easy" and ChessData.get_chess_turn() == 'black':         
            try:
                moves, piece = easy_bot_algorithm(2)
                self.update_board_for_move(moves, piece , None)
            except:
                ChessData.game_over()
                print('game over')
        elif ChessData.get_bot() == "hard" and ChessData.get_chess_turn() == "black":
            if self.delay+random.randint(0,70) >100:
                self.stockfish.set_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
                self.stockfish.make_moves_from_current_position(ChessData.get_moves_made())
                old_pos,new_pos = ChessData.map_move(self.stockfish.get_best_move())
                piece_x,piece_y = old_pos
                piece = ChessData.get_chess_board()[piece_x][piece_y]
                self.update_board_for_move(new_pos, piece,None)
                self.delay=0
            else:
                self.delay +=1


    def update_board_for_move(self, moves, piece , history):
        new_x, new_y = map(int, moves)
        ChessData.update_active_piece(piece)
        ChessData.update_bot_move(moves, piece)
        self.updated_flag = True
        piece_position = ChessData.get_chess_board()
        old_x, old_y = np.argwhere(piece_position == piece)[0]
        if history:
            ChessData.add_moves_to_history(history)
        else:
            ChessData.add_moves_to_history({"piece": piece, "old": [old_x, old_y], "new": [new_x, new_y], "castle": False,'enpassant':False, "promotion": False, "removed": '.'})
        self.capture_piece_if_needed(new_x, new_y)
        self.handle_castling_for_king(new_x, new_y, piece_position)
        
        piece_position[old_x][old_y] = "."
        piece_position[new_x][new_y] = piece
        promotion_bool = False
        if history is not None and history['promotion']:
            promotion_bool = False
            self.chessboard.remove_piece(piece)
            piece_position[new_x][new_y] = history['promotion']
            self.chessboard.add_piece(ChessPiece(f"{history['promotion']}", f"{(history['promotion'])[:5]}", f"Assets/{(history['promotion'])[6:-1].capitalize()}{(history['promotion'])[:5].capitalize()}.png", [new_x * 100 + 20, 107.5 + new_y * 77.5], self.screen))
            
        ChessData.update_chess_board(piece_position)
        ChessData.update_chess_turn()
        ChessData.update_has_piece_moved(ChessData.get_active_piece())
        ChessData.update_active_piece("")
        self.update_chessboard_pieces(moves, piece ,promotion_bool)
        


    def capture_piece_if_needed(self, new_x, new_y):
        if ChessData.get_chess_board()[new_x][new_y] != ".":
            captured_piece = ChessData.get_chess_board()[new_x][new_y]
            ChessData.get_current_state()['removed'] = captured_piece
            ChessData.update_removed_piece(captured_piece)
            ChessData.handle_removed_pieces_pixels(captured_piece)
            
        else:
            ChessData.update_move_sound(True)

    def handle_castling_for_king(self, new_x, new_y, piece_position):
        if 'king' in ChessData.get_active_piece():
            if new_x == 6 and ChessPiece.is_right_castling_available():
                piece_position[5][new_y] = ChessData.get_chess_turn() + "_rook2"
                piece_position[7][new_y] = "."
                ChessData.update_get_castling_side("right")
            if new_x == 2 and ChessPiece.is_left_castling_available():
                piece_position[3][new_y] = ChessData.get_chess_turn() + "_rook1"
                piece_position[0][new_y] = "."
                ChessData.update_get_castling_side("left")

    def update_chessboard_pieces(self, moves, piece, promotion):
        piece_type = piece[6:-1].capitalize() + piece[:5].capitalize()
        if 'king' in piece:
            piece_type = piece[6:].capitalize() + piece[:5].capitalize()
        if not promotion:
            self.chessboard.remove_piece(piece)
            x, y = map(int, moves)
            self.chessboard.add_piece(ChessPiece(piece, piece[:5], f"Assets/{piece_type}.png", [x * 100 + 20, 107.5 + y * 77.5], self.screen))
        ChessData.update_bot_move([], "")

    def handle_castling(self):
        if ChessData.get_castling_side() in ["left", "right"]:
            color = "white" if ChessData.get_chess_turn() == "black" else "black"
            rook = f"{color}_rook1" if ChessData.get_castling_side() == "left" else f"{color}_rook2"
            self.chessboard.remove_piece(rook)
            y = 650 if (color == "white" and ChessData.get_game_color() =='white') or (color == "black" and ChessData.get_game_color() =='black')  else 107.5
            x = 320 if ChessData.get_castling_side() == "left" else 520
            self.chessboard.add_piece(ChessPiece(rook, color, f"Assets/Rook{color.capitalize()}.png", [x, y], self.screen))
            ChessData.update_get_castling_side("")
            self.castling_sound.play()

    def handle_removed_pieces(self):
        if ChessData.get_removed_piece():
            for removed_piece in ChessData.get_removed_piece():
                self.chessboard.remove_piece(removed_piece)
            self.piece_capture_sound.play()
            ChessData.update_removed_piece("")
            ChessData.update_active_piece("")

    def handle_promotion(self):
        if ChessData.get_promotion_piece():
            self.menu_over = False
            while not self.menu_over:
                pygame.display.flip()
                self.display_promotion_menu()
                location, piece = ChessData.get_promotion_piece()
                x, y = map(int, location)
                x, y = x * 100 + 20, y * 77.5 + 107.5
                color = 'white' if 'white' in piece else 'black'
                # if ChessData.get_bot():
                #     color = 'white' if color == 'black' else 'white'
                self.chessboard.remove_piece(piece)
                promoted_piece_name = None
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.menu_over = True
                        self.game_over = True
                        self.running = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        promoted_piece_name = self.check_promotion_selection(mouse_pos, color, x, y)
                if promoted_piece_name:
                    self.promotion_sound.play()
                    temp_chessboard = ChessData.get_chess_board().copy()
                    temp_chessboard[int((x - 20) / 100)][int((y - 107.5) / 77.5)] = promoted_piece_name
                    ChessData.board_history.change_promotion(promoted_piece_name[6])
                    ChessData.moves_made[-1]=ChessData.moves_made[-1]+promoted_piece_name[6]
                    ChessData.update_chess_board(temp_chessboard)

    def display_promotion_menu(self):
        main_menu = pygame.image.load("Assets/wooden_board.png").convert_alpha()
        main_menu = pygame.transform.scale(main_menu, (300, 380))
        self.screen.blit(main_menu, (270, 162.5))
        font = pygame.font.Font(None, 40)
        promotion_text = "Promotion: "
        game_over_text = font.render(promotion_text, True, (0, 0, 0))
        self.screen.blit(game_over_text, (345, 200))
        self.chessboard.display_sub_menu(self.screen, image_path="Assets/Asset 9@4x.png", text="Queen", size=(150, 50), position=(345, 240))
        self.chessboard.display_sub_menu(self.screen, image_path="Assets/Asset 9@4x.png", text="Rook", size=(150, 50), position=(345, 305))
        self.chessboard.display_sub_menu(self.screen, image_path="Assets/Asset 9@4x.png", text="Bishop", size=(150, 50), position=(345, 370))
        self.chessboard.display_sub_menu(self.screen, image_path="Assets/Asset 9@4x.png", text="Knight", size=(150, 50), position=(345, 435))

    def check_promotion_selection(self, mouse_pos, color, x, y):
        promoted_piece_name = None
        if 345 <= mouse_pos[0] <= 495:
            if 220 <= mouse_pos[1] <= 290:
                self.menu_over = True
                ChessData.update_promotion_piece(None, '')
                promoted_piece_name = self.promote_piece(color, "queen", x, y)
            elif 305 <= mouse_pos[1] <= 355:
                self.menu_over = True
                ChessData.update_promotion_piece(None, '')
                promoted_piece_name = self.promote_piece(color, "rook", x, y)
            elif 370 <= mouse_pos[1] <= 420:
                self.menu_over = True
                ChessData.update_promotion_piece(None, '')
                promoted_piece_name = self.promote_piece(color, "bishop", x, y)
            elif 435 <= mouse_pos[1] <= 485:
                self.menu_over = True
                ChessData.update_promotion_piece(None, '')
                promoted_piece_name = self.promote_piece(color, "knight", x, y)
        return promoted_piece_name

    def promote_piece(self, color, piece_type, x, y):
        self.piece_count[f'{color}_{piece_type}'] += 1
        promoted_piece_name = f"{color}_{piece_type}{self.piece_count[f'{color}_{piece_type}']}"
        self.chessboard.add_piece(ChessPiece(promoted_piece_name, color, f"Assets/{piece_type.capitalize()}{color.capitalize()}.png", [x, y], self.screen))
        return promoted_piece_name  # Limit to 60 frames per second
        
        
    def game_over_menu(self):

        while(not self.menu_over):
            pygame.display.flip()
            game_over_menu = pygame.image.load("Assets/wooden_board.png").convert_alpha()  # Use your own marker image here
            game_over_menu = pygame.transform.scale(game_over_menu, (300, 310)) 
            self.screen.blit(game_over_menu, (270, 162.5))
            font = pygame.font.Font(None, 40)  # Use default font and set size
            winner_text = "Black Wins!" if ChessData.get_chess_turn() == "white" else "White Wins!"
            if self.stalemate:
                winner_text = 'Stalemate!'
            game_over_text = font.render(winner_text, True, (0, 0, 0))  # Black text
            self.screen.blit(game_over_text, (335, 200))
            self.chessboard.display_sub_menu(self.screen,image_path="Assets/Asset 9@4x.png",text="Restart",size=(150, 50),position=(345, 240))
            self.chessboard.display_sub_menu(self.screen,image_path="Assets/Asset 9@4x.png",text="Main Menu",size=(150, 50),position=(345, 305))
            self.chessboard.display_sub_menu(self.screen,image_path="Assets/Asset 9@4x.png",text="Quit",size=(150, 50),position=(345, 370))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                    self.running = False
                    self.menu_over = True
                    pygame.mixer.stop()
                    pygame.mixer.quit()
                    pygame.quit() 
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()  # Get the current mouse position
            
            # Check if the mouse is over the submenu
                    #Restart
                    if (345 <= mouse_pos[0] <= 345 + 150 and 240 <= mouse_pos[1] <= 240 + 50):  # Change these values based on your submenu position and size
                        self.running = True
                        self.menu_over = True
                        self.main_menu = False
                        ChessData.new_game()
                        ChessData.board_reset()
                        ChessData.board_history.reset()
                        ChessData.moves_made_reset()
                        ChessData.update_suggested_moves(None)
                        ChessData.reset_removed_list()
                        for piece in ChessData.get_chess_board().flatten():
                            if piece != '.':
                                self.chessboard.remove_piece(piece)
                        self.initialize_pieces()


                    
                    #Main Menu
                    elif (345 <= mouse_pos[0] <= 345 + 150 and 305 <= mouse_pos[1] <= 305 + 50):
                        self.main_menu = True
                        ChessData.new_game()
                        ChessData.board_reset()
                        ChessData.board_history.reset()
                        ChessData.moves_made_reset()
                        ChessData.update_suggested_moves(None)
                        ChessData.reset_removed_list()
                        ChessData.update_multiplayer_flag(False)
                        self.client.disconnect_from_server()
                        self.chessboard.remove_piece('white_king')
                        for piece in ChessData.get_chess_board().flatten():
                            if piece != '.':
                                self.chessboard.remove_piece(piece)
                        self.menu_over=True
                        self.game_over = False  # Exit game over state
                        self.running = False
                        pygame.display.flip()

                    #Quit
                    elif (345 <= mouse_pos[0] <= 345 + 150 and 370 <= mouse_pos[1] <= 370 + 50):
                        self.menu_over=True
                        self.game_over = True  # Exit game over state
                        self.running = False  # Stop the main loop
                        pygame.mixer.stop()  # Stop all sounds
                        pygame.mixer.quit()  # Quit the mixer
                        pygame.quit()  # Quit Pygame

    def menu(self):
        while(not self.menu_over):
            pygame.display.flip()
            main_menu = pygame.image.load("Assets/wooden_board.png").convert_alpha()  # Use your own marker image here
            main_menu = pygame.transform.scale(main_menu, (300, 310)) 
            self.screen.blit(main_menu, (270, 162.5))
            font = pygame.font.Font(None, 40)  # Use default font and set size
            winner_text = "Main Menu" 
            game_over_text = font.render(winner_text, True, (0, 0, 0))  # Black text
            self.screen.blit(game_over_text, (345, 200))
            self.chessboard.display_sub_menu(self.screen,image_path="Assets/Asset 9@4x.png",text="Singleplayer",size=(150, 50),position=(345, 240))
            self.chessboard.display_sub_menu(self.screen,image_path="Assets/Asset 9@4x.png",text="Multiplayer",size=(150, 50),position=(345, 305))
            self.chessboard.display_sub_menu(self.screen,image_path="Assets/Asset 9@4x.png",text="Quit",size=(150, 50),position=(345, 370))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                    self.running = False 
                    self.menu_over = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()  # Get the current mouse position
            
            # Check if the mouse is over the submenu
                    if (345 <= mouse_pos[0] <= 345 + 150 and 220 <= mouse_pos[1] <= 240 + 50):  # Change these values based on your submenu position and size
                        self.running = True
                        ChessData.new_game()
                        self.menu_over=True
                        self.singleplayer=True
                        self.choose_difficulty = True
                        self.piece_count= {'black_queen':1,'black_bishop':2,'black_knight':2,'black_rook':2,'white_queen':1,'white_bishop':2,'white_knight':2,'white_rook':2}
                        

                    if (345 <= mouse_pos[0] <= 345 + 150 and 305 <= mouse_pos[1] <= 305 + 50):  # Change these values based on your submenu position and size
                        self.running = True
                        ChessData.new_game()
                        self.menu_over=True
                        self.singleplayer=False
                        ChessData.update_multiplayer_flag(True)
                        self.piece_count= {'black_queen':1,'black_bishop':2,'black_knight':2,'black_rook':2,'white_queen':1,'white_bishop':2,'white_knight':2,'white_rook':2}
                        self.client.connect_to_server('https://chessserver-jnhk.onrender.com')
                        # Keep the client running


                    elif (345 <= mouse_pos[0] <= 345 + 150 and 350 <= mouse_pos[1] <= 370 + 50):
                        self.menu_over=True
                        self.game_over = True  # Exit game over state
                        self.running = False  # Stop the main loop
                        pygame.mixer.stop()  # Stop all sounds
                        pygame.mixer.quit()  # Quit the mixer
                        pygame.quit()  # Quit Pygame

    def choose_difficulty_menu(self):
        if self.main_menu:
            self.menu_over=False
        while(not self.menu_over):
            pygame.display.flip()
            main_menu = pygame.image.load("Assets/wooden_board.png").convert_alpha()  # Use your own marker image here
            main_menu = pygame.transform.scale(main_menu, (300, 310)) 
            self.screen.blit(main_menu, (270, 162.5))
            font = pygame.font.Font(None, 40)  # Use default font and set size
            winner_text = "Single Player" 
            game_over_text = font.render(winner_text, True, (0, 0, 0))  # Black text
            self.screen.blit(game_over_text, (345, 200))
            self.chessboard.display_sub_menu(self.screen,image_path="Assets/Asset 9@4x.png",text="Easy Bot",size=(150, 50),position=(345, 240))
            self.chessboard.display_sub_menu(self.screen,image_path="Assets/Asset 9@4x.png",text="Medium Bot",size=(150, 50),position=(345, 305))
            self.chessboard.display_sub_menu(self.screen,image_path="Assets/Asset 9@4x.png",text="Hard Bot",size=(150, 50),position=(345, 370))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                    self.running = False 
                    self.menu_over = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()  # Get the current mouse position
            
            # Check if the mouse is over the submenu
                    if (345 <= mouse_pos[0] <= 345 + 150 and 220 <= mouse_pos[1] <= 240 + 50):  # Change these values based on your submenu position and size
                        self.running = True
                        ChessData.new_game()
                        ChessData.board_reset()
                        self.menu_over=True
                        ChessData.update_bot_level("easy")

                    elif (345 <= mouse_pos[0] <= 345 + 150 and 220 <= mouse_pos[1] <= 305 + 50):  # Change these values based on your submenu position and size
                        self.running = True
                        ChessData.new_game()
                        ChessData.board_reset()
                        self.menu_over=True
                        ChessData.update_bot_level("medium")

                    elif (345 <= mouse_pos[0] <= 345 + 150 and 350 <= mouse_pos[1] <= 370 + 50):
                        self.running = True
                        ChessData.new_game()
                        ChessData.board_reset()
                        self.menu_over=True
                        ChessData.update_bot_level("hard")                  

    def handle_side_menu(self):
        
        self.chessboard.display_sub_menu(self.screen, image_path="Assets/redo.png", text="", size=(50, 50), position=(645, 25))
        self.chessboard.display_sub_menu(self.screen, image_path="Assets/menu.png", text="", size=(50, 50), position=(715, 25))
        self.chessboard.display_sub_menu(self.screen, image_path="Assets/suggestion.png", text="", size=(55, 50), position=(575, 25))

    def handle_side_menu_options(self,mouse_pos):
        if 645 <= mouse_pos[0] <= 695 and 25 <= mouse_pos[1] <= 75 and ChessData.board_history.get_undo_state():
            ChessData.handle_removed_pieces_pixels(ChessData.get_current_state()['removed'],False)
            new_chessboard = np.copy(ChessData.get_chess_board())
            old_x,old_y=ChessData.get_current_state()['old']
            new_x,new_y=ChessData.get_current_state()['new']
            new_chessboard[old_x][old_y] = ChessData.get_current_state()['piece']
            ChessData.update_enpassant_count('+')
            ChessData.update_enpassant_count('+')
            ChessData.moves_made = ChessData.moves_made[:-1]
            if ChessData.get_current_state()['promotion']:
                x,y = ChessData.get_current_state()['promotion'][0][0],ChessData.get_current_state()['promotion'][0][1]
                self.chessboard.remove_piece(new_chessboard[x][y])
                new_chessboard[x][y] = '.'   
            new_chessboard[new_x][new_y] = ChessData.get_current_state()['removed']    
            if ChessData.get_current_state()['castle']=='left':
                rook_piece = ChessData.get_current_state()['piece'][:5] + "_rook1"
                self.chessboard.remove_piece(rook_piece)
                new_chessboard[0][old_y] = rook_piece
                new_chessboard[3][old_y] = "."
                self.chessboard.add_piece(ChessPiece(rook_piece, ChessData.get_current_state()['piece'][:5], f"Assets/Rook{ChessData.get_current_state()['piece'][:5].capitalize()}.png", [0 * 100 + 20, 107.5 + old_y * 77.5], self.screen))
            if ChessData.get_current_state()['castle']=='right':
                rook_piece = ChessData.get_current_state()['piece'][:5] + "_rook2"
                self.chessboard.remove_piece(rook_piece)
                new_chessboard[7][old_y] = rook_piece
                new_chessboard[5][old_y] = "."
                self.chessboard.add_piece(ChessPiece(rook_piece, ChessData.get_current_state()['piece'][:5], f"Assets/Rook{ChessData.get_current_state()['piece'][:5].capitalize()}.png", [7 * 100 + 20, 107.5 + old_y * 77.5], self.screen))   
            if new_chessboard[new_x][new_y] != ".":
                self.chessboard.add_piece(ChessPiece(ChessData.get_current_state()['removed'], ChessData.get_current_state()['removed'][:5], f"Assets/{ChessData.get_current_state()['removed'][6:-1].capitalize() + ChessData.get_current_state()['removed'][:5].capitalize()}.png", [new_x * 100 + 20, 107.5 + new_y * 77.5], self.screen))
            if ChessData.get_current_state()['enpassant']:
                sign = -1 if ChessData.get_current_state()['piece'][:5] == 'white' else 1
                new_chessboard[new_x][new_y + sign] = new_chessboard[new_x][new_y]
                new_chessboard[new_x][new_y] = '.'
            if ChessData.board_history.get_undo_state()['enpassant']:
                
                sign = -1 if ChessData.get_current_state()['piece'][:5] == 'white' else 1
                new_chessboard[new_x][new_y + sign] = new_chessboard[new_x][new_y]
                new_chessboard[new_x][new_y] = '.'
            ChessData.update_chess_board(new_chessboard)
            self.chessboard.remove_piece(ChessData.get_current_state()['piece'])
            image = ChessData.get_current_state()['piece'][6:-1].capitalize() 
            if 'king' in ChessData.get_current_state()['piece']:
                image = ChessData.get_current_state()['piece'][6:].capitalize() 
            image += ChessData.get_current_state()['piece'][:5].capitalize() 
            
            self.chessboard.add_piece(ChessPiece(ChessData.get_current_state()['piece'], ChessData.get_current_state()['piece'][:5], f"Assets/{image}.png", [old_x * 100 + 20, 107.5 + old_y * 77.5], self.screen))
            ChessData.undo()
            
            ChessData.update_enpassant_count('+')
            ChessData.moves_made = ChessData.moves_made[:-1]
            new_chessboard2 = np.copy(ChessData.get_chess_board())
            old_x2,old_y2=ChessData.get_current_state()['old']
            new_x2,new_y2=ChessData.get_current_state()['new']
            new_chessboard2[old_x2][old_y2] = ChessData.get_current_state()['piece']
            ChessData.update_enpassant_count('+')
            ChessData.update_enpassant_count('+')
            if ChessData.get_current_state()['promotion']:
                x2,y2 = ChessData.get_current_state()['promotion'][0][0],ChessData.get_current_state()['promotion'][0][1]
                self.chessboard.remove_piece(new_chessboard2[x2][y2])
                new_chessboard2[x2][y2] = '.'   
            new_chessboard2[new_x2][new_y2] = ChessData.get_current_state()['removed']    
            if ChessData.get_current_state()['castle']=='left':
                rook_piece2 = ChessData.get_current_state()['piece'][:5] + "_rook1"
                self.chessboard.remove_piece(rook_piece2)
                new_chessboard2[0][old_y2] = rook_piece2
                new_chessboard2[3][old_y2] = "."
                self.chessboard2.add_piece(ChessPiece(rook_piece2, ChessData.get_current_state()['piece'][:5], f"Assets/Rook{ChessData.get_current_state()['piece'][:5].capitalize()}.png", [0 * 100 + 20, 107.5 + old_y2 * 77.5], self.screen))
            if ChessData.get_current_state()['castle']=='right':
                rook_piece = ChessData.get_current_state()['piece'][:5] + "_rook2"
                self.chessboard.remove_piece(rook_piece2)
                new_chessboard2[7][old_y2] = rook_piece2
                new_chessboard2[5][old_y2] = "."
                self.chessboard.add_piece(ChessPiece(rook_piece2, ChessData.get_current_state()['piece'][:5], f"Assets/Rook{ChessData.get_current_state()['piece'][:5].capitalize()}.png", [7 * 100 + 20, 107.5 + old_y2 * 77.5], self.screen))   
            if ChessData.get_current_state()['enpassant']:
                sign = 1 if ChessData.get_current_state()['piece'][:5] == 'white' else -1
                new_chessboard2[new_x2][new_y2 + sign] = new_chessboard[new_x2][new_y2]
                new_chessboard2[new_x2][new_y2] = '.'
                new_y2=new_y2+sign
            if new_chessboard2[new_x2][new_y2] != ".":
                self.chessboard.add_piece(ChessPiece(ChessData.get_current_state()['removed'], ChessData.get_current_state()['removed'][:5], f"Assets/{ChessData.get_current_state()['removed'][6:-1].capitalize() + ChessData.get_current_state()['removed'][:5].capitalize()}.png", [new_x2 * 100 + 20, 107.5 + new_y2 * 77.5], self.screen)) 
            ChessData.handle_removed_pieces_pixels(ChessData.get_current_state()['removed'],False)
            ChessData.update_chess_board(new_chessboard2)
            self.chessboard.remove_piece(ChessData.get_current_state()['piece'])
            image2 = ChessData.get_current_state()['piece'][6:-1].capitalize() 
            if 'king' in ChessData.get_current_state()['piece']:
                image2 = ChessData.get_current_state()['piece'][6:].capitalize() 
            image2 += ChessData.get_current_state()['piece'][:5].capitalize() 
            self.chessboard.add_piece(ChessPiece(ChessData.get_current_state()['piece'], ChessData.get_current_state()['piece'][:5], f"Assets/{image2}.png", [old_x2 * 100 + 20, 107.5 + old_y2 * 77.5], self.screen))
            ChessData.undo()
        if 715 <= mouse_pos[0] <= 765 and 25 <= mouse_pos[1] <= 75:
            self.handle_pause_menu()
        if 575 <= mouse_pos[0] <= 630 and 25 <= mouse_pos[1] <= 75:
            # ChessData.suggestion()
            self.stockfish.set_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
            self.stockfish.make_moves_from_current_position(ChessData.get_moves_made())
            ChessData.update_suggested_moves(self.stockfish.get_best_move())
    
    def handle_previous_move(self):
        if ChessData.get_current_state():
            previous_move = ChessData.get_current_state()['old'].copy()
            new_move = ChessData.get_current_state()['new'].copy()
            if ChessData.get_game_color() == ChessData.get_chess_turn() and ChessData.get_multiplayer_flag():
                previous_move = [previous_move[0] * 100 , (7-previous_move[1]) * 77.5 + 100]
                new_move = [new_move[0] * 100 , (7-new_move[1]) * 77.5 + 100]
            else:
                previous_move = [previous_move[0] * 100 , previous_move[1] * 77.5 + 100]
                new_move = [new_move[0] * 100 , new_move[1] * 77.5 + 100]
            self.screen.blit(self.prev_move_marker, (previous_move[0], previous_move[1]))
            self.screen.blit(self.prev_move_marker, (new_move[0], new_move[1]))

    def handle_suggested_move(self):
        if ChessData.get_suggested_moves():
            suggested_move = ChessData.get_suggested_moves()
            new_suggested_move = suggested_move[0]
            old_suggested_move = suggested_move[1]
            new_suggested_move = [new_suggested_move[0] * 100 , new_suggested_move[1] * 77.5 + 100]
            old_suggested_move = [old_suggested_move[0] * 100 , old_suggested_move[1] * 77.5 + 100]
            self.screen.blit(self.suggested_move_marker, (new_suggested_move[0], new_suggested_move[1]))
            self.screen.blit(self.suggested_move_marker, (old_suggested_move[0], old_suggested_move[1]))

    def handle_pause_menu(self):
        self.menu_over = False
        while not self.menu_over:
            pygame.display.flip()
            game_over_menu = pygame.image.load("Assets/wooden_board.png").convert_alpha()  # Use your own marker image here
            game_over_menu = pygame.transform.scale(game_over_menu, (300, 410)) 
            self.screen.blit(game_over_menu, (270, 162.5))

            font = pygame.font.Font(None, 40)  # Use default font and set size
            winner_text = "Paused!" 
            game_over_text = font.render(winner_text, True, (0, 0, 0))  # Black text
            self.screen.blit(game_over_text, (360, 200))

            self.chessboard.display_sub_menu(self.screen,image_path="Assets/Asset 9@4x.png",text="Resume",size=(150, 50),position=(345, 255))
            self.chessboard.display_sub_menu(self.screen,image_path="Assets/Asset 9@4x.png",text="Restart",size=(150, 50),position=(345, 320))
            self.chessboard.display_sub_menu(self.screen,image_path="Assets/Asset 9@4x.png",text="Main Menu",size=(150, 50),position=(345, 385))
            self.chessboard.display_sub_menu(self.screen,image_path="Assets/Asset 9@4x.png",text="Quit",size=(150, 50),position=(345, 450))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                    self.running = False
                    self.menu_over = True
                    pygame.mixer.stop()
                    pygame.mixer.quit()
                    pygame.quit() 
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()  # Get the current mouse position
            
            # Check if the mouse is over the submenu
                    #Resume
                    if (345 <= mouse_pos[0] <= 345 + 150 and 255 <= mouse_pos[1] <= 255 + 50):  # Change these values based on your submenu position and size
                        self.running = True
                        self.menu_over=True

                    #Restart
                    if (345 <= mouse_pos[0] <= 345 + 150 and 320 <= mouse_pos[1] <= 320 + 50):  # Change these values based on your submenu position and size
                        self.running = True
                        self.main_menu = False
                        ChessData.new_game()
                        ChessData.board_reset()
                        ChessData.board_history.reset()
                        ChessData.moves_made_reset()
                        ChessData.update_suggested_moves(None)
                        ChessData.reset_removed_list()
                        for piece in ChessData.get_chess_board().flatten():
                            if piece != '.':
                                self.chessboard.remove_piece(piece)
                        self.initialize_pieces()

                        
                        self.stockfish = Stockfish(path="stockfish/stockfish-windows-x86-64-avx2.exe")
                        self.menu_over=True
                        
                    #Main Menu
                    elif (345 <= mouse_pos[0] <= 345 + 150 and 385 <= mouse_pos[1] <= 385 + 50):
                        self.main_menu = True
                        ChessData.new_game()
                        ChessData.board_reset()
                        ChessData.board_history.reset()
                        ChessData.moves_made_reset()
                        ChessData.update_suggested_moves(None)
                        ChessData.reset_removed_list()
                        ChessData.update_multiplayer_flag(False)
                        self.client.disconnect_from_server()
                        for piece in ChessData.get_chess_board().flatten():
                            if piece != '.':
                                self.chessboard.remove_piece(piece)
                        self.menu_over=True
                        self.game_over = False  # Exit game over state
                        self.running = False
                        
                    #Quit
                    elif (345 <= mouse_pos[0] <= 345 + 150 and 450 <= mouse_pos[1] <= 450 + 50):
                        self.menu_over=True
                        self.game_over = True  # Exit game over state
                        self.running = False  # Stop the main loop

    def check_game_over(self):
        chessboard = ChessData.get_chess_board()
        moves_count = 0 
        
        for piece in ChessData.get_chess_board().flatten():
            if piece and ChessData.get_chess_turn() in piece:  # Ensure piece is not empty
                possible_moves = ChessPiece.get_possible_moves(piece, chessboard)
                if get_moves(possible_moves, piece):
                    moves_count +=1

        if moves_count == 0:
            if is_piece_in_check(ChessData.get_chess_turn(),ChessData.get_chess_board(),np.argwhere(ChessData.get_chess_board() == f'{ChessData.get_chess_turn()}_king')):
                self.stalemate = False          
                print('checkmate')
            else:
                self.stalemate = True
                print('stalemate')
            self.menu_over= False
            self.game_over = False # Exit game over state
            self.running = False  # Stop the main loop
        else:
            piece_values = {
                "bishop": 3,
                "knight": 3,
            }
            white_eval = 0
            black_eval = 0
            for x in range(8):
                for y in range(8):
                    piece = chessboard[x, y]
                    if piece != ".":
                        # If there is a queen, rook, or pawn, return immediately
                        if 'queen' in piece or 'rook' in piece or 'pawn' in piece:
                            return True  

                        # Accumulate piece values
                        value = next((v for k, v in piece_values.items() if k in piece), 0)
                        if "white" in piece:
                            white_eval += value
                        else:
                            black_eval += value
                        
                        # If either side has enough material, return True
                        if white_eval >= 5 or black_eval >= 5:
                            return True  
            self.stalemate = True
            self.menu_over= False
            self.game_over = False # Exit game over state
            self.running = False  
            return False 
                    
                        

    
    def show_removed_pieces(self):
        white,black = ChessData.get_removed_list()
        place = [7.5,727.5]
        if ChessData.get_game_color() == 'black':
            place = [727.5, 7.5]
        for count,piece in enumerate(white):
            name = re.search(r'_([A-Za-z]+)', piece).group(1).capitalize()
            piece_img = pygame.image.load(f"Assets/{name}White.png").convert_alpha()  # Use your own marker image here
            piece_img = pygame.transform.scale(piece_img, (60, 60)) 
            if name != 'Rook':
                self.screen.blit(piece_img, (20+30*count, place[0]))
            else:
                self.screen.blit(piece_img, (20+30*count, place[0]+5))
        for count,piece in enumerate(black):
            name = re.search(r'_([A-Za-z]+)', piece).group(1).capitalize()
            piece_img = pygame.image.load(f"Assets/{name}Black.png").convert_alpha()  # Use your own marker image here
            piece_img = pygame.transform.scale(piece_img, (60, 60)) 
            if piece != 'Rook':
                self.screen.blit(piece_img, (20+30*count, place[1]))
            else:
                self.screen.blit(piece_img, (20+30*count, place[1]+5))

def minmax_algorithm(chessboard, depth, is_maximizing_player, alpha, beta):
    if depth == 0 or not ChessData.get_game():
        return evaluate_board(chessboard)

    color = "black" if is_maximizing_player else "white"
    pieces_positions = {
        (x, y): chessboard[x, y]
        for x, y in zip(*np.where(chessboard != "."))
        if color in str(chessboard[x, y])
    }

    if is_maximizing_player:
        max_eval = float('-inf')
        for (old_x, old_y), piece in pieces_positions.items():
            possible_moves = get_moves(ChessPiece.get_possible_moves(piece, chessboard), piece)
            for new_x, new_y in possible_moves:
                new_x, new_y = int(new_x), int(new_y)
                original_target = chessboard[new_x, new_y]
                chessboard[new_x, new_y], chessboard[old_x, old_y] = piece, "."
                eval = minmax_algorithm(chessboard, depth - 1, False, alpha, beta)
                chessboard[new_x, new_y], chessboard[old_x, old_y] = original_target, piece
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return max_eval
    else:
        min_eval = float('inf')
        for (old_x, old_y), piece in pieces_positions.items():
            possible_moves = get_moves(ChessPiece.get_possible_moves(piece, chessboard), piece)
            for new_x, new_y in possible_moves:
                new_x, new_y = int(new_x), int(new_y)
                original_target = chessboard[new_x, new_y]
                chessboard[new_x, new_y], chessboard[old_x, old_y] = piece, "."
                eval = minmax_algorithm(chessboard, depth - 1, True, alpha, beta)
                chessboard[new_x, new_y], chessboard[old_x, old_y] = original_target, piece
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return min_eval

def evaluate_board(chessboard):
    piece_values = {
        "king": 1000,
        "queen": 9,
        "rook": 5,
        "bishop": 3,
        "knight": 3,
        "pawn": 1
    }
    evaluation = 0
    for x in range(8):
        for y in range(8):
            piece = chessboard[x, y]
            if piece != ".":
                value = next((v for k, v in piece_values.items() if k in piece), 0)
                evaluation += value if "black" in piece else -value
    return evaluation

def easy_bot_algorithm(depth):
    chessboard = ChessData.get_chess_board()
    best_move = None
    best_value = float('-inf')
    color = "black"
    pieces_positions = {
        (x, y): chessboard[x, y]
        for x, y in zip(*np.where(chessboard != "."))
        if color in str(chessboard[x, y])
    }

    positive_moves = []

    for (old_x, old_y), piece in pieces_positions.items():
        possible_moves = get_moves(ChessPiece.get_possible_moves(piece, chessboard), piece)
        for new_x, new_y in possible_moves:
            new_x, new_y = int(new_x), int(new_y)
            original_target = chessboard[new_x, new_y]
            chessboard[new_x, new_y], chessboard[old_x, old_y] = piece, "."
            move_value = minmax_algorithm(chessboard, depth - 1, False, float('-inf'), float('inf'))
            chessboard[new_x, new_y], chessboard[old_x, old_y] = original_target, piece
            if move_value >= 0:
                positive_moves.append(((new_x, new_y), piece, move_value))
            if move_value > best_value:
                best_value = move_value
                best_move = ((new_x, new_y), piece)
    if positive_moves and best_value==0:
        best_move = random.choice(positive_moves)[:2]
    return best_move if best_move else None

def get_moves(possible_moves, piece):
    removed_king_in_check = []
    current_chessboard = ChessData.get_chess_board()
    old_x, old_y = np.argwhere(current_chessboard == piece)[0]

    for moves in possible_moves:
        new_x, new_y = map(int, moves)
        original_target = current_chessboard[new_x][new_y]
        original_source = current_chessboard[old_x][old_y]
        current_chessboard[new_x][new_y] = piece
        current_chessboard[old_x][old_y] = "."

        king_location = np.argwhere(current_chessboard == (ChessData.get_chess_turn() + "_king"))[0]
        if not is_piece_in_check(ChessData.get_chess_turn(), current_chessboard, king_location):
            removed_king_in_check.append((new_x, new_y))

        current_chessboard[new_x][new_y] = original_target
        current_chessboard[old_x][old_y] = original_source

    outline_moves = removed_king_in_check
    king_location = np.argwhere(ChessData.get_chess_board() == (ChessData.get_chess_turn() + "_king"))[0]
    if piece == ChessData.get_chess_turn() + "_king" and not ChessData.get_has_piece_moved(piece) and not is_piece_in_check(ChessData.get_chess_turn(), ChessData.get_chess_board(), king_location):
        y = 7 if ChessData.get_chess_turn() == "white" else 0
        if ChessPiece.is_right_castling_available() and ChessData.get_chess_board()[5][y] == "." and ChessData.get_chess_board()[6][y] == ".":
            outline_moves.append((6, y))
        if ChessPiece.is_left_castling_available() and ChessData.get_chess_board()[3][y] == "." and ChessData.get_chess_board()[2][y] == "." and ChessData.get_chess_board()[1][y] == ".":
            outline_moves.append((2, y))

    return outline_moves

