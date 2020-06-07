import json
from typing import List

from django.contrib.auth import views as auth_views, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from .forms import RegisterForm, LoginForm, PostForm
from .models import Hashtags


class HomeView(TemplateView):
    template_name = 'home-page.html'


class LoginView(auth_views.LoginView):
    template_name = 'login.html'
    form_class = LoginForm


class LogoutView(LoginRequiredMixin, auth_views.LogoutView):
    """We don't need any additional functionality in it."""
    pass


class PostFormView(LoginRequiredMixin, FormView):
    template_name = 'post-create.html'
    form_class = PostForm
    success_url = reverse_lazy('home')

    @classmethod
    def parse_hashtags(cls, hashtags: str) -> List[str]:
        array = json.loads(hashtags)
        return [item["value"] for item in array if item["value"]]

    @classmethod
    def retrieve_all_hashtags(cls):
        tags = Hashtags.objects.all().values()
        return [tag['text'] for tag in tags]

    def post(self, request, *args, **kwars):
        """Process POST request to the view and get back a response."""
        # ToDo: Add tests for the function
        # ToDo: Refactor (extract method)
        form = self.get_form()
        if form.is_valid():
            # Convert received hashtags from json format to the list[str]
            hashtags = PostFormView.parse_hashtags(
                form.cleaned_data['hashtags']
            )
            stored_tag_values = PostFormView.retrieve_all_hashtags()

            # Filter tags, that aren't in the db and save them to db
            new_hashtags = [
                Hashtags(text=tag)
                for tag in hashtags
                if tag not in stored_tag_values
            ]
            for tag in new_hashtags:
                tag.save()

            # Alternative for single-object save
            # Don't work in sqlite, but works for postgresql
            # new_hashtags = Hashtags.objects.bulk_create(new_hashtags)

            # Save post and add author to it.
            # Posts needs to be saved before linking hashtags objects in the db
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            # Select all tags, that are linked with current post
            post_tags = [
                Hashtags(text=tag) for tag in hashtags
                if tag in stored_tag_values
            ]
            post_tags.extend(new_hashtags)

            # Link created hashtags with the post object in the db
            for tag in post_tags:
                post.hashtags.add(tag)

            # Return successful HttpResponse
            return super().form_valid(form)
        return super().form_invalid(form)


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


# class PostAdminView(FormView):
#     template_name = 'post-form.html'
