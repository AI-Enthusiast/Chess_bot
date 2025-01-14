import time
import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = (WIDTH // COLS)

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


# Place pieces randomly on the board
def place_pieces_randomly(images):
    positions = [(row, col) for row in range(ROWS) for col in range(COLS)]
    random.shuffle(positions)
    for piece in images.keys():
        row, col = positions.pop()
        screen.blit(images[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))


# Main loop
def main():
    clock = pygame.time.Clock()
    images = load_images()  # Load images here
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        draw_board()
        place_pieces_randomly(images)
        pygame.display.flip()
        time.sleep(5)
        clock.tick(60)


if __name__ == '__main__':
    main()
