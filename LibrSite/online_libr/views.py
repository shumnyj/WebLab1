from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth import login, logout, views as auth_views, models as auth_models
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from . import models as olm
# import online_libr.models as olm


def index_view(request):
    context = {}
    try:
        context['latest_books'] = olm.Book.objects.order_by('-added')[:5]
    except olm.Book.DoesNotExist:
        print("no books")
    return render(request, "online_libr/index.html", context)


def book_view(request, book_id):
    # book = get_object_or_404(olm.Book, pk=book_id)

    return HttpResponse("Certain book page = {}".format(book_id))


def profile_view(request, user_id):
    return HttpResponse("Certain user profile")


def profile_edit_view(request):
    return HttpResponse("Edit user profile")


def register_view(request, user_id):
    return HttpResponse("Register")


def login_view(request, user_id):
    return HttpResponse("Login")

