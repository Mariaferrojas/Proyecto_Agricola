from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta


class PasswordResetToken(models.Model):
   
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def is_valid(self):
        
        return not self.used and now() < self.expires_at

    def __str__(self):
        return f"Token reset para {self.user.email} - Válido: {self.is_valid()}"

    @staticmethod
    def create_for_user(user):
        
        from django.utils.crypto import get_random_string
        
        token = get_random_string(length=64)
        expires_at = now() + timedelta(hours=24)
        
     
        PasswordResetToken.objects.filter(user=user, used=False).update(used=True)
        
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        return reset_token
