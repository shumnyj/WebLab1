from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.db.utils import IntegrityError

from django.contrib.auth import login, logout, views as auth_views, models as auth_models
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, FormView, View, UpdateView, ListView
from django.forms.models import model_to_dict

from django.conf import settings

from . import models as olm
from . import forms as olf

from rest_framework import routers, viewsets, permissions, response, status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from .serializers import (IsAdminOrReadOnly, IsCreatorOrReadOnly, ReviewSerializerPost, StatusSerializerPost,
                          ReviewSerializer, StatusSerializer, UserSerializer, BookSerializer)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

import datetime
from random import choice


def index_view(request):
    context = {}
    try:
        context['latest_books'] = olm.Book.objects.order_by('-added')[:5]
    except olm.Book.DoesNotExist:
        print("no books")
    if request.user.is_authenticated:
        context["chosen_book_title"] = olf.chosen_book.title
    return render(request, "online_libr/index.html", context)


def about_view(request):
    # % url 'online_libr:api-root' %}
    return render(request, "online_libr/about.html")


def browse_view(request):
    context = {}
    try:
        context['books'] = olm.Book.objects.order_by('title')
    except olm.Book.DoesNotExist:
        print("no books")
    return render(request, "online_libr/browse.html", context)


"""def book_view(request, book_id):
    book = get_object_or_404(olm.Book, pk=book_id)
    last_reviews = book.reviews.all().order_by('date')[:4]
    context = {'book': book, 'last_reviews': last_reviews}
    return render(request, "online_libr/book.html", context)
    # return HttpResponse("Certain book page = {}".format(book_id))"""


class BookView(View):
    template_name = "online_libr/book.html"

    form_review = olf.ReviewForm
    form_status = olf.ReadStatusForm

    book = None
    u_review = None
    u_status = None

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self._common_context(request))

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        context = self._common_context(request)
        # could split into 2 views
        if 'chagestatus' in request.POST:           # checking which form is it (not secure?)
            # modify or add if don't exist
            form = self.form_status(request.POST, instance=self.u_status)
        elif 'addreview' in request.POST:
            form = self.form_review(request.POST, instance=self.u_review)
        else:
            form = None
        if form and form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.book = self.book
            try:
                obj.save()
                if not self.u_status:
                    obj.book.read_counter += 1
                    obj.book.save()
                # context['message'] = "Changes successful"
                return HttpResponseRedirect(reverse("online_libr:book", args=[self.book.id]))
            except IntegrityError:
                context['message'] = "Invalid form: integrity error"
        else:
            context['message'] = "Invalid form"
        # context.update(self._common_context(request))
        return render(request, self.template_name, context)

    def _common_context(self, request):
        context = dict()
        self.book = get_object_or_404(olm.Book, pk=self.kwargs['book_id'])
        if request.user.is_authenticated:
            try:
                self.u_review = request.user.reviews.all().get(book=self.book)
                context['user_review'] = self.u_review
            except olm.Review.DoesNotExist:
                pass
            context['form_review'] = self.form_review(instance=self.u_review)
            try:
                self.u_status = request.user.statuses.all().get(book=self.book)
                context['user_status'] = self.u_status
            except olm.ReadStatus.DoesNotExist:
                pass
            context['form_status'] = self.form_status(instance=self.u_status)
        context['book'] = self.book
        context['last_reviews'] = self.book.reviews.all().order_by('-date')[:8]
        return context


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


class ProfileView(DetailView):
    model = auth_models.User
    context_object_name = 'base_user'
    template_name = "online_libr/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lib_user'] = super().get_object().libuser
        # print(str(super().get_object().reviews.all()))
        """try:
            statuses = olm.ReadStatus.all().filter(user=super().get_object())
            context['user_statuses'] = statuses
        except olm.ReadStatus.DoesNotExist:
            pass"""
        return context


