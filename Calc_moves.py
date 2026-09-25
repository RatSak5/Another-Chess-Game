from Const import (
    BISHOP,
    CASTLE,
    EN_PESSANT,
    KING,
    KNIGHT,
    NORMAL,
    PAWN,
    PROMOTION,
    QUEEN,
    ROOK,
    WHITE,
)
from Utils import col, colour, encode_move, flag, from_square, piece, row, to_square


def under_attack(pos, board, self_colour):
    return (
        diagonal_moves(pos, board, is_attacking=True, self_colour=self_colour)
        or straightline_moves(pos, board, is_attacking=True, self_colour=self_colour)
        or pawn_moves(pos, board, is_attacking=True, self_colour=self_colour)
        or area_moves(pos, board, is_attacking=True, self_colour=self_colour)
        or knight_moves(pos, board, is_attacking=True, self_colour=self_colour)
        or promotion_moves(pos, board, is_attacking=True, self_colour=self_colour)
    )


def diagonal_moves(pos, board, is_attacking=False, self_colour=0):
    if is_attacking:
        pieces = False
    moves = []
    flag = NORMAL
    from_square_ = pos
    move_piece = board.find_piece(from_square_)
    colour_ = colour(move_piece) if not is_attacking else self_colour
    from_col = pos % 8

    for offset in [-7, +7, -9, +9]:
        current = pos
        prev_col = from_col
        while True:
            current += offset
            if not (0 <= current < 64):
                break
            cur_col = current % 8
            if abs(cur_col - prev_col) != 1:
                break
            prev_col = cur_col

            piece_ = board.find_piece(current)
            if piece_:
                if colour(piece_) != colour_:
                    if is_attacking and (
                        piece(piece_) == BISHOP or piece(piece_) == QUEEN
                    ):
                        pieces = True
                    moves.append(encode_move(from_square_, current, flag=flag))
                break
            else:
                moves.append(encode_move(from_square_, current, flag=flag))

    if not is_attacking:
        moves = remove_danger(moves, board, colour_)

    if is_attacking:
        return pieces
    return moves


