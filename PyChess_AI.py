import pygame
import chess
import chess.svg
import cairosvg
import io
from stockfish import Stockfish

stockfish = Stockfish('stockfish/stockfish-windows-x86-64-avx2.exe')

# Define the chessboard size
WIDTH, HEIGHT = 640, 640

# Initialize Pygame and Pygame constants
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('PyChess AI')
font_RetroChild = pygame.font.Font('assets/fonts/RetroChildExtrude.ttf', 60) # Define font
font_Pixeloid = pygame.font.Font('assets/fonts/PixeloidSans.ttf', 20)
font_Pixeloid_big = pygame.font.Font('assets/fonts/PixeloidSans.ttf', 40)
timer = pygame.time.Clock()

# Initialize chessboard and define variables
board = chess.Board()
selected_square = None  # Track the selected square
lan_stack = []          # Long Algebraic Notation stack
move_count = 0          # counter for all moves played
game_state = 'menu'
games_archive_index = 0
editing = False

# Menu buttons
play_button = pygame.Rect(252.5, 225, 135, 50)
archives_button = pygame.Rect(232, 300, 176, 50)
left_button = pygame.Rect(20, 20, 50, 50)
right_button = pygame.Rect(250, 20, 50, 50)
archive_return_button = pygame.Rect(460, 20, 50, 50)
edit_button = pygame.Rect(520, 20, 50, 50)
delete_button = pygame.Rect(580, 20, 50, 50)
game_return_button = pygame.Rect(650, 20, 50, 50)

# load images
return_img = pygame.image.load('assets/images/return.png')
delete_img = pygame.image.load('assets/images/delete.png')
edit_img = pygame.image.load('assets/images/edit.png')


# load sounds for different moves
move_sound = pygame.mixer.Sound("assets/sound_effects/piece_move.mp3")
capture_sound = pygame.mixer.Sound("assets/sound_effects/capture.mp3")
check_sound = pygame.mixer.Sound("assets/sound_effects/check.mp3")
start_sound = pygame.mixer.Sound("assets/sound_effects/end.mp3")
pygame.mixer_music.load("assets/sound_effects/bgm.mp3")

def draw_menu():

    screen.fill('dark grey')
    # Draw menu buttons
    pygame.draw.rect(screen, 'light grey', play_button, 3, 15)
    pygame.draw.rect(screen, 'light grey', archives_button, 3, 15)
    pygame.draw.rect(screen, 'light grey', (200, 175, 240, 350), 2, 20)
    # Draw menu text
    title_text = font_RetroChild.render('PyChess AI', True, 'white')
    play_text = font_Pixeloid.render('Play Chess', True, 'white')
    archive_text = font_Pixeloid.render('Games Archive', True, 'white')

    screen.blit(title_text, (155, 100))
    screen.blit(play_text, (262.5, 237))
    screen.blit(archive_text, (242, 312))

# Draw the chessboard
def draw_board():
    screen.fill('dark grey')
    pygame.draw.rect(screen, 'light grey', game_return_button, 3, 15)
    screen.blit(return_img, (game_return_button.x + 10, game_return_button.y + 10))
    if selected_square is not None:

         # Create a dictionary for highlighting squares
        highlight_squares = {selected_square: '#68BC00'}  # Green for the selected square
         
         # Highlight possible moves in red
        for move in board.legal_moves:
            if move.from_square == selected_square:
                highlight_squares[move.to_square] = '#FF0000'  # Red for possible moves

        svg = chess.svg.board(board, size=640, fill=highlight_squares)
        png_io = io.BytesIO()
        cairosvg.svg2png(bytestring=bytes(svg, "utf8"), write_to=png_io)
        png_io.seek(0)

        board_img = pygame.image.load(png_io, "png")
        screen.blit(board_img, (0,0))
    else:
        svg = chess.svg.board(board, size=640)
        png_io = io.BytesIO()
        cairosvg.svg2png(bytestring=bytes(svg, "utf8"), write_to=png_io)
        png_io.seek(0)

        board_img = pygame.image.load(png_io, "png")
        screen.blit(board_img, (0,0))  

# Draws game over after checkmate or stalemate
def draw_game_over():
    result = board.result()
    if result == '1-0':
        winner = 'White won the game!'
    elif result == '0-1':
        winner = 'Black won the game!'
    else:
        winner = 'Game ended due to draw!'        
    pygame.draw.rect(screen, 'black', (160, 280, 320, 80))
    screen.blit(font_Pixeloid.render(f'{winner}', True, 'white'), (170, 290))
    screen.blit(font_Pixeloid.render(f'Press ENTER to Restart!', True, 'white'), (170, 330))

