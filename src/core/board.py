import time
import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
WHITE = (255, 202, 97)
BLACK = (200, 127, 0)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Chess')

# Load images
def load_images():
    pieces = ['black-bishop', 'black-king', 'black-knight', 'black-pawn', 'black-queen', 'black-rook',
              'white-bishop', 'white-king', 'white-knight', 'white-pawn', 'white-queen', 'white-rook']
    images = {}
    for piece in pieces:
        image = pygame.image.load(f'images/{piece}.png')
        images[piece] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
    return images

# Draw the board
def draw_board():
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Parse FEN string and place pieces on the board
def place_pieces_from_fen(fen, images):
    piece_to_fen = {
        'r': 'black-rook', 'n': 'black-knight', 'b': 'black-bishop', 'q': 'black-queen', 'k': 'black-king',
        'p': 'black-pawn',
        'R': 'white-rook', 'N': 'white-knight', 'B': 'white-bishop', 'Q': 'white-queen', 'K': 'white-king',
        'P': 'white-pawn'
    }
    rows = fen.split(' ')[0].split('/')
    board = [['' for _ in range(COLS)] for _ in range(ROWS)]
    for row_idx, row in enumerate(rows):
        col_idx = 0
        for char in row:
            if char.isdigit():
                col_idx += int(char)
            else:
                piece = piece_to_fen[char]
                board[row_idx][col_idx] = piece
                screen.blit(images[piece], (col_idx * SQUARE_SIZE, row_idx * SQUARE_SIZE))
                col_idx += 1
    return board

# Check if the move is valid for a pawn
def is_valid_pawn_move(board, start_pos, end_pos, piece):
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    direction = -1 if piece.startswith('white') else 1
    start_row_home = 6 if piece.startswith('white') else 1

    # Move forward one square
    if start_col == end_col and board[end_row][end_col] == '':
        if end_row == start_row + direction:
            return True
        # Move forward two squares from starting position
        if start_row == start_row_home and end_row == start_row + 2 * direction and board[start_row + direction][start_col] == '':
            return True
    # Capture diagonally
    if abs(start_col - end_col) == 1 and end_row == start_row + direction and board[end_row][end_col] != '' and not board[end_row][end_col].startswith(piece.split('-')[0]):
        return True
    return False

# Check if the move is valid for a rook
def is_valid_rook_move(board, start_pos, end_pos, piece):
    start_row, start_col = start_pos
    end_row, end_col = end_pos

    if start_row == end_row:
        step = 1 if start_col < end_col else -1
        for col in range(start_col + step, end_col, step):
            if board[start_row][col] != '':
                return False
        return True
    elif start_col == end_col:
        step = 1 if start_row < end_row else -1
        for row in range(start_row + step, end_row, step):
            if board[row][start_col] != '':
                return False
        return True
    return False

# Check if the move is valid for a knight
def is_valid_knight_move(board, start_pos, end_pos, piece):
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    row_diff = abs(start_row - end_row)
    col_diff = abs(start_col - end_col)
    return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

# Check if the move is valid for a bishop
def is_valid_bishop_move(board, start_pos, end_pos, piece):
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    if abs(start_row - end_row) == abs(start_col - end_col):
        row_step = 1 if start_row < end_row else -1
        col_step = 1 if start_col < end_col else -1
        for i in range(1, abs(start_row - end_row)):
            if board[start_row + i * row_step][start_col + i * col_step] != '':
                return False
        return True
    return False

# Check if the move is valid for a queen
def is_valid_queen_move(board, start_pos, end_pos, piece):
    return is_valid_rook_move(board, start_pos, end_pos, piece) or is_valid_bishop_move(board, start_pos, end_pos, piece)

# Check if the move is valid for a king
def is_valid_king_move(board, start_pos, end_pos, piece):
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    row_diff = abs(start_row - end_row)
    col_diff = abs(start_col - end_col)
    return row_diff <= 1 and col_diff <= 1

# Check if the king is in check
def is_in_check(board, king_pos, king_color):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece and not piece.startswith(king_color):
                if piece.endswith('pawn') and is_valid_pawn_move(board, (row, col), king_pos, piece):
                    return True
                elif piece.endswith('rook') and is_valid_rook_move(board, (row, col), king_pos, piece):
                    return True
                elif piece.endswith('knight') and is_valid_knight_move(board, (row, col), king_pos, piece):
                    return True
                elif piece.endswith('bishop') and is_valid_bishop_move(board, (row, col), king_pos, piece):
                    return True
                elif piece.endswith('queen') and is_valid_queen_move(board, (row, col), king_pos, piece):
                    return True
                elif piece.endswith('king') and is_valid_king_move(board, (row, col), king_pos, piece):
                    return True
    return False

