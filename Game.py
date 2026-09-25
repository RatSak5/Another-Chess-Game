import os
import sys

import pygame

import Board
import Const
import Theme
from Calc_moves import (
    area_moves,
    castle_moves,
    diagonal_moves,
    en_pessent,
    knight_moves,
    pawn_moves,
    promotion_moves,
    straightline_moves,
)
from Utils import (
    colour,
    flag,
    get_piece_img,
    piece,
    promotion_piece,
    to_square,
)


class Game:
    def __init__(self):
        self.board = Board.Board()
        self.theme = Theme.Formal()  # Theme.Brown()
        self.squares = 0
        self.highlighted_moves = []
        self.selected_piece = 0

    def _show_bg(self, surface):
        for pos in range(64):
            row, col = pos // 8, pos % 8

            if (self.squares >> 2 * pos) & (2**2 - 1) == 0:  #  0 - NORMAL
                colour_ = self.theme.dark if (row + col) % 2 == 0 else self.theme.light
            if (self.squares >> 2 * pos) & (2**2 - 1) == 1:  #  1 - SELECTED
                colour_ = (
                    self.theme.selected_dark
                    if (row + col) % 2 == 0
                    else self.theme.selected_light
                )
            if (self.squares >> 2 * pos) & (2**2 - 1) == 2:  #  2 - MOVE
                colour_ = (
                    self.theme.move_dark
                    if (row + col) % 2 == 0
                    else self.theme.move_light
                )

            temp_rect = pygame.Rect(
                Const.SQLENGTH * col,
                Const.SQLENGTH * row,
                Const.SQLENGTH,
                Const.SQLENGTH,
            )
            pygame.draw.rect(surface, colour_, temp_rect)

    def _show_pieces(self, surface):
        for pos in range(64):
            row, col = pos // 8, pos % 8

            piece_ = self.board.find_piece(pos)
            if piece_:
                img = get_piece_img(piece_)
                image = pygame.image.load(img)
                img_center = (
                    col * Const.SQLENGTH + Const.SQLENGTH // 2,
                    row * Const.SQLENGTH + Const.SQLENGTH // 2,
                )
                img_rect = image.get_rect(center=img_center)
                surface.blit(image, img_rect)

    def select_square(self, pos):
        shift = 2 * pos
        self.squares &= ~(0b11 << shift)  # clear both bits for square
        self.squares |= 0b01 << shift
        piece_ = self.board.find_piece(pos)

        if piece_ and colour(piece_) == self.board.colour:
            self.update_highlighted_moves(pos)
            self.selected_piece = self.board.find_piece(pos)
            for move in self.highlighted_moves:
                to_pos = to_square(move)
                self.move_square(to_pos)

    def update_highlighted_moves(self, pos):
        piece_ = self.board.find_piece(pos)
        if piece(piece_) == Const.PAWN:
            self.highlighted_moves += pawn_moves(pos, self.board)
            if (pos // 8 == 3 and colour(piece_) == Const.WHITE) or (
                pos // 8 == 4 and colour(piece_) == Const.BLACK
            ):
                self.highlighted_moves += en_pessent(
                    pos,
                    self.board,
                    last_move=self.board.last_move["move"],
                    last_piece=self.board.last_move["piece"],
                )

            elif (pos // 8 == 1 and colour(piece_) == Const.WHITE) or (
                pos // 8 == 6 and colour(piece_) == Const.BLACK
            ):
                self.highlighted_moves += promotion_moves(pos, self.board)

        if piece(piece_) == Const.ROOK:
            self.highlighted_moves += straightline_moves(pos, self.board)

        if piece(piece_) == Const.BISHOP:
            self.highlighted_moves += diagonal_moves(pos, self.board)

        if piece(piece_) == Const.QUEEN:
            self.highlighted_moves += straightline_moves(pos, self.board)
            self.highlighted_moves += diagonal_moves(pos, self.board)

        if piece(piece_) == Const.KING:
            self.highlighted_moves += area_moves(pos, self.board)
            self.highlighted_moves += castle_moves(pos, self.board)

        if piece(piece_) == Const.KNIGHT:
            self.highlighted_moves += knight_moves(pos, self.board)

    def play_move(self, pos, promotion_piece_=0):
        for move in self.highlighted_moves:
            if to_square(move) == pos:
                promotion_row = 0 if self.board.colour == Const.WHITE else 7
                if (
                    promotion_piece_ == promotion_piece(move)
                    and pos // 8 == promotion_row
                    and flag(move) == Const.PROMOTION
                ) or promotion_piece_ == 0:
                    self.board.make_move(move)
                    self.highlighted_moves = []
                    return True

        self.highlighted_moves = []
        return False

    def move_square(self, pos):
        shift = 2 * pos
        self.squares &= ~(0b11 << shift)  # clear both bits for square
        self.squares |= 0b10 << shift

    def clear_all(self):
        self.highlighted_moves = []
        self.squares = 0
        self.selected_piece = 0

    def state(self, pos):
        return (self.squares >> 2 * pos) & (2**2 - 1)

    def show_promotion_menu(self, surface, colour_):
        options = ["queen", "rook", "bishop", "knight"]
        rects = []

        blit_colour = "white" if colour_ == Const.WHITE else "black"

        menu_width = 4 * Const.SQLENGTH
        menu_height = Const.SQLENGTH
        start_x = (Const.WIDTH - menu_width) // 2
        start_y = (Const.LENGTH - menu_height) // 2

        pygame.draw.rect(
            surface, (240, 240, 240), (start_x, start_y, menu_width, menu_height)
        )
        pygame.draw.rect(
            surface, (0, 0, 0), (start_x, start_y, menu_width, menu_height), 4
        )

        for i, piece_ in enumerate(options):
            img_path = os.path.join(
                f"assets\\images\\imgs-80px\\{blit_colour}_{piece_}.png"
            )
            image = pygame.image.load(img_path)

            # Center image
            rect = image.get_rect(
                center=(
                    start_x + i * Const.SQLENGTH + Const.SQLENGTH // 2,
                    start_y + Const.SQLENGTH // 2,
                )
            )
            rects.append(rect)
            surface.blit(image, rect)

        pygame.display.update()

        encode = {
            "queen": Const.QUEEN,
            "bishop": Const.BISHOP,
            "rook": Const.ROOK,
            "knight": Const.KNIGHT,
        }

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(mouse_pos):
                            return encode[options[i]]
