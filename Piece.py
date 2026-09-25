import os

from Const import BISHOP, KING, KNIGHT, PAWN, QUEEN, ROOK, WHITE


class Piece:
    def __init__(self, colour, idx, img=None, img_rect=None):
        self.possible_moves = 0
        self.encoding = colour + idx
        self.img = img
        self.img_rect = img_rect
        self.colour = "white" if colour == WHITE else "black"

        if idx == KING:
            self.name = "king"
        elif idx == QUEEN:
            self.name = "queen"
        elif idx == ROOK:
            self.name = "rook"
        elif idx == BISHOP:
            self.name = "bishop"
        elif idx == KNIGHT:
            self.name = "knight"
        elif idx == PAWN:
            self.name = "pawn"

        self.set_img()

    def set_img(self, size=80):
        self.img = os.path.join(
            f"assets\images\imgs-{size}px\{self.colour}_{self.name}.png"
        )


class King(Piece):
    def __init__(self, colour):
        super().__init__(colour=colour, idx=KING)


class Queen(Piece):
    def __init__(self, colour):
        super().__init__(colour=colour, idx=QUEEN)


class Rook(Piece):
    def __init__(self, colour):
        super().__init__(colour=colour, idx=ROOK)


class Knight(Piece):
    def __init__(self, colour):
        super().__init__(colour=colour, idx=KNIGHT)


class Bishop(Piece):
    def __init__(self, colour):
        super().__init__(colour=colour, idx=BISHOP)


class Pawn(Piece):
    def __init__(self, colour):
        super().__init__(colour=colour, idx=PAWN)