# Check for checkmate
def is_checkmate(board, king_pos, king_color, castling_rights):
    if not is_in_check(board, king_pos, king_color):
        return False
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece and piece.startswith(king_color):
                valid_moves = get_all_valid_moves(board, (row, col), piece, castling_rights)
                for move in valid_moves:
                    temp_board = [row[:] for row in board]
                    temp_board[move[0]][move[1]] = piece
                    temp_board[row][col] = ''
                    if not is_in_check(temp_board, king_pos, king_color):
                        return False
    return True

# Check if castling is valid
def is_valid_castling(board, start_pos, end_pos, piece, castling_rights):
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    if start_row != end_row or abs(start_col - end_col) != 2:
        return False
    if piece.startswith('white'):
        if end_col == 6 and castling_rights['white_kingside']:
            return board[start_row][5] == '' and board[start_row][6] == ''
        elif end_col == 2 and castling_rights['white_queenside']:
            return board[start_row][1] == '' and board[start_row][2] == '' and board[start_row][3] == ''
    else:
        if end_col == 6 and castling_rights['black_kingside']:
            return board[start_row][5] == '' and board[start_row][6] == ''
        elif end_col == 2 and castling_rights['black_queenside']:
            return board[start_row][1] == '' and board[start_row][2] == '' and board[start_row][3] == ''
    return False

# Track the history of moves and turns
move_history = []
turn_history = []

# Add an undo button
def draw_undo_button():
    font = pygame.font.Font(None, 36)
    text = font.render('Undo', True, (0, 0, 0))
    pygame.draw.rect(screen, (255, 255, 255), (WIDTH - 100, HEIGHT - 50, 80, 40))
    screen.blit(text, (WIDTH - 90, HEIGHT - 45))

# Undo the last move
def undo_move(board, move_history, turn_history):
    if move_history and turn_history:
        last_move = move_history.pop()
        start_pos, end_pos, piece = last_move
        board[start_pos[0]][start_pos[1]] = piece
        board[end_pos[0]][end_pos[1]] = ''
        return turn_history.pop()
    return None

# Get all valid moves for a piece
def get_all_valid_moves(board, start_pos, piece, castling_rights):
    valid_moves = []
    for row in range(ROWS):
        for col in range(COLS):
            end_pos = (row, col)
            target_piece = board[row][col]
            if target_piece and target_piece.startswith(piece.split('-')[0]):
                continue  # Skip moves that would take your own piece
            if piece.endswith('pawn') and is_valid_pawn_move(board, start_pos, end_pos, piece):
                valid_moves.append(end_pos)
            elif piece.endswith('rook') and is_valid_rook_move(board, start_pos, end_pos, piece):
                valid_moves.append(end_pos)
            elif piece.endswith('knight') and is_valid_knight_move(board, start_pos, end_pos, piece):
                valid_moves.append(end_pos)
            elif piece.endswith('bishop') and is_valid_bishop_move(board, start_pos, end_pos, piece):
                valid_moves.append(end_pos)
            elif piece.endswith('queen') and is_valid_queen_move(board, start_pos, end_pos, piece):
                valid_moves.append(end_pos)
            elif piece.endswith('king') and (is_valid_king_move(board, start_pos, end_pos, piece) or is_valid_castling(board, start_pos, end_pos, piece, castling_rights)):
                valid_moves.append(end_pos)
    return valid_moves

# Make a random valid move for the current turn
def make_random_move(board, current_turn, castling_rights):
    pieces = [(row, col) for row in range(ROWS) for col in range(COLS) if board[row][col].startswith(current_turn)]
    random.shuffle(pieces)
    for start_pos in pieces:
        piece = board[start_pos[0]][start_pos[1]]
        valid_moves = get_all_valid_moves(board, start_pos, piece, castling_rights)
        if valid_moves:
            end_pos = random.choice(valid_moves)
            move_history.append((start_pos, end_pos, piece))
            turn_history.append(current_turn)
            board[start_pos[0]][start_pos[1]] = ''
            board[end_pos[0]][end_pos[1]] = piece
            return True
    return False

