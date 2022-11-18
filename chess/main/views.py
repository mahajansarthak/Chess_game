import io
import traceback

################
import chess
import chess.pgn
from rest_framework import status, serializers ## create an api
from rest_framework.response import Response ##response an api
from rest_framework.views import APIView ##view an api


from main.models import ChessGame, User ##stored a chess game in table form
from main.utils import get_outcome_str ##

##Create Player Api
class CreatePlayer(APIView):
    class CreatePlayerSerializer(serializers.Serializer):
        first_name = serializers.CharField(required=True)
        last_name = serializers.CharField(required=True)
        email = serializers.EmailField(required=True)

    def post(self, request):
        serializer = self.CreatePlayerSerializer(data=request.data)
        if serializer.is_valid():
            first_name = serializer.validated_data.get("first_name")
            last_name = serializer.validated_data.get("last_name")
            email = serializer.validated_data.get("email")

            try:
                User.objects.get(email=email)
                return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                user = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=email)
                return Response({"id": user.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_200_OK)

##List Players
class ListPlayers(APIView):
    def get(self, request):
        data = User.objects.all().values("id", "first_name", "last_name", "email")
        response_data = {
            "data": data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


##Create Game Api
class ChessCreateGame(APIView):
    class ChessCreateSerializer(serializers.Serializer):
        black_player_id = serializers.IntegerField(required=True)
        white_player_id = serializers.IntegerField(required=True)

    def post(self, request):
        serializer = self.ChessCreateSerializer(data=request.data)
        if serializer.is_valid():
            black_player_id = serializer.validated_data.get("black_player_id")
            white_player_id = serializer.validated_data.get("white_player_id")
            if black_player_id == white_player_id:
                return Response({"error": "Players cannot be the same"}, status=status.HTTP_400_BAD_REQUEST)
            game_obj = ChessGame.objects.create(
                black_player_id=black_player_id,
                white_player_id=white_player_id
            )
            game = chess.pgn.Game()
            exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True) ##
            pgn_string = game.accept(exporter) ##
            game_obj.pgn = pgn_string ##pgn --> string --> save --> 
            print("pgn_string", pgn_string)
            game_obj.save()

            response_data = {
                "game_id": game_obj.id,
                "white_player_id":game_obj.white_player_id,
                "black_player_id":game_obj.black_player_id
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_200_OK)

##List
class ChessListGame(APIView):
    def get(self, request):
        data = ChessGame.objects.all().values("id", "status", "white_player_id", "black_player_id")
        response_data = {
            "data": data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


## Move
class ChessMove(APIView):
    class ChessMoveSerializer(serializers.Serializer):
        game_id = serializers.IntegerField(required=True)
        move = serializers.CharField(required=True)

    def post(self, request):
        serializer = self.ChessMoveSerializer(data=request.data)
        if serializer.is_valid():
            params = serializer.validated_data
            try:
                game_obj = ChessGame.objects.get(id=params["game_id"])
            except ChessGame.DoesNotExist:
                return Response({"error": "Game does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            pgn = io.StringIO(game_obj.pgn) ##string --> pgn
            game = chess.pgn.read_game(pgn) ##pgn save
            board = game.end().board()  ##last boad state
            try:
                board.push_san(params["move"])
            except Exception as e:
                print("ERROR", e)
                traceback.print_tb(e.__traceback__)
                response = {
                    "error": "Invalid move",
                    "legal_moves": [str(move) for move in board.legal_moves],
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            game = chess.pgn.Game.from_board(board)

            exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
            pgn_string = game.accept(exporter)
            game_obj.pgn = pgn_string 
            print("pgn_string",pgn_string)

            current_outcome_str = get_outcome_str(board) ##finding string
            game_obj.status = current_outcome_str
            game_obj.save()

            response_data = {
                "fen": game.end().board().fen(),
                "board_ascii": [line for line in (str(game.end().board())).splitlines()],
                "current-status": current_outcome_str
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

##Last State Game
class ChessGetGame(APIView):
    class ChessGetGameSerializer(serializers.Serializer):
        game_id = serializers.IntegerField(required=True)

    def get(self, request):
        serializer = self.ChessGetGameSerializer(data=request.GET)
        if serializer.is_valid():
            params = serializer.validated_data
            try:
                game_obj = ChessGame.objects.get(id=params["game_id"])
            except ChessGame.DoesNotExist:
                return Response({"error": "Game does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            pgn = io.StringIO(game_obj.pgn) ##string -->pgn
            game = chess.pgn.read_game(pgn) 
            current_outcome_str = get_outcome_str(game.end().board())
            response_data = {
                "fen": game.end().board().fen(),
                "board_ascii": [line for line in (str(game.end().board())).splitlines()],
                "current-status": current_outcome_str
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


##Game At Specific Move
class ChessGetGameAtSpecificMove(APIView):
    class ChessGetGameSerializer(serializers.Serializer):
        game_id = serializers.IntegerField(required=True)
        move_number = serializers.IntegerField(required=True)

    def get(self, request):
        serializer = self.ChessGetGameSerializer(data=request.GET)
        if serializer.is_valid():
            params = serializer.validated_data
            try:
                game_obj = ChessGame.objects.get(id=params["game_id"])
            except ChessGame.DoesNotExist:
                return Response({"error": "Game does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            move_number = params["move_number"]
            pgn = io.StringIO(game_obj.pgn)
            game = chess.pgn.read_game(pgn)

            for i in range(move_number):
                game = game.next()
                if game is None:
                    return Response({"error": f"Invalid move number, try number <= {i}"}, status=status.HTTP_400_BAD_REQUEST)

            current_outcome_str = get_outcome_str(game.board())
            response_data = {
                "fen": game.board().fen(),
                "board_ascii": [line for line in (str(game.board())).splitlines()],
                "current-status": current_outcome_str
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)