from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from autoslug import AutoSlugField
from django_countries.fields import CountryField
from employers.models import Job
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.db.models import Q



CHOICES = (
    ('Full Time', 'Full Time'),
    ('Part Time', 'Part Time'),
    ('Internship', 'Internship'),
    ('Remote', 'Remote'),
)

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    full_name = models.CharField(max_length=200, null=True, blank=True)
    country = CountryField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    resume = models.FileField(upload_to='resumes', null=True, blank=True)
    grad_year = models.IntegerField(blank=True)
    looking_for = models.CharField(
        max_length=30, choices=CHOICES, default='Full Time', null=True)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    slug = AutoSlugField(populate_from='user', unique=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(grad_year__lte=2027),
                name='valid_grad_year'
            )
        ]

    def get_absolute_url(self):
        return "/profile/{}".format(self.slug)

    def save(self, *args, **kwargs):
        if self.grad_year and self.grad_year > 2027:
            raise ValueError("Graduation year should not be greater than 2027.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username


class Skill(models.Model):
    skill = models.CharField(max_length=200)
    user = models.ForeignKey(
        User, related_name='skills', on_delete=models.CASCADE)


class SavedJobs(models.Model):
    job = models.ForeignKey(
        Job, related_name='saved_job', on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name='saved', on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.job.title


class AppliedJobs(models.Model):
    job = models.ForeignKey(
        Job, related_name='applied_job', on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name='applied_user', on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.job.title


class SavedSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query