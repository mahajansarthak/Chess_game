from django.urls import path

from main.views import ChessCreateGame, ChessMove, ChessGetGame, ChessGetGameAtSpecificMove, ChessListGame, \
    CreatePlayer, ListPlayers

urlpatterns = [
    path("create_player/", CreatePlayer.as_view(), name="create_player"),
    path("list_players/", ListPlayers.as_view(), name="list_players"),
    path("create_game/", ChessCreateGame.as_view(), name="create_game"),
    path("list_games/", ChessListGame.as_view(), name="list_games"),
    path("make_move/", ChessMove.as_view(), name="make_move"),
    path("get_game_state/", ChessGetGame.as_view(), name="get_game_state"),
    path("get_game_state_at_move_num/", ChessGetGameAtSpecificMove.as_view(), name="get_game_state_at_move_num"),
]
