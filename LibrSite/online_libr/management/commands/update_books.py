from django.core.management.base import BaseCommand
from decimal import *

from online_libr.models import Book, Review, ReadStatus
from datetime import datetime


class Command(BaseCommand):
    help = 'Update ratings and read counters on books'

    def handle(self, *args, **options):
        getcontext().prec = 2
        all_books = Book.objects.all()
        no_rev = 0
        for book in all_books:
            rating = 0
            book_reviews = book.reviews.all()
            if book_reviews.count() != 0:
                for review in book_reviews:
                    rating += review.rating
                book.rating = (Decimal(rating) / Decimal(book_reviews.count()))
            else:
                no_rev += 1
                # book.rating = -1
            book.read_counter = book.statuses.count()
            book.save()

        self.stdout.write(self.style.SUCCESS(
            'Updated {} books. {} have no reviews, score undefined'.format(all_books.count(), no_rev)))
