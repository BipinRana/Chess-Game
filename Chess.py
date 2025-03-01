from GameController import GameController

if __name__ == "__main__":
    game = GameController()
      # Initializes the chess pieces
    while True:
        game.menu()
        if game.game_over:
            break
        elif game.choose_difficulty :
            game.choose_difficulty_menu()
            if game.game_over:
                break
        
        game.initialize_pieces()
        game.run()  # Start the game loop
        game.game_over_menu()
        if game.main_menu:
            game.menu_over = False
        if game.game_over:
            break
