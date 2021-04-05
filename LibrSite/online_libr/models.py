from django.db import models
from django.conf import settings
from datetime import date

SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unknown'),
        ('O', 'Other'),
    ]


def get_range_choices(xmax, xmin=1):
    range_choices = list()
    for x in range(xmin, xmax+1):
        range_choices.append((x, x))
    return range_choices


class LibUser(models.Model):
    """
        Extension of :model:`auth.User`
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='libuser', default=0, editable=False)
    sex = models.CharField(max_length=2, choices=SEX_CHOICES, default='U')
    birth_date = models.DateField(blank=True, null=True,)

    def __str__(self):
        return self.user.last_name + ' ' + self.user.first_name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200, default="Unknown")
    pub_date = models.DateField(default="1998-08-06", null=True, blank=True)
    description = models.CharField(max_length=500, default="", blank=True)
    # rating = models.DecimalField(default=0, editable=False, decimal_places=2, max_digits=5)
    rating = models.FloatField(default=0, editable=False)
    read_counter = models.IntegerField(default=0, editable=False)
    added = models.DateField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['title', 'author'], name='unique_book')]

    def __str__(self):
        return self.title


class ReadStatus(models.Model):
    STATUS_CHOICES = [
        ('P', 'Planned'),
        ('C', 'Completed'),
        ('D', 'Dropped'),
        # ('U', 'Unread'),
        ('R', 'Reading')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='statuses',
                             on_delete=models.CASCADE, default=0, editable=False)
    book = models.ForeignKey(Book, related_name='statuses', on_delete=models.CASCADE, default=0, editable=False)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='U')
    date = models.DateField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'book'], name='unique_status')]
        ordering = ['status']

    def __str__(self):
        return self.book.title + ' ' + str(self.user.id) + ' ' + self.status


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reviews',
                             on_delete=models.CASCADE, default=0, editable=False)
    book = models.ForeignKey(Book, related_name='reviews', on_delete=models.CASCADE, default=0, editable=False)
    comment = models.CharField(max_length=400, blank=True)
    rating = models.IntegerField(default=10, choices=get_range_choices(10))
    date = models.DateField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'book'], name='unique_review')]

    def __str__(self):
        return self.book.title + ' - ' + str(self.user) + ' ' + str(self.rating)