# Make a greedy move for the current turn
def piece_value(piece):
    values = {
        'pawn': 1,
        'knight': 3,
        'bishop': 3,
        'rook': 5,
        'queen': 9,
        'king': 0  # King is invaluable
    }
    return values[piece.split('-')[1]]

def make_greedy_move(board, current_turn, castling_rights):
    best_move = None
    best_value = -1
    pieces = [(row, col) for row in range(ROWS) for col in range(COLS) if board[row][col].startswith(current_turn)]

    for start_pos in pieces:
        piece = board[start_pos[0]][start_pos[1]]
        valid_moves = get_all_valid_moves(board, start_pos, piece, castling_rights)

        for end_pos in valid_moves:
            target_piece = board[end_pos[0]][end_pos[1]]
            value = piece_value(target_piece) if target_piece else 0
            if value > best_value:
                best_value = value
                best_move = (start_pos, end_pos, piece)

    if best_move:
        start_pos, end_pos, piece = best_move
        move_history.append((start_pos, end_pos, piece))
        turn_history.append(current_turn)
        board[start_pos[0]][start_pos[1]] = ''
        board[end_pos[0]][end_pos[1]] = piece
        return True
    return False

# Check for stalemate
def is_stalemate(board, current_turn):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece and piece.startswith(current_turn):
                for r in range(ROWS):
                    for c in range(COLS):
                        if piece.endswith('pawn') and is_valid_pawn_move(board, (row, col), (r, c), piece):
                            if not is_in_check(board, (r, c), current_turn):
                                return False
                        elif piece.endswith('rook') and is_valid_rook_move(board, (row, col), (r, c), piece):
                            if not is_in_check(board, (r, c), current_turn):
                                return False
                        elif piece.endswith('knight') and is_valid_knight_move(board, (row, col), (r, c), piece):
                            if not is_in_check(board, (r, c), current_turn):
                                return False
                        elif piece.endswith('bishop') and is_valid_bishop_move(board, (row, col), (r, c), piece):
                            if not is_in_check(board, (r, c), current_turn):
                                return False
                        elif piece.endswith('queen') and is_valid_queen_move(board, (row, col), (r, c), piece):
                            if not is_in_check(board, (r, c), current_turn):
                                return False
                        elif piece.endswith('king') and is_valid_king_move(board, (row, col), (r, c), piece):
                            if not is_in_check(board, (r, c), current_turn):
                                return False
    return True

# Main loop
def main():
    clock = pygame.time.Clock()
    images = load_images()  # Load images here
    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    board = place_pieces_from_fen(fen, images)
    castling_rights = {
        'white_kingside': True,
        'white_queenside': True,
        'black_kingside': True,
        'black_queenside': True
    }
    current_turn = 'white'  # Track the current turn

    # Choose models for each side
    white_model = make_random_move
    black_model = make_greedy_move

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if WIDTH - 100 <= x <= WIDTH - 20 and HEIGHT - 50 <= y <= HEIGHT - 10:
                    previous_turn = undo_move(board, move_history, turn_history)
                    if previous_turn:
                        current_turn = previous_turn

        if current_turn == 'white':
            if not white_model(board, current_turn, castling_rights):
                if is_stalemate(board, current_turn):
                    print(f"Stalemate. {current_turn} has no valid moves and is not in check. Game over.")
                else:
                    print(f"{current_turn} has no valid moves. Game over.")
                pygame.quit()
                sys.exit()
        else:
            if not black_model(board, current_turn, castling_rights):
                if is_stalemate(board, current_turn):
                    print(f"Stalemate. {current_turn} has no valid moves and is not in check. Game over.")
                else:
                    print(f"{current_turn} has no valid moves. Game over.")
                pygame.quit()
                sys.exit()

        current_turn = 'black' if current_turn == 'white' else 'white'  # Switch turns

        draw_board()
        draw_undo_button()
        for row in range(ROWS):
            for col in range(COLS):
                if board[row][col]:
                    screen.blit(images[board[row][col]], (col * SQUARE_SIZE, row * SQUARE_SIZE))
        pygame.display.flip()
        clock.tick(1)  # Slow down the game to 1 move per second

if __name__ == '__main__':
    main()