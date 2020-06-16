import json
from typing import List

from django.contrib.auth import views as auth_views, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Form
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from .forms import RegisterForm, LoginForm, PostForm, TagForm
from .models import Hashtags, Post


class HomeView(TemplateView):
    template_name = 'home-page.html'


class LoginView(auth_views.LoginView):
    template_name = 'login.html'
    form_class = LoginForm


class LogoutView(LoginRequiredMixin, auth_views.LogoutView):
    """We don't need any additional functionality in it."""
    pass


class TagsRetrieveView(LoginRequiredMixin, View):
    def get(self, request: dict, *args, **kwargs) -> JsonResponse:
        """Retrieve all tags from the db and put them in JsonResponse."""
        values = Hashtags.objects.all().values()
        values = {'values': [tag['text'] for tag in values]}
        return JsonResponse(values)


class PostFormView(LoginRequiredMixin, FormView):
    template_name = 'post-create.html'
    form_class = PostForm
    success_url = reverse_lazy('home')
    # Holds tags which already exists in db
    stored_tags = []
    # Holds tags which are present in the post
    post_tags = []

    @classmethod
    def parse_hashtags(cls, hashtags: str) -> List[str]:
        array = json.loads(hashtags)
        return [item["value"] for item in array if item["value"]]

    @classmethod
    def retrieve_stored_tags(cls):
        tags = Hashtags.objects.all().values()
        return [tag['text'] for tag in tags]

    def filter_new_tags(self, post_tags: List[str]) -> List[TagForm]:
        """Filter all the tags, which are not present in the db."""
        return [
            TagForm({'text': tag})
            for tag in post_tags
            if tag not in self.stored_tags
        ]

    def new_tags_are_valid(self, new_tags: List[TagForm]) -> bool:
        """Validate new tags."""
        return all(tag.is_valid() for tag in new_tags)

    def save_new_tags(self, new_tags: List[TagForm]) -> List[Hashtags]:
        """Save new tags to the db and return Hashtags objects."""
        return [tag.save() for tag in new_tags]

        # Alternative for single-object save
        # Don't work in sqlite, but works for postgresql
        # new_hashtags = Hashtags.objects.bulk_create(new_hashtags)

    def get_user(self):
        """Return user object from request."""
        return self.request.user

    def save_post(self, form: Form) -> Post:
        """Save post and add author to it.
        
        Post needs to be saved before linking hashtag objects.
        """
        post = form.save(commit=False)
        post.author = self.get_user()
        post.save()
        return post

    def form_valid(self, form):
        """Process and save form data and return back an RedirectResponse."""
        # ToDo: Add unit tests
        # ToDo: Refactor (extract method)
        # Convert received hashtags from json format to the list[str]
        hashtags = PostFormView.parse_hashtags(
            form.cleaned_data['hashtags']
        )
        self.stored_tags = PostFormView.retrieve_stored_tags()

        # Filter new tags, validate them and save them to db
        new_tags = self.filter_new_tags(hashtags)

        if not self.new_tags_are_valid(new_tags):
            form.add_error('hashtags', 'Hashtag(s) doesn\'t comply')
            return self.form_invalid(form)

        new_tags = self.save_new_tags(new_tags)

        # Save post and add author to it.
        # Posts needs to be saved before linking hashtags objects in the db
        post = self.save_post(form)

        # Select all tags, which are linked with current post
        post_tags = [
            Hashtags(text=tag) for tag in hashtags
            if tag in self.stored_tags
        ]
        post_tags.extend(new_tags)

        # Link created hashtags with the post object in the db
        for tag in post_tags:
            post.hashtags.add(tag)

        # Return successful HttpResponse
        return super().form_valid(form)


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        new_user = form.save()
        login(self.request, new_user)
        return super().form_valid(form)


class SecretView(LoginRequiredMixin, TemplateView):
    template_name = 'secret-page.html'
