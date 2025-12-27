import pygame, sys, random, math

# ================= INITIALIZATION =================
pygame.init()
W, H = 480, 750
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Tic Tac Toe • Nova Glass")
clock = pygame.time.Clock()

# ================= THEME COLORS =================
BG_DARK = (8, 10, 20)
BG_LIGHT = (20, 30, 60)
GLASS_BASE = (255, 255, 255, 25)
GLASS_BRIGHT = (255, 255, 255, 60)

X_COLOR = (255, 70, 110)   # Neon Pink/Red
O_COLOR = (0, 210, 255)    # Electric Blue
WIN_GLOW = (100, 255, 180) # Matrix Green
WHITE = (245, 245, 255)
GOLD = (255, 215, 0)

# ================= FONTS =================
font_main = pygame.font.SysFont("Verdana", 42, bold=True)
font_score = pygame.font.SysFont("Verdana", 18, bold=True)
font_ui = pygame.font.SysFont("Verdana", 22, bold=True)

# ================= GAME DATA =================
board = [None] * 9
turn = "X"
winner = None
win_cells = None
mode = None 
difficulty = None
scores = {"X": 0, "O": 0, "Draw": 0}
scales = [0.0] * 9

# ================= UTILS =================
def draw_bg():
    for i in range(H):
        r = BG_DARK[0] + (BG_LIGHT[0] - BG_DARK[0]) * i // H
        g = BG_DARK[1] + (BG_LIGHT[1] - BG_DARK[1]) * i // H
        b = BG_DARK[2] + (BG_LIGHT[2] - BG_DARK[2]) * i // H
        pygame.draw.line(screen, (r, g, b), (0, i), (W, i))

