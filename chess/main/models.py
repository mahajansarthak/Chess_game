from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class ChessGame(models.Model):

    pgn = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=100, default="Ongoing")
    black_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name="black_player", default=1)
    white_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name="white_player", default=2)

    def __str__(self):
        return f"game created at {self.created_at}"