class UserReviewsView(ListView):
    template_name = "online_libr/user_reviews.html"
    # queryset = olm.Review.objects.all()
    context_object_name = 'reviews_list'
    allow_empty = True
    ordering = 'date'
    paginate_by = 10

    def get_queryset(self):
        return olm.Review.objects.filter(user_id=self.kwargs['pk'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {'related_user': get_object_or_404(auth_models.User, id=self.kwargs['pk'])}
        return super().get_context_data(**context)


class ProfileUpdate(FormView, LoginRequiredMixin):
    template_name = "online_libr/edit_profile.html"
    form_class = olf.UpdateProfileForm
    success_url = reverse_lazy("online_libr:index")
    login_url = reverse_lazy("online_libr:login")

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        try:
            u = auth_models.User.objects.get(pk=self.request.user.pk)
            return form_class(instance=u, **self.get_form_kwargs())
        except auth_models.User.DoesNotExist:
            return form_class(**self.get_form_kwargs())

    def get_initial(self):
        # self.initial = model_to_dict(self.request.user, exclude=['password'])
        self.initial.update(model_to_dict(self.request.user.libuser))
        return self.initial.copy()

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        try:
            self.success_url = reverse_lazy("online_libr:profile", kwargs={'pk': self.request.user.id})
        except IntegrityError:
            print("get success_url failed")
        return str(self.success_url)

    def form_valid(self, form):
        # form.instance = self.request.user # not needed
        form.save()
        self.request.user.libuser.sex = form.cleaned_data['sex']
        self.request.user.libuser.birth_date = form.cleaned_data['birth_date']
        self.request.user.libuser.save()
        return super(ProfileUpdate, self).form_valid(form)


def search_view(request):
    context = dict()
    if request.method == 'POST':  # Form sent
        form = olf.SearchForm(request.POST)
        context['form'] = form
        if form.is_valid():
            qry = form.cleaned_data['query']
            try:
                found_books = olm.Book.objects.filter(title__iregex=qry.replace(' ', '.*'))
            except olm.Book.DoesNotExist:
                found_books = None
            context['found_books'] = found_books
    else:
        context['form'] = olf.SearchForm()
    return render(request, "online_libr/search.html", context)

# api views


class UserViewSet(viewsets.ModelViewSet):
    queryset = auth_models.User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get']


class BookViewSet(viewsets.ModelViewSet):
    queryset = olm.Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(methods=['get'], detail=True, permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def reviews(self, request, pk=None):
        try:
            book = olm.Book.objects.get(id=pk)
        except olm.Book.DoesNotExist:
            return response.Response({"error": "Book not found."}, status=status.HTTP_400_BAD_REQUEST)
        res = book.reviews.all()
        return response.Response(ReviewSerializer(res, context={'request': request}, many=True).data)

    @action(methods=['get'], detail=True, permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def statuses(self, request, pk=None):
        try:
            book = olm.Book.objects.get(id=pk)
        except olm.Book.DoesNotExist:
            return response.Response({"error": "Book not found."}, status=status.HTTP_400_BAD_REQUEST)
        res = book.statuses.all()
        return response.Response(StatusSerializer(res, context={'request': request}, many=True).data)

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers['default'])

    serializers = {
        'default': BookSerializer,
        'reviews': ReviewSerializerPost,
        'statuses': StatusSerializerPost,
    }


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = olm.Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsCreatorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers['default'])

    serializers = {
        'default': ReviewSerializer,
        'create': ReviewSerializerPost,
    }

    def perform_create(self, serializer):
            serializer.save(user=self.request.user)

    def create(self, validated_data):
        #validated_data['user'] = self.request.user
        try:
            return super(ReviewViewSet, self).create(validated_data)
        except IntegrityError:
            raise ParseError(detail="Unique together constraint on ['user', 'book'] is probably violated")


class StatusViewSet(viewsets.ModelViewSet):
    queryset = olm.ReadStatus.objects.all()
    serializer_class = StatusSerializer
    permission_classes = [IsCreatorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers['default'])

    serializers = {
        'default': StatusSerializer,
        'create': StatusSerializerPost,
    }

    def perform_create(self, serializer):
            serializer.save(user=self.request.user)

    def create(self, validated_data):
        # validated_data['user'] = self.request.user
        try:
            return super(StatusViewSet, self).create(validated_data)
        except IntegrityError:
            raise ParseError(detail="Unique together constraint on ['user', 'book'] is probably violated")


ApiRouter = routers.DefaultRouter()
ApiRouter.register(r'books', BookViewSet)
ApiRouter.register(r'users', UserViewSet)
ApiRouter.register(r'reviews', ReviewViewSet)
ApiRouter.register(r'statuses', StatusViewSet)


@login_required
def chat_view(request):
    context = dict()
    if olf.chosen_book is None:
        olf.chosen_book = choice(olm.Book.objects.all())  # using SQL DB record is probably overkill
        # should be chosen/saved daily, currently gets chosen on reboot for simplicity
    # print(str(olf.chosen_book))
    context['chosen_book'] = olf.chosen_book
    context['room_name'] = "test_name"
    context['act_user'] = request.user
    context['connected_users'] = olm.ChatUser.objects.all()  # not just admin ?
    return render(request, 'online_libr/chat_page.html', context)


@login_required
def chat_users(request):
    if request.user.is_staff:
        connected_users = olm.ChatUser.objects.all()
        return render(request, 'online_libr/chat_online_users.html', {'connected_users': connected_users,
                                                                      'chosen_book': olf.chosen_book})
    return HttpResponseRedirect(reverse("online_libr:index"))


@login_required
def kick_chat_user(request, pk):
    if request.user.is_staff:
        try:
            chat_user = olm.ChatUser.objects.get(pk=pk).user.username
            channel_layer = get_channel_layer()
            if not channel_layer.groups:
                return HttpResponse('No chat')
            # (no security, should encrypt this and deencrypt in consumer)
            async_to_sync(channel_layer.group_send)(
                list(channel_layer.groups.keys())[0],
                {
                    'type': 'chat_message',
                    'message': '- User %s kicked ! ' % chat_user,
                    'kick_username': chat_user
                }
            )
        except olm.ChatUser.DoesNotExist:
            print("Tried to kick non-existent chat user")
        return HttpResponseRedirect(reverse("online_libr:chat_users"))

