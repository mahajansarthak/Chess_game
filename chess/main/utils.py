import chess


def get_outcome_str(board):
    current_outcome = board.outcome()
    current_outcome_str = "Ongoing"
    if current_outcome != None: ##if game ended
        is_draw = current_outcome.winner == None 
        winner_mapper = {
            chess.WHITE: "White",
            chess.BLACK: "Black"
        }

        termination_mapper = {
            chess.Termination.CHECKMATE: "Checkmate",
            chess.Termination.STALEMATE: "Stalemate",
            chess.Termination.INSUFFICIENT_MATERIAL: "Insufficient Material",
        }

        if is_draw:
            current_outcome_str = f"Game is Draw, (by {termination_mapper[current_outcome.termination]})"
        else:
            current_outcome_str = f"{winner_mapper[current_outcome.winner]} won the Game, (by {termination_mapper[current_outcome.termination]})"

    return current_outcome_str