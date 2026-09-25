import sys

import pygame

import Const
import Game


class Main:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((Const.WIDTH, Const.LENGTH))
        self.game = Game.Game()
        pygame.display.set_caption("Chess")

    def mainloop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    row, col = (
                        pygame.mouse.get_pos()[1] // Const.SQLENGTH,
                        pygame.mouse.get_pos()[0] // Const.SQLENGTH,
                    )
                    pos = row * 8 + col
                    if self.game.state(pos) == Const.NORMAL_:
                        self.game.clear_all()
                        self.game.select_square(pos)

                    elif self.game.state(pos) == Const.SELECTED:
                        self.game.clear_all()

                    elif self.game.state(pos) == Const.MOVE:
                        promotion_row = (
                            0 if self.game.board.colour == Const.WHITE else 7
                        )
                        promotion_piece = 0
                        if (
                            pos // 8 == promotion_row
                            and self.game.selected_piece
                            == self.game.board.colour + Const.PAWN
                        ):
                            promotion_piece = self.game.show_promotion_menu(
                                self.surface, self.game.board.colour
                            )

                        played = self.game.play_move(
                            pos, promotion_piece_=promotion_piece
                        )
                        if played:
                            self.game.clear_all()
                            status = self.game.board.game_over_status()

                            if status == 2:
                                print("checkmate")
                            elif status == 1:
                                print("stalemate")

            self.game._show_bg(self.surface)
            self.game._show_pieces(self.surface)

            pygame.display.update()


if __name__ == "__main__":
    main = Main()
    main.mainloop()
