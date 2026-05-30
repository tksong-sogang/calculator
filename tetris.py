import tkinter as tk
import random
import time

COLS, ROWS = 10, 20
CELL = 30
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL
SIDEBAR = 160
FPS = 60

COLORS = {
    'I': '#00f0f0',
    'O': '#f0f000',
    'T': '#a000f0',
    'S': '#00f000',
    'Z': '#f00000',
    'J': '#0000f0',
    'L': '#f0a000',
    'ghost': '#333333',
    'bg': '#1a1a2e',
    'grid': '#16213e',
    'sidebar': '#0f3460',
    'text': '#e0e0e0',
}

SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
}

SCORES = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}

def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

class Piece:
    def __init__(self, name=None):
        self.name = name or random.choice(list(SHAPES.keys()))
        self.shape = [row[:] for row in SHAPES[self.name]]
        self.color = COLORS[self.name]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotated(self):
        p = Piece(self.name)
        p.shape = rotate(self.shape)
        p.x, p.y = self.x, self.y
        p.color = self.color
        return p

class Tetris:
    def __init__(self, root):
        self.root = root
        self.root.title('Tetris')
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS['bg'])

        frame = tk.Frame(root, bg=COLORS['bg'])
        frame.pack(padx=10, pady=10)

        self.canvas = tk.Canvas(frame, width=WIDTH, height=HEIGHT,
                                bg=COLORS['bg'], highlightthickness=2,
                                highlightbackground='#e94560')
        self.canvas.grid(row=0, column=0)

        self.side = tk.Canvas(frame, width=SIDEBAR, height=HEIGHT,
                              bg=COLORS['sidebar'], highlightthickness=0)
        self.side.grid(row=0, column=1, padx=(8, 0))

        self.root.bind('<Left>', lambda e: self.move(-1, 0))
        self.root.bind('<Right>', lambda e: self.move(1, 0))
        self.root.bind('<Down>', lambda e: self.move(0, 1))
        self.root.bind('<Up>', lambda e: self.try_rotate())
        self.root.bind('<space>', lambda e: self.hard_drop())
        self.root.bind('<p>', lambda e: self.toggle_pause())
        self.root.bind('<P>', lambda e: self.toggle_pause())
        self.root.bind('<r>', lambda e: self.restart())
        self.root.bind('<R>', lambda e: self.restart())

        self.new_game()

    def new_game(self):
        self.board = [[None] * COLS for _ in range(ROWS)]
        self.score = 0
        self.level = 1
        self.lines = 0
        self.paused = False
        self.game_over = False
        self.bag = []
        self.current = self.next_piece()
        self.next = self.next_piece()
        self.interval = 800
        self.last_fall = time.time() * 1000
        self.update()

    def restart(self):
        self.new_game()

    def next_piece(self):
        if not self.bag:
            self.bag = list(SHAPES.keys()) * 2
            random.shuffle(self.bag)
        return Piece(self.bag.pop())

    def toggle_pause(self):
        if self.game_over:
            return
        self.paused = not self.paused

    def valid(self, piece, dx=0, dy=0, shape=None):
        s = shape or piece.shape
        for r, row in enumerate(s):
            for c, cell in enumerate(row):
                if cell:
                    nx, ny = piece.x + c + dx, piece.y + r + dy
                    if nx < 0 or nx >= COLS or ny >= ROWS:
                        return False
                    if ny >= 0 and self.board[ny][nx]:
                        return False
        return True

    def move(self, dx, dy):
        if self.paused or self.game_over:
            return
        if self.valid(self.current, dx, dy):
            self.current.x += dx
            self.current.y += dy
            return True
        return False

    def try_rotate(self):
        if self.paused or self.game_over:
            return
        rotated = self.current.rotated()
        for kick in [0, 1, -1, 2, -2]:
            if self.valid(rotated, kick, 0):
                rotated.x += kick
                self.current = rotated
                return

    def hard_drop(self):
        if self.paused or self.game_over:
            return
        while self.move(0, 1):
            pass
        self.lock()

    def ghost_y(self):
        dy = 0
        while self.valid(self.current, 0, dy + 1):
            dy += 1
        return self.current.y + dy

    def lock(self):
        for r, row in enumerate(self.current.shape):
            for c, cell in enumerate(row):
                if cell:
                    ny = self.current.y + r
                    nx = self.current.x + c
                    if ny < 0:
                        self.game_over = True
                        return
                    self.board[ny][nx] = self.current.color

        cleared = 0
        new_board = [row for row in self.board if any(cell is None for cell in row)]
        cleared = ROWS - len(new_board)
        self.board = [[None] * COLS for _ in range(cleared)] + new_board

        self.lines += cleared
        self.score += SCORES.get(cleared, 0) * self.level
        self.level = self.lines // 10 + 1
        self.interval = max(100, 800 - (self.level - 1) * 70)

        self.current = self.next
        self.next = self.next_piece()

        if not self.valid(self.current):
            self.game_over = True

    def update(self):
        if not self.game_over and not self.paused:
            now = time.time() * 1000
            if now - self.last_fall >= self.interval:
                if not self.move(0, 1):
                    self.lock()
                self.last_fall = now

        self.draw()
        self.root.after(1000 // FPS, self.update)

    def draw_cell(self, canvas, x, y, color, size=CELL, offset_x=0, offset_y=0):
        x1 = offset_x + x * size + 1
        y1 = offset_y + y * size + 1
        x2 = offset_x + x * size + size - 1
        y2 = offset_y + y * size + size - 1
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')
        canvas.create_rectangle(x1, y1, x1 + size - 3, y1 + 3, fill='white', outline='', stipple='gray25')
        canvas.create_rectangle(x1, y1, x1 + 3, y1 + size - 3, fill='white', outline='', stipple='gray25')

    def draw(self):
        self.canvas.delete('all')
        self.side.delete('all')

        # grid lines
        for r in range(ROWS + 1):
            self.canvas.create_line(0, r * CELL, WIDTH, r * CELL, fill=COLORS['grid'])
        for c in range(COLS + 1):
            self.canvas.create_line(c * CELL, 0, c * CELL, HEIGHT, fill=COLORS['grid'])

        # board
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c]:
                    self.draw_cell(self.canvas, c, r, self.board[r][c])

        if not self.game_over:
            # ghost
            gy = self.ghost_y()
            for r, row in enumerate(self.current.shape):
                for c, cell in enumerate(row):
                    if cell and gy + r != self.current.y + r:
                        x1 = (self.current.x + c) * CELL + 2
                        y1 = (gy + r) * CELL + 2
                        x2 = x1 + CELL - 3
                        y2 = y1 + CELL - 3
                        self.canvas.create_rectangle(x1, y1, x2, y2,
                                                     outline=self.current.color,
                                                     fill='', width=1)

            # current piece
            for r, row in enumerate(self.current.shape):
                for c, cell in enumerate(row):
                    if cell:
                        self.draw_cell(self.canvas, self.current.x + c,
                                       self.current.y + r, self.current.color)

        # sidebar
        self.side.create_text(SIDEBAR // 2, 20, text='TETRIS', fill='#e94560',
                              font=('Courier', 16, 'bold'))

        self.side.create_text(SIDEBAR // 2, 60, text='SCORE', fill=COLORS['text'],
                              font=('Courier', 11, 'bold'))
        self.side.create_text(SIDEBAR // 2, 80, text=str(self.score), fill='#f0f000',
                              font=('Courier', 14, 'bold'))

        self.side.create_text(SIDEBAR // 2, 115, text='LEVEL', fill=COLORS['text'],
                              font=('Courier', 11, 'bold'))
        self.side.create_text(SIDEBAR // 2, 135, text=str(self.level), fill='#00f0f0',
                              font=('Courier', 14, 'bold'))

        self.side.create_text(SIDEBAR // 2, 170, text='LINES', fill=COLORS['text'],
                              font=('Courier', 11, 'bold'))
        self.side.create_text(SIDEBAR // 2, 190, text=str(self.lines), fill='#a000f0',
                              font=('Courier', 14, 'bold'))

        self.side.create_text(SIDEBAR // 2, 230, text='NEXT', fill=COLORS['text'],
                              font=('Courier', 11, 'bold'))
        ns = self.next.shape
        nw, nh = len(ns[0]), len(ns)
        ox = (SIDEBAR - nw * CELL) // 2
        oy = 250
        for r, row in enumerate(ns):
            for c, cell in enumerate(row):
                if cell:
                    self.draw_cell(self.side, c, r, self.next.color, offset_x=ox, offset_y=oy)

        controls = [
            ('←→', 'Move'),
            ('↑', 'Rotate'),
            ('↓', 'Soft drop'),
            ('SPC', 'Hard drop'),
            ('P', 'Pause'),
            ('R', 'Restart'),
        ]
        y0 = HEIGHT - 160
        self.side.create_text(SIDEBAR // 2, y0, text='CONTROLS', fill=COLORS['text'],
                              font=('Courier', 9, 'bold'))
        for i, (key, action) in enumerate(controls):
            self.side.create_text(SIDEBAR // 2, y0 + 18 + i * 16,
                                  text=f'{key}: {action}', fill='#aaaaaa',
                                  font=('Courier', 8))

        if self.paused:
            self.canvas.create_rectangle(0, HEIGHT // 2 - 40, WIDTH, HEIGHT // 2 + 40,
                                         fill='#000000', outline='')
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 12, text='PAUSED',
                                    fill='#e94560', font=('Courier', 22, 'bold'))
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 18, text='Press P to resume',
                                    fill=COLORS['text'], font=('Courier', 11))

        if self.game_over:
            self.canvas.create_rectangle(0, HEIGHT // 2 - 50, WIDTH, HEIGHT // 2 + 50,
                                         fill='#000000', outline='')
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 20, text='GAME OVER',
                                    fill='#e94560', font=('Courier', 20, 'bold'))
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 15, text=f'Score: {self.score}',
                                    fill='#f0f000', font=('Courier', 14))
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 40, text='R: Restart',
                                    fill=COLORS['text'], font=('Courier', 11))

if __name__ == '__main__':
    root = tk.Tk()
    Tetris(root)
    root.mainloop()