# Records each move
def archive_move(move, san = True):
    if san == True:
        san = board.san(move)
    if move_count % 2 == 0:
        lan_stack.append(str(move_count//2 + 1) +'. '+ san + ' ')            
    else:
        lan_stack.append(san + ' ')

# Writes after game ends
def archive_game():
    lan_stack.append(board.result() + '\n')
    f = open('Games_Archive.txt','a')
    f.writelines(lan_stack)
    f.close()

def draw_archive():

    global games_archive_index, games_archive, game_lan, editing

    screen.fill('grey')
    pygame.draw.rect(screen, 'light grey', left_button, 3, 15)
    pygame.draw.rect(screen, 'light grey', right_button, 3, 15)
    pygame.draw.rect(screen, 'light grey', archive_return_button, 3, 15)
    pygame.draw.rect(screen, 'light grey', edit_button, 3, 15)
    pygame.draw.rect(screen, 'light grey', delete_button, 3, 15)

    screen.blit(font_Pixeloid_big.render('<', True, 'black'), (left_button.x + 17, left_button.y))
    screen.blit(font_Pixeloid_big.render('>', True, 'black'), (right_button.x + 17, right_button.y))
    screen.blit(return_img, (archive_return_button.x + 10, archive_return_button.y + 10))
    screen.blit(edit_img, (edit_button.x + 10, edit_button.y + 10))
    screen.blit(delete_img, (delete_button.x + 10, delete_button.y + 10))
    f = open('Games_Archive.txt', 'r')
    games_archive = f.readlines()
    f.close()
    if games_archive == []:
        game_lan = "No games recorded."
    elif editing:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    game_lan = game_lan[:-1]
                elif event.key == pygame.K_RETURN:
                    f = open('Games_Archive.txt', 'w')
                    game_lan = game_lan.replace('\n', '') + '\n'
                    games_archive[games_archive_index] = game_lan
                    f.writelines(games_archive)
                    f.close()
                    editing = False
                else:
                    game_lan += event.unicode
    else:
        game_lan = games_archive[games_archive_index]
        if len(game_lan) > 50:
            for i in range(len(game_lan)//50):
                index = game_lan.find(str(6 + 4*i) + '.')
                game_lan = game_lan[:index] + '\n' + game_lan[index:]

    lan = font_Pixeloid.render(game_lan, True, 'black')    
    screen.blit(font_Pixeloid_big.render('Game '+ str(games_archive_index + 1), True, 'black'), (80, 20))
    
    pygame.draw.rect(screen, 'light grey', (20, 100, lan.get_width() + 30, lan.get_height() + 15), 0, 15)
    screen.blit(lan , (35, 110))
    

# Main loop
running = True
timer.tick(60)
pygame.mixer.music.play(-1,1.0)
while running == True:
    if game_state == 'menu':
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                if play_button.collidepoint(x, y):
                    # Start the chess game
                    game_state = 'game'
                    # pygame.mixer.music.fadeout(2000)
                    screen = pygame.display.set_mode((720, HEIGHT))
                    draw_board()
                elif archives_button.collidepoint(x, y):
                    # Show game archives

                    game_state = 'archive'
        pygame.display.flip()
    if game_state =='game':

        if board.turn == chess.BLACK:
            move = chess.Move.from_uci(stockfish.get_best_move())
            archive_move(move)
            board.push(move)
            stockfish.make_moves_from_current_position([move])
            draw_board()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
               running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Handle mouse click events
                x, y = event.pos
                if game_return_button.collidepoint(x, y):
                    game_state = 'menu'
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))
                if 25 <= x <= 613 and 25 <= y <= 613:
                    # Calculate the square from the mouse click
                    col = int((x - 25) // 73.5)
                    row = int(7 - ((y - 25) // 73.5))
                    square = chess.square(col, row)
                    piece = board.piece_at(square)

                    if selected_square is None:
                        if piece is not None and piece.color == chess.WHITE:
                            selected_square = square
                            draw_board()
                    else:
                        move = chess.Move(selected_square, square)
                        x, y = event.pos
                        col, row = x // 80, 7 - (y // 80)  # Calculate the square from the mouse click
                
                        if move in board.legal_moves:
                            pygame.mixer.Sound.play(move_sound)  
                            if board.is_capture(move):
                                pygame.mixer.Sound.play(capture_sound)
                            archive_move(move)        
                            board.push(move)
                            stockfish.make_moves_from_current_position([move])
                            move_count += 1
                            draw_board()

                            if board.is_check():
                                pygame.mixer.Sound.play(check_sound)
                        
                        selected_square = None
                
            if event.type == pygame.KEYDOWN and board.is_game_over():
                if event.key == pygame.K_RETURN:
                    archive_game()
                    board.reset()
                    move_count = 0
                    pygame.mixer.Sound.play(start_sound)
                    draw_board()
                    
        if board.is_game_over():
            draw_game_over()
            stockfish.set_position([])
        pygame.display.flip()
    
    if game_state == 'archive':
        draw_archive()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                if left_button.collidepoint(x, y):
                    if games_archive_index > 0:
                        games_archive_index -= 1
                elif right_button.collidepoint(x, y):
                    if games_archive_index < len(games_archive) - 1:
                        games_archive_index += 1
                elif archive_return_button.collidepoint(x, y):
                    game_state = 'menu'
                elif edit_button.collidepoint(x, y):
                    editing = True
                elif delete_button.collidepoint(x, y):
                    f = open('Games_Archive.txt', 'w')
                    if games_archive_index < len(games_archive) - 1:
                        f.writelines(games_archive[:games_archive_index] + games_archive[games_archive_index + 1:])
                    else:
                        f.writelines(games_archive[:games_archive_index])
                        games_archive_index -= 1
                    f.close()
                    

                            

        pygame.display.flip()            

# Quit Pygame
pygame.quit()