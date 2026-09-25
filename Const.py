WIDTH = 800
LENGTH = 800

ROWS = 8
COLS = 8
SQLENGTH = 100

PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 4
QUEEN = 5
KING = 6

WHITE = 8
BLACK = 16

# Move ->  flag -- promotion_piece -- to_square -- from_square
#           2            3               6             6

# flags:
NORMAL = 0
EN_PESSANT = 1
CASTLE = 2
PROMOTION = 3

# masks to get values:
FROM_SQUARE_MASK = 2**6 - 1
TO_SQUARE_MASK = FROM_SQUARE_MASK << 6
PROMOTION_PIECE_MASK = (2**3 - 1) << 12
FLAG_MASK = (2**2 - 1) << 15

# square states:
NORMAL_ = 0
SELECTED = 1
MOVE = 2

# castling rights
BLACK_CASTLE = 0b11
WHITE_CASTLE = 0b11
