import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone
from accounts.models import User


class ActivityFeed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    description = models.CharField(max_length=255)  # e.g. "Completed Lesson: Intro to Python"
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} — {self.description}'


class Streak(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')

    login_current_streak = models.PositiveIntegerField(default=0)
    login_longest_streak = models.PositiveIntegerField(default=0)
    last_login_date = models.DateField(null=True, blank=True)

    course_current_streak = models.PositiveIntegerField(default=0)
    course_longest_streak = models.PositiveIntegerField(default=0)
    last_course_activity_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Streak — {self.user.email}'

    def _bump(self, current_field, longest_field, last_date_field):
        today = timezone.localdate()
        last_date = getattr(self, last_date_field)

        if last_date == today:
            return  # already counted today, no-op

        current = getattr(self, current_field)
        longest = getattr(self, longest_field)

        if last_date == today - timedelta(days=1):
            current += 1
        else:
            current = 1  # missed a day or first-ever activity, reset

        longest = max(longest, current)

        setattr(self, current_field, current)
        setattr(self, longest_field, longest)
        setattr(self, last_date_field, today)
        self.save(update_fields=[current_field, longest_field, last_date_field, 'updated_at'])

    def bump_login_streak(self):
        self._bump('login_current_streak', 'login_longest_streak', 'last_login_date')

    def bump_course_streak(self):
        self._bump('course_current_streak', 'course_longest_streak', 'last_course_activity_date')

    @classmethod
    def record_login(cls, user):
        streak, _ = cls.objects.get_or_create(user=user)
        streak.bump_login_streak()
        return streak

    @classmethod
    def record_course_activity(cls, user):
        streak, _ = cls.objects.get_or_create(user=user)
        streak.bump_course_streak()
        return streak


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} — {self.title}'