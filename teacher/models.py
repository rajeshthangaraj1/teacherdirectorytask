from django.db import models

# Create your models here.
from phonenumber_field.modelfields import PhoneNumberField


class Teacher(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    profile_pic = models.ImageField()
    phone = PhoneNumberField()
    room_no = models.CharField(max_length=100)
    subjects = models.JSONField()

    def save(self, *args, **kwargs):
        assert len(
            self.subjects) <= 5, f"A Teacher can only teach upto 5 subjects, {self.user.get_full_name()} has {len(self.subjects)} subjects"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name()
