from __future__ import annotations

import random

from typing import List, Optional, Dict


HUMAN = "O"
AI = "X"
EMPTY = " "

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # cols
    (0, 4, 8), (2, 4, 6)              # diagonals
]

def print_board(b: List[str]) -> None:
    def cell(i: int) -> str:
        return b[i] if b[i] != EMPTY else str(i+1)
    rows = [
        f" {cell(0)} | {cell(1)} | {cell(2)} ",
        f" {cell(3)} | {cell(4)} | {cell(5)} ",
        f" {cell(6)} | {cell(7)} | {cell(8)} ",
    ]
    print("\n---+---+---\n".join(rows))

def winner(b: List[str]) -> Optional[str]:
    for a, c, d in WIN_LINES:
        if b[a] != EMPTY and b[a] == b[c] == b[d]:
            return b[a]
    return None

def is_draw(b: List[str]) -> bool:
    return winner(b) is None and all(x != EMPTY for x in b)

def available_moves(b: List[str]) -> List[int]:
    return [i for i, x in enumerate(b) if x == EMPTY]

def winning_moves(b: List[str], player: str) -> List[int]:
    """Returns moves (indices) that make 'player' win immediately."""
    wins = []
    for m in available_moves(b):
        b[m] = player
        if winner(b) == player:
            wins.append(m)
        b[m] = EMPTY
    return wins


def board_key(b: List[str], turn: str) -> str:
    return "".join(b) + turn

def minimax(b: List[str], turn: str, memo: Dict[str, int]) -> int:
    w = winner(b)
    if w == AI:
        return 1
    if w == HUMAN:
        return -1
    if is_draw(b):
        return 0

    key = board_key(b, turn)
    if key in memo:
        return memo[key]

    moves = available_moves(b)

    if turn == AI:
        best = -10
        for m in moves:
            b[m] = AI
            score = minimax(b, HUMAN, memo)
            b[m] = EMPTY
            best = max(best, score)
        memo[key] = best
        return best
    else:
        best = 10
        for m in moves:
            b[m] = HUMAN
            score = minimax(b, AI, memo)
            b[m] = EMPTY
            best = min(best, score)
        memo[key] = best
        return best

def best_ai_move(b: List[str]) -> int:
    memo: Dict[str, int] = {}
    best_score = -10
    best_move = -1

    # Threats BEFORE AI moves: can HUMAN win immediately?
    human_threats_now = winning_moves(b, HUMAN)
    if human_threats_now:
        threats_str = ", ".join(str(x+1) for x in human_threats_now)
        print(f"\n⚠ HUMAN threatens to win at: {threats_str}")

    print("\nAI is thinking...")

    for m in available_moves(b):
        # Try AI move
        b[m] = AI

        # 1) Immediate win check
        if winner(b) == AI:
            print(f"Move {m+1} → ✅ immediate win")
            b[m] = EMPTY
            print(f"Chosen move: {m+1}\n")
            return m

        # 2) After this AI move, can HUMAN win immediately?
        human_wins_next = winning_moves(b, HUMAN)

        # 3) Normal minimax score
        score = minimax(b, HUMAN, memo)

        # Undo AI move
        b[m] = EMPTY

        flags = []
        # If this move blocks an existing immediate threat, it will be one of the threat squares
        if m in human_threats_now:
            flags.append("✅ blocks threat")

        if human_wins_next:
            wins_str = ", ".join(str(x+1) for x in human_wins_next)
            flags.append(f"⚠ allows HUMAN win next at: {wins_str}")

        if flags:
            print(f"Move {m+1} → score {score}  " + " | ".join(flags))
        else:
            print(f"Move {m+1} → score {score}")

        if score > best_score:
            best_score = score
            best_move = m

    print(f"Chosen move: {best_move+1}\n")
    return best_move

def choose_ai_move(b: List[str], difficulty: str) -> int:
    """
    Siempre calcula scores (best_ai_move imprime pensamiento).
    Luego decide si juega perfecto o si 'se equivoca' según dificultad.
    """
    # Primero: calculo perfecto (y además imprime todo)
    best = best_ai_move(b)

    # Si es hard: siempre perfecto
    if difficulty == "hard":
        return best

    moves = available_moves(b)
    if len(moves) == 1:
        return best

    # Probabilidad de jugar perfecto
    if difficulty == "medium":
        p_best = 0.7
    else:  # easy
        p_best = 0.35

    # Decide
    if random.random() < p_best:
        print(f"AI ({difficulty}) chooses the BEST move.\n")
        return best

    # "Se equivoca": elige otro movimiento válido distinto al mejor
    other_moves = [m for m in moves if m != best]
    mistake = random.choice(other_moves)
    print(f"AI ({difficulty}) makes a mistake and chooses {mistake+1} instead of {best+1}.\n")
    return mistake


def ask_human_move(b: List[str]) -> int:
    while True:
        s = input("Choose a position (1-9): ").strip()
        if not s.isdigit():
            print("Please type a number 1-9.")
            continue
        pos = int(s) - 1
        if pos < 0 or pos > 8:
            print("Out of range. Use 1-9.")
            continue
        if b[pos] != EMPTY:
            print("That spot is taken.")
            continue
        return pos
    
def choose_starting_player() -> str:
    while True:
        s = input("Who starts? (H)uman / (A)I: ").strip().lower()
        if s in ("h", "human"):
            return HUMAN
        if s in ("a", "ai"):
            return AI
        print("Please type H or A.")

def choose_difficulty() -> str:
    while True:
        s = input("Choose difficulty: (E)asy / (M)edium / (H)ard: ").strip().lower()
        if s in ("e", "easy"):
            return "easy"
        if s in ("m", "medium"):
            return "medium"
        if s in ("h", "hard"):
            return "hard"
        print("Please type E, M, or H.")

def main() -> None:
    DEMO = False  # False para jugar normal

    if DEMO:
        b = [HUMAN, HUMAN, EMPTY,
             EMPTY, AI, EMPTY,
             EMPTY, EMPTY, EMPTY]
    else:
        b = [EMPTY] * 9

    print("Tic-Tac-Toe: You are O, AI is X.\n")
    print_board(b)

    turn = choose_starting_player()  # <-- ESTA es la línea nueva

    difficulty = choose_difficulty()

    while True:
        if turn == HUMAN:
            move = ask_human_move(b)
            b[move] = HUMAN
        
        else:
            move = choose_ai_move(b, difficulty)   # <-- siempre acá
            b[move] = AI                           # <-- siempre aplica al tablero
            print(f"\nAI plays at {move+1}")        # <-- siempre imprime

        print()
        print_board(b)

        w = winner(b)
        if w is not None:
            print("\nResult:", "AI wins." if w == AI else "You win!")
            break
        if is_draw(b):
            print("\nResult: Draw.")
            break

        turn = HUMAN if turn == AI else AI

if __name__ == "__main__":
    main()
