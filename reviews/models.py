from django.db import models
from django.contrib.auth.models import User
from menu.models import MenuItem

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()  # 1-5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user} - {self.rating}/5"
