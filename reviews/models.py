""" imports """
from django.conf import settings
from django.db import models
from django.db.models import Count
from django.urls import reverse
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    """
    This creates a custom manager. It allows us to retrieve reviews using
    code like Review.published.all()
    Note: All models come with a default manager - the objects manager
    for example Review.objects.all()
    """

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(status=review.Status.PUBLISHED)

    def most_discussioned(self):
        return self.get_queryset().annotate(discussion_count=Count(
            'discussions')).order_by('-discussion_count')[:3]


class Review(models.Model):
    """ data model for a review """
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=210,
        unique_for_date='created_on'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_reviews'
    )
    body = models.TextField()
    tags = TaggableManager()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT
    )
    # the default manager   ie Review.objects.all()
    objects = models.Manager()
    # our custom manager   ie Review.published.all()
    published = PublishedManager()

    class Meta:
        """
        This class defines the meta data for the model
        ordering is tell django that it should sort results by the updated_on
        field (latest first indicated by '-')
        indexes allows us to define the database indexing for this model
        """
        ordering = ['-updated_on']
        indexes = [
            models.Index(fields=['-updated_on']),
        ]

    def __str__(self):
        return f'{self.title} by {self.author.username}'

    def get_absolute_url(self):
        return reverse(
            "reviews:review_detail",
            args=[
                self.created_on.year,
                self.created_on.month,
                self.created_on.day,
                self.slug
            ]
        )



class Discussion(models.Model):

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="discussions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    body = models.TextField(max_length=800)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_on']
        indexes = [
            models.Index(fields=['created_on']),
        ]

    def __str__(self):
        return f'discussion by {self.user} on {self.review}'