# Chess

A two-player chess game built from scratch in Python with [Pygame](https://www.pygame.org/), featuring a click-to-move graphical board, full rule enforcement (castling, en passant, pawn promotion, check/checkmate/stalemate detection), and a bitboard-based board representation for fast move generation.

## Features

- **Full chess rules** : legal move generation for all pieces, castling (both sides), en passant, and pawn promotion with an in-game piece-selection menu.
- **Check, checkmate & stalemate detection** : the game inspects the king's attacked squares and available legal moves each turn to determine game-over conditions.
- **Bitboard board representation** : each piece type/colour is stored as a 64-bit integer bitboard, and moves are encoded into a single integer (`flag | promotion piece | to-square | from-square`) for compact, efficient state updates and undo.
- **Move make/unmake** : a full `make_move` / `unmake_move` pipeline that reversibly applies moves (including captures, castling rook shifts, en passant captures, and promotions), which lays the groundwork for search-based engines.
- **Pin detection** : ray-casting from the king in all 8 directions to identify absolutely pinned pieces.
- **Click-based UI** : select a piece, see its legal destinations highlighted on the board, and click to move; two selectable board themes (Formal green and Brown wood).

## Project structure

```
.
├── Main.py         # Entry point: window setup, Pygame event loop, promotion menu trigger
├── Game.py         # Game/UI state: square selection, highlighting, rendering board & pieces
├── Board.py        # Core chess logic: bitboards, make/unmake move, move generation, pin detection
├── Calc_moves.py   # Per-piece move generators (sliding, knight, king, pawn, castling, en passant)
├── Piece.py        # Piece classes (King, Queen, Rook, Bishop, Knight, Pawn) and sprite lookup
├── Utils.py        # Bit-packing helpers: encode/decode moves, row/col/colour/piece extraction
├── Const.py        # Shared constants: board size, piece codes, move flags, bitmasks
├── Theme.py        # Board colour themes (Formal, Brown)
└── assets/images/  # Piece sprites (80px PNGs, white/black × 6 piece types)
```

## How it works

### Encoding a piece

Each square (0–63, row-major from the top-left) can hold a *piece code* that packs colour and piece type into one integer using disjoint bit ranges:

| | Value | Binary |
|---|---|---|
| `WHITE` | 8 | `01000` |
| `BLACK` | 16 | `10000` |
| `PAWN`…`KING` | 1–6 | `00001`…`00110` |

Colour occupies the upper bits, piece type the lower 3 bits, so `colour + piece_type` never overlaps and can be decomposed again with a mask:

```python
def colour(piece_enc):
    return piece_enc & ~(2**3 - 1)   # clears the low 3 bits -> just the colour

def piece(piece_enc):
    return piece_enc & (2**3 - 1)    # keeps only the low 3 bits -> just the piece type
```

So a white knight (`WHITE=8, KNIGHT=2`) is encoded as `8 + 2 = 10` (binary `01010`); `colour(10) == 8` and `piece(10) == 2` recover the two parts. This is what lets `Board.bitboard` use a single dict key like `WHITE + PAWN` for "white pawns."

### Bitboards

Rather than a list/array of 64 squares, the board keeps **one 64-bit integer per piece type per colour** (12 integers total: 6 piece types × 2 colours). Bit *i* of a bitboard is `1` if that piece occupies square *i*, else `0`. For example, the starting white pawns occupy squares 48–55 (the second-to-last row), so:

```python
self.bitboard[WHITE + PAWN] = (2**8 - 1) << 48   # 8 set bits, shifted to squares 48-55
```

Looking up what's on a square (`find_piece`) scans the 12 bitboards and tests bit `position` of each:

```python
def find_piece(self, position):
    for piece_code, bb in self.bitboard.items():
        if (bb >> position) & 1:
            return piece_code
    return 0
```

Placing/removing a piece is a single bitwise operation instead of a list mutation — e.g. moving a piece off `from_square` and onto `to_square`:

```python
self.bitboard[move_piece] &= ~(1 << from_square)   # clear the old bit
self.bitboard[move_piece] |= (1 << to_square)       # set the new bit
```

Iterating over "every square this piece type occupies" (used heavily by move generation) is done bit-by-bit with the classic *isolate-lowest-set-bit* trick, so no square list needs to be maintained separately from the bitboard:

```python
def iter_bits(self, bb):
    while bb:
        lsb = bb & -bb               # isolates the lowest set bit (two's-complement trick)
        sq = lsb.bit_length() - 1    # bit position -> square index
        yield sq
        bb ^= lsb                    # clear that bit and continue
```

### Encoding a move

A move (from-square, to-square, promotion piece, and special-move flag) is packed into one 17-bit integer instead of a tuple or object, using the following layout (least-significant bit on the right):

```
 flag(2) | promotion_piece(3) | to_square(6) | from_square(6)
   15..16      12..14              6..11           0..5
```

```python
def encode_move(from_square, to_square, flag=NORMAL, promotion_piece=0):
    return (flag << 15) + (promotion_piece << 12) + (to_square << 6) + from_square
```

Each field is later pulled back out with a precomputed mask and a shift (`Const.py` defines `FROM_SQUARE_MASK`, `TO_SQUARE_MASK`, `PROMOTION_PIECE_MASK`, `FLAG_MASK`):

```python
def to_square(move):
    return (move & TO_SQUARE_MASK) >> 6

def flag(move):
    return (move & FLAG_MASK) >> 15
```

`flag` distinguishes the four move kinds the engine needs to treat specially: `NORMAL = 0`, `EN_PESSANT = 1`, `CASTLE = 2`, `PROMOTION = 3`. Packing a move into one integer (rather than an object) makes it cheap to store, compare, and pass around — the same trick applies to `Game.squares`, which packs a 2-bit *display state* (normal/selected/highlighted) per square into one big integer using `squares >> 2*pos & 0b11`.

### Board state, make/unmake, and history

- **The board** stores the 12 bitboards described above; `find_piece` scans them to look up a square's occupant, and `make_move`/`unmake_move` flip the relevant bits.
- **`make_move`** branches on the move's `flag` to apply the right bit updates: a normal move clears the old bit and sets the new one (and clears the captured piece's bit if any); castling additionally moves the rook's bits; en passant removes the captured pawn from a square *other* than `to_square`; promotion clears the pawn's bit and sets the *promoted* piece's bit instead. Before mutating anything, it pushes an `unmake_data` record (captured piece, prior castling rights, prior en passant file, previous record) onto a linked stack so the move can be reversed exactly.
- **`unmake_move`** pops that record and replays the inverse bit operations, restoring captured pieces, castling rights, and en passant state.
- **Move generation** (`Calc_moves.py`) walks rays for sliding pieces (rook/bishop/queen), fixed offsets for knights/kings, and handles pawn pushes, captures, en passant, promotion, and castling as special cases, using `Board.find_piece`/bitboards to test occupancy along the way.
- **Pin detection** (`Board.find_pins`) casts a ray from the king in each of the 8 directions; if it hits exactly one friendly piece and then an enemy slider that attacks along that direction, that friendly piece is recorded as pinned to the set of squares on the ray.
- **The UI loop** (`Main.py`/`Game.py`) translates mouse clicks into board squares, asks `Board` for legal moves from the selected square, highlights them, and applies the chosen move — showing a promotion picker when a pawn reaches the back rank.

## Getting started

### Requirements
- Python 3.9+
- [Pygame](https://www.pygame.org/)

### Installation
```bash
pip install pygame
```

### Run
```bash
python Main.py
```

A window opens with the starting position. Click a piece to see its legal moves highlighted, then click a highlighted square to move. Promoting a pawn opens a small menu to pick the new piece.

## Roadmap / possible extensions

- AI opponent (minimax/alpha-beta search, evaluation function)
- Move history / algebraic notation log
- Undo/redo via the existing `unmake_move` method
- Draw detection by repetition and the 50-move rule
- On-screen check/checkmate/stalemate banners (currently printed to the console)

## License

[MIT](LICENSE)
