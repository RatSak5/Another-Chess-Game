from Const import (
    BISHOP,
    FLAG_MASK,
    FROM_SQUARE_MASK,
    KING,
    KNIGHT,
    NORMAL,
    PAWN,
    PROMOTION_PIECE_MASK,
    QUEEN,
    ROOK,
    TO_SQUARE_MASK,
)
from Piece import Bishop, King, Knight, Pawn, Queen, Rook


def row(square):
    return square // 8


def col(square):
    return square % 8


def colour(piece_enc):
    return piece_enc & ~(2**3 - 1)


def piece(piece_enc):
    return piece_enc & (2**3 - 1)


def get_piece_img(piece_enc):
    c, p = colour(piece_enc), piece(piece_enc)
    if p == PAWN:
        return Pawn(c).img
    elif p == BISHOP:
        return Bishop(c).img
    elif p == KNIGHT:
        return Knight(c).img
    elif p == ROOK:
        return Rook(c).img
    elif p == QUEEN:
        return Queen(c).img
    elif p == KING:
        return King(c).img


def encode_move(from_square, to_square, flag=NORMAL, promotion_piece=0):
    return (flag << 15) + (promotion_piece << 12) + (to_square << 6) + from_square


def to_square(move):
    return (move & TO_SQUARE_MASK) >> 6


def from_square(move):
    return move & FROM_SQUARE_MASK


def promotion_piece(move):
    return (move & PROMOTION_PIECE_MASK) >> 12


def flag(move):
    return (move & FLAG_MASK) >> 15
