from Calc_moves import (
    area_moves,
    castle_moves,
    diagonal_moves,
    en_pessent,
    knight_moves,
    pawn_moves,
    promotion_moves,
    straightline_moves,
    under_attack,
)
from Const import (
    BISHOP,
    BLACK,
    CASTLE,
    EN_PESSANT,
    KING,
    KNIGHT,
    NORMAL,
    PAWN,
    PROMOTION,
    QUEEN,
    ROOK,
    ROWS,
    WHITE,
)
from Utils import (
    col,
    colour,
    flag,
    from_square,
    piece,
    promotion_piece,
    row,
    to_square,
)


class Board:
    def __init__(self):
        self.colour = 8
        self.castling_rights = 0b1111
        self.ep_file = None

        self.bitboard = {
            BLACK + PAWN: 0,
            WHITE + PAWN: 0,
            BLACK + BISHOP: 0,
            WHITE + BISHOP: 0,
            BLACK + KNIGHT: 0,
            WHITE + KNIGHT: 0,
            BLACK + ROOK: 0,
            WHITE + ROOK: 0,
            BLACK + QUEEN: 0,
            WHITE + QUEEN: 0,
            WHITE + KING: 0,
            BLACK + KING: 0,
        }

        self._add_pieces()
        self.last_move = {"move": 0, "piece": 0}

        self.unmake_data = {
            "valid": 0,
            "move": 0,
            "piece eaten": 0,
            "colour": 0,
            "castling rights": self.castling_rights,
            "ep_file": None,
            "prev": 0,
        }

    def __eq__(self, other):
        return self.bitboard == other.bitboard

    def total_pieces(self):
        return sum((v).bit_count() for v in self.bitboard.values())

    def _add_pieces(self):
        self.bitboard[BLACK + PAWN] = (2**8 - 1) << 8 * 1
        self.bitboard[WHITE + PAWN] = (2**8 - 1) << 8 * 6
        self.bitboard[BLACK + BISHOP] = (1 << (0 * ROWS + 2)) + (1 << (0 * ROWS + 5))
        self.bitboard[WHITE + BISHOP] = (1 << (7 * ROWS + 2)) + (1 << (7 * ROWS + 5))
        self.bitboard[BLACK + KNIGHT] = (1 << (0 * ROWS + 1)) + (1 << (0 * ROWS + 6))
        self.bitboard[WHITE + KNIGHT] = (1 << (7 * ROWS + 1)) + (1 << (7 * ROWS + 6))
        self.bitboard[BLACK + ROOK] = (1 << (0 * ROWS + 0)) + (1 << (0 * ROWS + 7))
        self.bitboard[WHITE + ROOK] = (1 << (7 * ROWS + 0)) + (1 << (7 * ROWS + 7))
        self.bitboard[BLACK + QUEEN] = 1 << (0 * ROWS + 3)
        self.bitboard[WHITE + QUEEN] = 1 << (7 * ROWS + 3)
        self.bitboard[BLACK + KING] = 1 << (0 * ROWS + 4)
        self.bitboard[WHITE + KING] = 1 << (7 * ROWS + 4)

    def find_piece(self, position):
        for k, v in self.bitboard.items():
            if (v >> position) & 1:
                return k
        return 0

    def make_move(self, move):
        old_castling_rights = self.castling_rights
        old_ep_file = self.ep_file

        self.unmake_data = {
            "valid": 1,
            "move": move,
            "piece eaten": 0,
            "colour": 0,
            "castling rights": old_castling_rights,
            "ep_file": old_ep_file,
            "last_move": self.last_move,
            "prev": self.unmake_data,
        }

        from_square_ = from_square(move)
        to_square_ = to_square(move)
        flag_ = flag(move)
        promotion_piece_ = promotion_piece(move)
        move_piece = self.find_piece(from_square_)
        move_colour = colour(move_piece)

        if flag_ == NORMAL:
            eat_piece = self.find_piece(to_square_)

            self.bitboard[move_piece] &= ~(1 << from_square_)
            self.bitboard[move_piece] |= 1 << to_square_

            if eat_piece != 0:
                self.bitboard[eat_piece] &= ~(1 << to_square_)
                self.unmake_data["piece eaten"] = eat_piece

            shift = 2 if move_colour == WHITE else 0
            if move_piece == move_colour + KING:
                self.castling_rights &= ~((2**2 - 1) << shift)
            elif move_piece == move_colour + ROOK:
                v = 1 if col(from_square_) == 7 else 2
                self.castling_rights &= ~(v << shift)
            elif eat_piece == move_colour + ROOK:
                v = 1 if col(to_square_) == 7 else 2
                self.castling_rights &= ~(v << shift)

        elif flag_ == CASTLE:
            self.bitboard[move_piece] &= ~(1 << from_square_)
            self.bitboard[move_piece] |= 1 << to_square_  # changed king pos

            castle_col = col(to_square_)
            castle_row = row(to_square_)

            if castle_col == 2:
                self.bitboard[move_colour + ROOK] &= ~(
                    1 << (castle_row * ROWS + 0)
                )  # rook gayab
                self.bitboard[move_colour + ROOK] |= 1 << (
                    castle_row * ROWS + 3
                )  # rook aa gaya
            elif castle_col == 6:
                self.bitboard[move_colour + ROOK] &= ~(
                    1 << (castle_row * ROWS + 7)
                )  # rook gayab
                self.bitboard[move_colour + ROOK] |= 1 << (
                    castle_row * ROWS + 5
                )  # rook aa gaya

            shift = 2 if move_colour == WHITE else 0
            self.castling_rights &= ~((2**2 - 1) << shift)

        elif flag_ == EN_PESSANT:
            eat_square = row(from_square_) * ROWS + col(to_square_)
            eat_piece = self.find_piece(eat_square)
            self.bitboard[move_piece] &= ~(1 << from_square_)
            self.bitboard[move_piece] |= 1 << to_square_

            self.bitboard[eat_piece] &= ~(1 << eat_square)
            self.unmake_data["piece eaten"] = eat_piece

        elif flag_ == PROMOTION:
            eat_piece = self.find_piece(to_square_)
            promoted_piece = move_colour + promotion_piece_

            self.bitboard[move_piece] &= ~(1 << from_square_)
            self.bitboard[promoted_piece] |= 1 << to_square_

            if eat_piece != 0:
                self.bitboard[eat_piece] &= ~(1 << to_square_)
                self.unmake_data["piece eaten"] = eat_piece

        self.unmake_data["colour"] = move_colour
        self.colour = 16 if move_colour == 8 else 8

        self.last_move = {"move": move, "piece": move_piece}

    def unmake_move(self):
        if self.unmake_data["valid"]:
            move = self.unmake_data["move"]
            from_square_ = from_square(move)
            to_square_ = to_square(move)
            flag_ = flag(move)  # 4 flags possible
            move_piece = self.find_piece(to_square_)  # colour and piece
            move_colour = colour(move_piece)  # colour of the piece

            if flag_ == NORMAL:
                eat_piece = self.unmake_data["piece eaten"]

                self.bitboard[move_piece] |= 1 << from_square_
                self.bitboard[move_piece] &= ~(1 << to_square_)

                if eat_piece != 0:
                    self.bitboard[eat_piece] |= 1 << to_square_

            elif flag_ == CASTLE:
                self.bitboard[move_piece] |= 1 << from_square_
                self.bitboard[move_piece] &= ~(1 << to_square_)  # changed king pos

                castle_col = col(to_square_)
                castle_row = row(to_square_)

                if castle_col == 2:
                    self.bitboard[move_colour + ROOK] |= 1 << (
                        castle_row * ROWS + 0
                    )  # rook gayab
                    self.bitboard[move_colour + ROOK] &= ~(
                        1 << (castle_row * ROWS + 3)
                    )  # rook aa gaya
                elif castle_col == 6:
                    self.bitboard[move_colour + ROOK] |= 1 << (
                        castle_row * ROWS + 7
                    )  # rook gayab
                    self.bitboard[move_colour + ROOK] &= ~(
                        1 << (castle_row * ROWS + 5)
                    )  # rook aa gaya

            elif flag_ == EN_PESSANT:
                eat_square = row(from_square_) * ROWS + col(to_square_)
                eat_piece = self.unmake_data["piece eaten"]
                self.bitboard[move_piece] |= 1 << from_square_
                self.bitboard[move_piece] &= ~(1 << to_square_)  # changed pawn pos

                self.bitboard[eat_piece] |= 1 << eat_square

            elif flag_ == PROMOTION:
                promoted_piece = move_piece

                self.bitboard[move_colour + PAWN] |= 1 << from_square_  # pawn returns
                self.bitboard[promoted_piece] &= ~(
                    1 << to_square_
                )  # promoted piece removed

                eat_piece = self.unmake_data["piece eaten"]
                if eat_piece != 0:
                    self.bitboard[eat_piece] |= (
                        1 << to_square_
                    )  # captured piece restored
                    self.unmake_data["piece eaten"] = 0

            self.colour = self.unmake_data["colour"]
            self.castling_rights = self.unmake_data["castling rights"]
            self.ep_file = self.unmake_data["ep_file"]
            self.last_move = self.unmake_data["last_move"]

            self.unmake_data = self.unmake_data["prev"]

    def generate_moves(self, colour_):
        moves = []
        for p in [PAWN, BISHOP, QUEEN, KING, KNIGHT, ROOK]:
            piece_ = colour_ + p

            if piece(piece_) == PAWN:
                for pos in self.iter_bits(self.bitboard[piece_]):
                    moves += pawn_moves(pos, self)
                    if (pos // 8 == 3 and colour_ == WHITE) or (
                        pos // 8 == 4 and colour_ == BLACK
                    ):
                        moves += en_pessent(
                            pos,
                            self,
                            last_move=self.last_move["move"],
                            last_piece=self.last_move["piece"],
                        )
                    elif (pos // 8 == 1 and colour_ == WHITE) or (
                        pos // 8 == 6 and colour_ == BLACK
                    ):
                        moves += promotion_moves(pos, self)

            if piece(piece_) == ROOK:
                for pos in self.iter_bits(self.bitboard[piece_]):
                    moves += straightline_moves(pos, self)

            if piece(piece_) == BISHOP:
                for pos in self.iter_bits(self.bitboard[piece_]):
                    moves += diagonal_moves(pos, self)

            if piece(piece_) == QUEEN:
                for pos in self.iter_bits(self.bitboard[piece_]):
                    moves += straightline_moves(pos, self)
                    moves += diagonal_moves(pos, self)

            if piece(piece_) == KING:
                for pos in self.iter_bits(self.bitboard[piece_]):
                    moves += area_moves(pos, self)
                    moves += castle_moves(pos, self)

            if piece(piece_) == KNIGHT:
                for pos in self.iter_bits(self.bitboard[piece_]):
                    moves += knight_moves(pos, self)

        return moves

    def find_pins(self, colour_):
        king_bb = self.bitboard[colour_ + KING]
        if king_bb == 0:
            return {}

        king_sq = king_bb.bit_length() - 1
        king_row, king_col = row(king_sq), col(king_sq)

        directions = [
            (-1, 0, (ROOK, QUEEN)),
            (1, 0, (ROOK, QUEEN)),
            (0, -1, (ROOK, QUEEN)),
            (0, 1, (ROOK, QUEEN)),
            (-1, -1, (BISHOP, QUEEN)),
            (-1, 1, (BISHOP, QUEEN)),
            (1, -1, (BISHOP, QUEEN)),
            (1, 1, (BISHOP, QUEEN)),
        ]

        pinned = {}

        for dr, dc, slider_types in directions:
            ray_squares = []
            own_piece_sq = None
            r, c = king_row + dr, king_col + dc

            while 0 <= r < 8 and 0 <= c < 8:
                sq = r * 8 + c
                ray_squares.append(sq)
                occ = self.find_piece(sq)

                if occ != 0:
                    if colour(occ) == colour_:
                        if own_piece_sq is None:
                            own_piece_sq = sq
                            r += dr
                            c += dc
                            continue
                        break
                    else:
                        if own_piece_sq is not None and piece(occ) in slider_types:
                            pinned[own_piece_sq] = set(ray_squares)
                        break

                r += dr
                c += dc

        return pinned

    def status_and_moves(self, colour_):
        king_bb = self.bitboard[colour_ + KING]
        if king_bb == 0:
            return 2, []

        king_square = king_bb.bit_length() - 1
        in_check = under_attack(king_square, self, colour_)
        moves = self.generate_moves(colour_)

        if len(moves) == 0:
            return (2 if in_check else 1), moves

        return 0, moves

    def game_over_status(self):
        status, _ = self.status_and_moves(self.colour)
        return status

    def iter_bits(self, bb):
        while bb:
            lsb = bb & -bb  # 2's complement to get the lowest active bit
            sq = lsb.bit_length() - 1
            yield sq
            bb ^= lsb


if __name__ == "__main__":
    board = Board()
    print(board.bitboard)
    print(board.total_pieces())
