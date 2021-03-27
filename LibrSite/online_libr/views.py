from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth import login, logout, views as auth_views, models as auth_models
from django.views.generic import DetailView, FormView
from django.db.utils import IntegrityError
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import models as olm
from . import forms as olf
# import online_libr.models as olm


def index_view(request):
    context = {}
    try:
        context['latest_books'] = olm.Book.objects.order_by('-added')[:5]
    except olm.Book.DoesNotExist:
        print("no books")
    return render(request, "online_libr/index.html", context)


def about_view(request):
    return render(request, "online_libr/about.html")


def browse_view(request):
    context = {}
    try:
        context['books'] = olm.Book.objects.order_by('title')
    except olm.Book.DoesNotExist:
        print("no books")
    return render(request, "online_libr/browse.html", context)


def book_view(request, book_id):
    book = get_object_or_404(olm.Book, pk=book_id)
    last_reviews = book.reviews.all().order_by('date')[:4]
    context = {'book': book, 'last_reviews': last_reviews}
    return render(request, "online_libr/book.html", context)
    # return HttpResponse("Certain book page = {}".format(book_id))


def profile_view(request, user_id):
    return HttpResponse("Certain user profile")


def profile_edit_view(request):
    return HttpResponse("Edit user profile")


def register_view(request):
    form = olf.MyRegisterForm()
    return render(request, "online_libr/register.html", {'form': form})


class RegisterView(FormView):
    template_name = "online_libr/register.html"
    form_class = olf.MyRegisterForm
    success_url = reverse_lazy("online_libr:login")

    def form_valid(self, form):
        new_user = auth_models.User()
        new_libuser = olm.LibUser()

        auth_models.UserManager.create_user(form.cleaned_data['username'], form.cleaned_data['email'],
                                            form.cleaned_data['password1'],
                                            {'first_name': form.cleaned_data['first_name'],
                                                'last_name': form.cleaned_data['last_name']} )
        new_libuser.user = new_user
        new_libuser.sex = form.cleaned_data['sex']
        new_libuser.birth_date = form.cleaned_data['birth_date']
        try:
            new_libuser.save()
        except IntegrityError:
            return super().form_invalid(form)
        login(user=new_user)
        return super().form_valid(form)


class MyLoginView(auth_views.LoginView):
    template_name = "online_libr/login.html"
    redirect_field_name = "next"
    form_class = olf.MyAuthForm


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("online_libr:index"))


"""class MyRegisterView(auth_views.Re):
    template_name = "online_libr/register.html"
    redirect_field_name = "next"
    form_class = olf.MyAuthForm"""


class ProfileView(DetailView):
    model = auth_models.User
    context_object_name = 'base_user'
    template_name = "online_libr/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lib_user'] = super().get_object().libuser
        return context

