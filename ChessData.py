import numpy as np
from Node import ChessHistory
class ChessData:
    bot=""
    game=True
    outline_flag = False
    chess_turn="white"
    active_piece = ""
    outline_moves = []
    chess_board = np.array([
        ['black_rook1', 'black_pawn1', '.', '.', '.', '.', 'white_pawn1', 'white_rook1'],
        ['black_knight1', 'black_pawn2', '.', '.', '.', '.', 'white_pawn2', 'white_knight1'],
        ['black_bishop1', 'black_pawn3', '.', '.', '.', '.', 'white_pawn3', 'white_bishop1'],
        ['black_queen1', 'black_pawn4', '.', '.', '.', '.', 'white_pawn4', 'white_queen1'],
        ['black_king', 'black_pawn5', '.', '.', '.', '.', 'white_pawn5', 'white_king'],
        ['black_bishop2', 'black_pawn6', '.', '.', '.', '.', 'white_pawn6', 'white_bishop2'],
        ['black_knight2', 'black_pawn7', '.', '.', '.', '.', 'white_pawn7', 'white_knight2'],
        ['black_rook2', 'black_pawn8', '.', '.', '.', '.', 'white_pawn8', 'white_rook2']
    ])
    starting_chess_board=np.array([
        ['black_rook1', 'black_pawn1', '.', '.', '.', '.', 'white_pawn1', 'white_rook1'],
        ['black_knight1', 'black_pawn2', '.', '.', '.', '.', 'white_pawn2', 'white_knight1'],
        ['black_bishop1', 'black_pawn3', '.', '.', '.', '.', 'white_pawn3', 'white_bishop1'],
        ['black_queen1', 'black_pawn4', '.', '.', '.', '.', 'white_pawn4', 'white_queen1'],
        ['black_king', 'black_pawn5', '.', '.', '.', '.', 'white_pawn5', 'white_king'],
        ['black_bishop2', 'black_pawn6', '.', '.', '.', '.', 'white_pawn6', 'white_bishop2'],
        ['black_knight2', 'black_pawn7', '.', '.', '.', '.', 'white_pawn7', 'white_knight2'],
        ['black_rook2', 'black_pawn8', '.', '.', '.', '.', 'white_pawn8', 'white_rook2']
    ])
    move_sound=False
    removed_pieces = []
    dragging_flag=False
    castle=""
    has_piece_moved={'black_king':False,'white_king':False,'black_rook2':False,'black_rook1':False,'white_rook1':False,'white_rook2':False}
    player_color=""
    bot_move=[]
    bot_piece=""
    promotion_piece=''
    promotion_location=[]
    en_passant_moves = {'initial': None, 'final': None, 'color': None,'enpassant':False,'count':0}
    en_passant_turn = ''
    board_history = ChessHistory()
    moves_made = []
    dict_x = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h', 'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    old = []
    new = []
    show_suggested_moves = False
    white_removed = []
    black_removed = []
    multiplayer = False
    multiplayer_move = False
    opp_move={}
    game_color='white'

    @classmethod
    def get_chess_board(cls):
        return cls.chess_board

    @classmethod
    def get_outline_flag(cls):
        return cls.outline_flag

    @classmethod
    def true_outline_flag(cls):
        cls.outline_flag = True  # Toggle the outline flag

    @classmethod
    def false_outline_flag(cls):
        cls.outline_flag = False  # Toggle the outline flag

    @classmethod
    def update_chess_board(cls, new_chess_board):
        cls.chess_board = new_chess_board  # Update the chess board with a new one

    @classmethod
    def get_outline_moves(cls):
        return cls.outline_moves
    
    @classmethod
    def update_outline_moves(cls,new_outline_moves):
        cls.outline_moves= new_outline_moves

    @classmethod
    def get_active_piece(cls):
        return cls.active_piece
    
    @classmethod
    def update_active_piece(cls,new_piece):
        cls.active_piece= new_piece

    @classmethod
    def get_chess_turn(cls):
        return cls.chess_turn
    
    @classmethod
    def update_chess_turn(cls):
        if cls.chess_turn=="white":
            cls.chess_turn="black"
        elif cls.chess_turn=="black": 
            cls.chess_turn="white"

    @classmethod
    def get_removed_piece(cls):
        return cls.removed_pieces
    
    @classmethod
    def update_removed_piece(cls,new_removed_piece):
        if new_removed_piece != '':
            cls.removed_pieces.append(new_removed_piece)
        else:
            cls.removed_pieces = []

    
    @classmethod
    def get_move_sound(cls):
        return cls.move_sound
    
    @classmethod
    def update_move_sound(cls,move_sound_logic):
        cls.move_sound=move_sound_logic

    @classmethod
    def get_dragging_flag(cls):
        return cls.dragging_flag
    
    @classmethod
    def update_dragging_flag(cls,flag_option):
        cls.dragging_flag=flag_option

    @classmethod
    def game_over(cls):
        cls.game=False

    @classmethod
    def get_game(cls):
        return cls.game
    
    @classmethod
    def new_game(cls):
        cls.game =True
    

    
    @classmethod
    def get_has_piece_moved(cls,piece):
        return cls.has_piece_moved[piece]
    
    @classmethod
    def update_has_piece_moved(cls,piece):
        if piece in cls.has_piece_moved:
            cls.has_piece_moved[piece]=True
    @classmethod
    def get_castling_side(cls):
        return cls.castle
    
    @classmethod
    def update_get_castling_side(cls,castle_side):
        cls.castle=castle_side

    @classmethod
    def board_reset(cls):
        cls.chess_board = cls.starting_chess_board.copy()
        cls.chess_turn="white"
        cls.active_piece = ""
        cls.castle=""
        cls.has_piece_moved={'black_king':False,'white_king':False,'black_rook2':False,'black_rook1':False,'white_rook1':False,'white_rook2':False}
    
    @classmethod
    def get_player_color(cls):
        return cls.player_color
    
    @classmethod
    def update_player_color(cls,color):
        cls.player_color=color

    @classmethod
    def get_bot(cls):
        return cls.bot
    
    @classmethod
    def update_bot_level(cls,level):
        cls.bot=level
    
    @classmethod
    def get_bot_move(cls):
        if cls.bot_piece != "" :
            return cls.bot_move,cls.bot_piece
        else:
            return False
    
    @classmethod
    def update_bot_move(cls,move,piece):
        cls.bot_move=move
        cls.bot_piece=piece
        
    @classmethod
    def get_promotion_piece(cls):
        if cls.promotion_piece != "" :
            return cls.promotion_location,cls.promotion_piece
        else:
            return False
    
    @classmethod
    def update_promotion_piece(cls,location,piece):
        cls.promotion_piece = piece
        cls.promotion_location = location
    
    @classmethod
    def update_en_passant_piece(cls, x, y):
        if x != -1 and y != -1:
            if ChessData.get_chess_turn() == "white":
                initial_positions = []
                if x > 1 and "black_pawn" in ChessData.chess_board[x-1][y]:
                    initial_positions.append([x-1, y])  # Use list instead of np.array
                if x < 7 and "black_pawn" in ChessData.chess_board[x+1][y]:
                    initial_positions.append([x+1, y])  # Use list instead of np.array
                if initial_positions:
                    cls.en_passant_moves = {'initial': initial_positions, 'final': [x, y+1], 'color': 'black','count':2}  # Use list instead of np.array
            else:
                initial_positions = []
                if x > 1 and "white_pawn" in ChessData.chess_board[x-1][y]:
                    initial_positions.append([x-1, y])  # Use list instead of np.array
                if x < 7 and "white_pawn" in ChessData.chess_board[x+1][y]:
                    initial_positions.append([x+1, y])  # Use list instead of np.array
                if initial_positions:
                    cls.en_passant_moves = {'initial': initial_positions, 'final': [x, y-1], 'color': 'white','count':2}  # Use list instead of np.array
        else:
            cls.en_passant_moves = {'initial': None, 'final': None, 'color': None,'count':0}

    @classmethod
    def get_en_passant_piece(cls):
        if cls.en_passant_moves['initial'] is None:
            return False
        elif ChessData.get_chess_turn() == "white" and cls.en_passant_moves['color'] == "white" and cls.en_passant_moves['count']>0:
            return cls.en_passant_moves
        elif ChessData.get_chess_turn() == "black" and cls.en_passant_moves['color'] == "black" and cls.en_passant_moves['count']>0:
            return cls.en_passant_moves
        elif cls.en_passant_moves['count']==0:
            ChessData.update_en_passant_piece(-1,-1)
            return False
        
    @classmethod
    def update_enpassant_count(cls,sign):
        if(cls.en_passant_moves['count'] >0 and sign == '-'):
            cls.en_passant_moves['count']-=1
        elif sign == '+' and cls.en_passant_moves['count'] <2:
            cls.en_passant_moves['count']+=1
        elif cls.en_passant_moves['count'] == 0 or cls.en_passant_moves['count'] == 2:
            ChessData.update_en_passant_piece(-1,-1)

    @classmethod
    def add_moves_to_history(cls, state):
        cls.moves_made.append(f"{cls.dict_x[state['old'][0]]}{8-state['old'][1]}{cls.dict_x[state['new'][0]]}{8-state['new'][1]}")
        cls.board_history.add_state(state)

    @classmethod
    def get_current_state(cls):
        return cls.board_history.get_current_state()
    
    @classmethod
    def undo(cls):
        return cls.board_history.undo()
    
    @classmethod
    def redo(cls):
        return cls.board_history.redo()
    
    @classmethod
    def get_moves_made(cls):
        return cls.moves_made
    
    @classmethod
    def reset_moves_made(cls):
        cls.moves_made = []

    @classmethod
    def update_suggested_moves(cls,move):
        if move == None:
            cls.old = []
            cls.new = []
        else:
            cls.old,cls.new = cls.map_move(move)

    @classmethod
    def get_suggested_moves(cls):
        if cls.old == [] and cls.new == []:
            return False
        return cls.old, cls.new
    
    @classmethod
    def moves_made_reset(cls):
        cls.moves_made =[]


    @classmethod
    def map_move(cls,move):
        old_x = cls.dict_x[move[0]]
        old_y = 8-int(move[1])
        new_x = cls.dict_x[move[2]]
        new_y = 8-int(move[3])
        return [old_x, old_y],[new_x, new_y]

    @classmethod
    def handle_removed_pieces_pixels(cls,piece,command=True):
        if 'white' in piece: 
            if piece not in cls.white_removed and command:
                cls.white_removed+=[piece]
            else:
                cls.white_removed.remove(piece)

        if 'black' in piece: 
            if piece not in cls.black_removed:
                cls.black_removed+=[piece]
            else:
                cls.black_removed.remove(piece)
            

    @classmethod
    def get_removed_list(cls):
        return cls.white_removed, cls.black_removed
    
    @classmethod
    def reset_removed_list(cls):
        cls.white_removed=[]
        cls.black_removed=[]

    @classmethod
    def update_multiplayer_flag(cls,bool):
        cls.multiplayer = bool

    @classmethod
    def update_multiplayer_move_flag(cls,bool):
        cls.multiplayer_move = bool

    @classmethod
    def get_multiplayer_flag(cls):
        return cls.multiplayer

    @classmethod
    def get_multiplayer_move_flag(cls):
        return cls.multiplayer_move 
    
    @classmethod
    def update_opponent(cls,move):
        cls.opp_move = move

    @classmethod
    def get_opponent_response(cls):
        return cls.opp_move

    @classmethod
    def game_color_update(cls,color):
        cls.game_color = color

    @classmethod 
    def get_game_color(cls):
        return cls.game_color