def cell_rect(i):
    return pygame.Rect(60 + (i % 3) * 120, 250 + (i // 3) * 120, 120, 120)

def restart_game():
    global board, turn, winner, win_cells, scales
    board = [None] * 9
    turn = "X"
    winner = None
    win_cells = None
    scales = [0.0] * 9

# ================= AI LOGIC =================
def check_state(b):
    combos = [(0,1,2),(3,4,5),(6,7,8), (0,3,6),(1,4,7),(2,5,8), (0,4,8),(2,4,6)]
    for a,b_idx,c in combos:
        if b[a] and b[a] == b[b_idx] == b[c]:
            return b[a], (a,b_idx,c)
    if all(x is not None for x in b): return "DRAW", None
    return None, None

def minimax(b, depth, is_maxing):
    res, _ = check_state(b)
    if res == "O": return 10 - depth
    if res == "X": return depth - 10
    if res == "DRAW": return 0

    if is_maxing:
        best = -1000
        for i in range(9):
            if b[i] is None:
                b[i] = "O"
                best = max(best, minimax(b, depth + 1, False))
                b[i] = None
        return best
    else:
        best = 1000
        for i in range(9):
            if b[i] is None:
                b[i] = "X"
                best = min(best, minimax(b, depth + 1, True))
                b[i] = None
        return best

def get_ai_move():
    if difficulty == "Easy":
        empty = [i for i, v in enumerate(board) if v is None]
        return random.choice(empty) if empty else None
    
    best_val = -1000
    move = -1
    for i in range(9):
        if board[i] is None:
            board[i] = "O"
            move_val = minimax(board, 0, False)
            board[i] = None
            if move_val > best_val:
                move = i
                best_val = move_val
    return move

# ================= CORE LOOP =================
while True:
    draw_bg()
    m_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if mode is None:
                if pygame.Rect(90, 300, 300, 60).collidepoint(m_pos): mode = "PVP"
                if pygame.Rect(90, 380, 300, 60).collidepoint(m_pos): mode = "AI"
            elif mode == "AI" and difficulty is None:
                if pygame.Rect(90, 300, 300, 60).collidepoint(m_pos): difficulty = "Easy"; restart_game()
                if pygame.Rect(90, 380, 300, 60).collidepoint(m_pos): difficulty = "Hard"; restart_game()
            elif not winner and turn == "X":
                for i in range(9):
                    if cell_rect(i).collidepoint(m_pos) and board[i] is None:
                        board[i] = "X"
                        winner, win_cells = check_state(board)
                        if winner: scores[winner] += 1
                        turn = "O"
            if (winner or all(board)) and pygame.Rect(140, 650, 200, 50).collidepoint(m_pos):
                restart_game()

    # AI Turn
    if mode == "AI" and turn == "O" and not winner:
        pygame.time.delay(600)
        move = get_ai_move()
        if move is not None:
            board[move] = "O"
            winner, win_cells = check_state(board)
            if winner: scores[winner] += 1
            turn = "X"

    # ================= UI DESIGN =================
    # Score Header
    s_bg = pygame.Surface((400, 80), pygame.SRCALPHA)
    pygame.draw.rect(s_bg, GLASS_BASE, (0, 0, 400, 80), border_radius=20)
    screen.blit(s_bg, (40, 30))
    
    x_score = font_score.render(f"PLAYER X: {scores['X']}", True, X_COLOR)
    o_score = font_score.render(f"PLAYER O: {scores['O']}", True, O_COLOR)
    d_score = font_score.render(f"DRAWS: {scores['Draw']}", True, WHITE)
    screen.blit(x_score, (70, 60)); screen.blit(d_score, (200, 60)); screen.blit(o_score, (310, 60))

    if mode is None:
        txt = font_main.render("Select Mode", True, WHITE)
        screen.blit(txt, (W//2 - txt.get_width()//2, 200))
        for y, l in [(300, "Local PVP"), (380, "Computer AI")]:
            r = pygame.Rect(90, y, 300, 60)
            pygame.draw.rect(screen, WHITE if r.collidepoint(m_pos) else GLASS_BRIGHT, r, border_radius=15)
            lbl = font_ui.render(l, True, BG_DARK if r.collidepoint(m_pos) else WHITE)
            screen.blit(lbl, (r.centerx - lbl.get_width()//2, r.centery - lbl.get_height()//2))

    elif mode == "AI" and difficulty is None:
        txt = font_main.render("Difficulty", True, WHITE)
        screen.blit(txt, (W//2 - txt.get_width()//2, 200))
        for y, l in [(300, "Relaxed (Easy)"), (380, "God Mode (Hard)")]:
            r = pygame.Rect(90, y, 300, 60)
            pygame.draw.rect(screen, WHITE if r.collidepoint(m_pos) else GLASS_BRIGHT, r, border_radius=15)
            lbl = font_ui.render(l, True, BG_DARK if r.collidepoint(m_pos) else WHITE)
            screen.blit(lbl, (r.centerx - lbl.get_width()//2, r.centery - lbl.get_height()//2))

    else:
        # Drawing Board
        for i in range(9):
            r = cell_rect(i)
            # Glass Effect
            c = GLASS_BRIGHT if r.collidepoint(m_pos) and not board[i] else GLASS_BASE
            pygame.draw.rect(screen, c, r.inflate(-10, -10), border_radius=20)
            
            if board[i]:
                if scales[i] < 1.0: scales[i] += 0.15
                sz = int(40 * scales[i])
                if board[i] == "X":
                    pygame.draw.line(screen, X_COLOR, (r.centerx-sz, r.centery-sz), (r.centerx+sz, r.centery+sz), 14)
                    pygame.draw.line(screen, X_COLOR, (r.centerx+sz, r.centery-sz), (r.centerx-sz, r.centery+sz), 14)
                else:
                    pygame.draw.circle(screen, O_COLOR, r.center, sz, 12)

        # Winning Glow
        if win_cells:
            p1, p3 = cell_rect(win_cells[0]).center, cell_rect(win_cells[2]).center
            pygame.draw.line(screen, WIN_GLOW, p1, p3, 15)

        # Bottom Status
        status_msg = f"Match is Draw! 🤝" if winner == "DRAW" else f"{winner} Wins! 🏆" if winner else f"{turn}'s Turn"
        st_color = WIN_GLOW if winner else WHITE
        st_txt = font_ui.render(status_msg, True, st_color)
        screen.blit(st_txt, (W//2 - st_txt.get_width()//2, 610))

        if winner or all(board):
            btn = pygame.Rect(140, 660, 200, 50)
            pygame.draw.rect(screen, WHITE, btn, border_radius=15)
            btn_txt = font_ui.render("Play Again", True, BG_DARK)
            screen.blit(btn_txt, (btn.centerx - btn_txt.get_width()//2, btn.centery - btn_txt.get_height()//2))

    pygame.display.flip()
    clock.tick(60)