def straightline_moves(pos, board, is_attacking=False, self_colour=0):
    if is_attacking:
        pieces = False
    moves = []
    flag = NORMAL
    from_square_ = pos
    move_piece = board.find_piece(from_square_)
    colour_ = colour(move_piece) if not is_attacking else self_colour

    for offset in [-8, +8]:
        limit = -1 if offset < 0 else 64
        for to_square_ in range(pos + offset, limit, offset):
            piece_ = board.find_piece(to_square_)
            if piece_:
                if colour(piece_) != colour_:
                    if is_attacking and (
                        piece(piece_) == ROOK or piece(piece_) == QUEEN
                    ):
                        pieces = True
                    move = encode_move(from_square_, to_square_, flag=flag)
                    moves.append(move)
                break
            else:
                move = encode_move(from_square_, to_square_, flag=flag)
                moves.append(move)

    for offset in [-1, 1]:
        limit = (pos // 8) * 8 - 1 if offset < 0 else (pos // 8 + 1) * 8
        for to_square_ in range(pos + offset, limit, offset):
            piece_ = board.find_piece(to_square_)
            if piece_:
                if colour(piece_) != colour_:
                    if is_attacking and (
                        piece(piece_) == ROOK or piece(piece_) == QUEEN
                    ):
                        pieces = True
                    move = encode_move(from_square_, to_square_, flag=flag)
                    moves.append(move)
                break
            else:
                move = encode_move(from_square_, to_square_, flag=flag)
                moves.append(move)

    if not is_attacking:
        moves = remove_danger(moves, board, colour_)

    if is_attacking:
        return pieces
    return moves


def pawn_moves(pos, board, is_attacking=False, self_colour=0):
    moves = []

    parent_piece = board.find_piece(pos)
    colour_ = colour(parent_piece) if not is_attacking else self_colour

    orig_row = 6 if colour_ == WHITE else 1
    direction = -1 if colour_ == WHITE else 1

    promotion_row = 1 if colour_ == WHITE else 6

    moved = row(pos) != orig_row
    from_square_ = pos
    to_square_ = (row(pos) + direction) * 8 + col(pos)
    flag = NORMAL

    if not board.find_piece(to_square_) and row(pos) != promotion_row:
        move = encode_move(from_square_, to_square_, flag=flag)
        moves.append(move)

        if not moved:
            to_square_ = (row(pos) + 2 * direction) * 8 + col(pos)
            if not board.find_piece(to_square_):
                move = encode_move(from_square_, to_square_, flag=flag)
                moves.append(move)

    if is_attacking:
        pieces = False

    if row(pos) != promotion_row:
        if col(pos) < 7:
            to_square_ = (row(pos) + direction) * 8 + col(pos) + 1
            piece_ = board.find_piece(to_square_)
            if piece_ and colour(piece_) != colour_:
                if piece(piece_) == PAWN and is_attacking:
                    pieces = True
                moves.append(encode_move(from_square_, to_square_, flag=NORMAL))

        if col(pos) > 0:
            to_square_ = (row(pos) + direction) * 8 + col(pos) - 1
            piece_ = board.find_piece(to_square_)
            if piece_ and colour(piece_) != colour_:
                if piece(piece_) == PAWN and is_attacking:
                    pieces = True
                moves.append(encode_move(from_square_, to_square_, flag=NORMAL))

    if not is_attacking:
        moves = remove_danger(moves, board, colour_)
    if is_attacking:
        return pieces
    return moves


def en_pessent(pos, board, last_move, last_piece):
    moves = []

    parent_piece = board.find_piece(pos)
    colour_ = colour(parent_piece)
    from_square_ = pos

    last_row = 1 if colour_ == WHITE else 6
    last_direction = 1 if colour_ == WHITE else -1

    if (
        row(from_square(last_move)) == last_row
        and row(to_square(last_move)) == last_row + 2 * last_direction
        and piece(last_piece) == PAWN
        and (
            col(to_square(last_move)) == col(pos) + 1
            or col(to_square(last_move)) == col(pos) - 1
        )
    ):
        to_square_ = (last_row + last_direction) * 8 + col(to_square(last_move))
        flag = EN_PESSANT

        move = encode_move(from_square_, to_square_, flag=flag)
        moves.append(move)

    moves = remove_danger(moves, board, colour_)

    return moves


def area_moves(pos, board, is_attacking=False, self_colour=0):
    moves = []
    from_square_ = pos
    if is_attacking:
        pieces = False
    from_col = pos % 8
    from_row = pos // 8
    # (offset, col_delta, row_delta)
    king_offsets = [
        (9, 1, 1),
        (8, 0, 1),
        (7, -1, 1),
        (-1, -1, 0),
        (1, 1, 0),
        (-9, -1, -1),
        (-8, 0, -1),
        (-7, 1, -1),
    ]
    flag = NORMAL
    parent_piece = board.find_piece(pos)
    colour_ = colour(parent_piece) if not is_attacking else self_colour

    for offset, col_delta, row_delta in king_offsets:
        to_square_ = from_square_ + offset
        if not (0 <= to_square_ <= 63):
            continue
        if (
            to_square_ % 8 != from_col + col_delta
            or to_square_ // 8 != from_row + row_delta
        ):
            continue
        piece_ = board.find_piece(to_square_)
        if piece_:
            if colour_ != colour(piece_):
                if piece(piece_) == KING and is_attacking:
                    pieces = True
                moves.append(encode_move(from_square_, to_square_, flag=flag))
        else:
            moves.append(encode_move(from_square_, to_square_, flag=flag))

    if not is_attacking:
        moves = remove_danger(moves, board, colour_)

    if is_attacking:
        return pieces
    return moves


def castle_moves(pos, board):
    moves = []
    flag = CASTLE

    parent_piece = board.find_piece(pos)
    colour_ = colour(parent_piece)
    castle_row = 7 if colour_ == WHITE else 0
    castle_col = 2

    from_square_ = pos
    to_square_ = castle_row * 8 + castle_col

    shift = 2 if colour_ == WHITE else 0
    castling_rights = board.castling_rights >> shift

    # check for check
    if under_attack(pos, board, self_colour=colour_):
        return moves

    if (castling_rights >> 1) & 1 and not (
        board.find_piece(castle_row * 8 + castle_col + 1)
        or board.find_piece(castle_row * 8 + castle_col)
        or board.find_piece(castle_row * 8 + castle_col - 1)
        or under_attack(castle_row * 8 + castle_col + 1, board, self_colour=colour_)
        or under_attack(castle_row * 8 + castle_col, board, self_colour=colour_)
    ):
        move = encode_move(from_square_, to_square_, flag=flag)
        moves.append(move)

    castle_col = 6
    to_square_ = castle_row * 8 + castle_col

    if (castling_rights) & 1 and not (
        board.find_piece(castle_row * 8 + castle_col - 1)
        or board.find_piece(castle_row * 8 + castle_col)
        or under_attack(castle_row * 8 + castle_col - 1, board, self_colour=colour_)
        or under_attack(castle_row * 8 + castle_col, board, self_colour=colour_)
    ):
        move = encode_move(from_square_, to_square_, flag=flag)
        moves.append(move)

    return moves


def knight_moves(pos, board, is_attacking=False, self_colour=0):
    from_square_ = pos
    moves = []
    if is_attacking:
        pieces = False
    from_col = pos % 8
    from_row = pos // 8

    # (offset, col_delta, row_delta)
    knight_offsets = [
        (17, 1, 2),
        (15, -1, 2),
        (10, 2, 1),
        (6, -2, 1),
        (-6, 2, -1),
        (-10, -2, -1),
        (-15, 1, -2),
        (-17, -1, -2),
    ]

    parent_piece = board.find_piece(pos)
    colour_ = colour(parent_piece) if not is_attacking else self_colour

    for offset, col_delta, row_delta in knight_offsets:
        to_square_ = from_square_ + offset
        flag = NORMAL

        if not (0 <= to_square_ <= 63):
            continue
        if (
            to_square_ % 8 != from_col + col_delta
            or to_square_ // 8 != from_row + row_delta
        ):
            continue

        piece_ = board.find_piece(to_square_)
        if piece_:
            if colour_ != colour(piece_):
                if piece(piece_) == KNIGHT and is_attacking:
                    pieces = True
                move = encode_move(from_square_, to_square_, flag=flag)
                moves.append(move)
        else:
            move = encode_move(from_square_, to_square_, flag=flag)
            moves.append(move)

    if not is_attacking:
        moves = remove_danger(moves, board, colour_)

    if is_attacking:
        return pieces
    return moves


def promotion_moves(pos, board, is_attacking=False, self_colour=0):
    moves = []

    parent_piece = board.find_piece(pos)
    colour_ = colour(parent_piece) if not is_attacking else self_colour
    direction = -1 if colour_ == WHITE else 1

    from_square_ = pos
    r = row(pos) + direction
    c = col(pos)

    target_squares = []

    # 1. Forward
    push_square = r * 8 + c
    if not board.find_piece(push_square):
        target_squares.append(push_square)

    if is_attacking:
        pieces = False

    # 2. Right Capture
    if c < 7:
        cap_right = r * 8 + (c + 1)
        target_p = board.find_piece(cap_right)
        if target_p != 0 and colour(target_p) != colour_:
            if piece(target_p) == PAWN and is_attacking:
                pieces = True
            target_squares.append(cap_right)

    # 3. Left Capture
    if c > 0:
        cap_left = r * 8 + (c - 1)
        target_p = board.find_piece(cap_left)
        if target_p != 0 and colour(target_p) != colour_:
            if piece(target_p) == PAWN and is_attacking:
                pieces = True
            target_squares.append(cap_left)

    for target in target_squares:
        for piece_type in [QUEEN, ROOK, KNIGHT, BISHOP]:
            moves.append(
                encode_move(
                    from_square_, target, flag=PROMOTION, promotion_piece=piece_type
                )
            )

    if not is_attacking:
        moves = remove_danger(moves, board, colour_)

    if is_attacking:
        return pieces
    return moves


def remove_danger(moves, board, self_colour):
    if not moves:
        return moves

    moving_piece = board.find_piece(from_square(moves[0]))

    if piece(moving_piece) == KING or any(flag(m) == EN_PESSANT for m in moves):
        return remove_danger_slow(moves, board, self_colour)

    king_bb = board.bitboard[self_colour + KING]
    if king_bb == 0:
        return moves

    king_sq = king_bb.bit_length() - 1
    if under_attack(king_sq, board, self_colour):
        return remove_danger_slow(moves, board, self_colour)

    pinned = board.find_pins(self_colour)
    if not pinned:
        return moves

    legal = []
    for move in moves:
        frm = from_square(move)
        if frm not in pinned or to_square(move) in pinned[frm]:
            legal.append(move)
    return legal


def remove_danger_slow(moves, board, self_colour):
    i = 0
    while i < len(moves):
        move = moves[i]
        board.make_move(move)
        king_bb = board.bitboard[self_colour + KING]
        king_sq = king_bb.bit_length() - 1
        in_check = under_attack(king_sq, board, self_colour)
        board.unmake_move()
        if in_check:
            del moves[i]
        else:
            i += 1
    return moves
