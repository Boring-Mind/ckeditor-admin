from crispy_forms import layout
from crispy_forms.helper import FormHelper
from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse
from django.core.validators import RegexValidator
import re

from .models import Post, Hashtags


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs): # pragma: no cover
        """Initialize crispy forms."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-LoginForm'
        self.helper.form_class = 'form-group'
        self.form_method = 'post'
        self.helper.form_action = reverse(settings.LOGIN_URL)

        self.helper.add_input(layout.Submit('login', 'Login'))
        self.helper.add_input(layout.Hidden('next', ''))


class RegisterForm(UserCreationForm):
    username = forms.CharField(label='Username', max_length=45)
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(
        min_length=settings.MIN_PASSWORD_LENGTH,
        label='Password',
        strip=False,
        help_text=f'Enter {settings.MIN_PASSWORD_LENGTH} digits and chars',
        widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        min_length=settings.MIN_PASSWORD_LENGTH,
        label='Repeat the password',
        strip=False,
        widget=forms.PasswordInput()
    )

    def crispy_init(self): # pragma: no cover
        """Initialize crispy-forms helper."""
        self.helper = FormHelper()
        self.helper.form_id = 'id-RegistrationForm'
        self.helper.form_class = 'form-group'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('register')

        self.helper.layout = layout.Layout(
            layout.Field('username'),
            layout.Field('email'),
            layout.Field('password1'),
            layout.Field('password2'),
            layout.ButtonHolder(
                layout.Submit('submit', 'Register')
            )
        )

    def __init__(self, *args, **kwargs): # pragma: no cover
        super().__init__(*args, **kwargs)
        self.crispy_init()


class PostForm(forms.ModelForm):
    title = forms.CharField(label='Title', max_length=80)
    description = forms.CharField(
        widget=forms.Textarea()
    )
    hashtags = forms.CharField(
        label='Add tags to your post',
        max_length=200,
        help_text='Maximum 5 tags up to 30 characters long',
        widget=forms.TextInput(attrs={'id': 'hashtags_input'})
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'editor',
            'max_length': settings.MAX_POST_LENGTH
        })
    )
    preview_img_url = forms.URLField(max_length=300)

    class Meta:
        model = Post
        exclude = ('author', 'hashtags', 'post_date', 'modified_date')

    def crispy_init(self): # pragma: no cover
        """Initialize crispy-forms helper."""
        self.helper = FormHelper()
        self.helper.form_id = 'id-PostCreateForm'
        self.helper.form_class = 'form-group'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('create_post')

        # self.helper.layout = layout.Layout(
        #     layout.Field('title'),
        #     layout.Field('description'),
        #     layout.Field('hashtags'),
        #     layout.Field('content'),
        #     layout.Field('preview_img_url'),
        #     layout.Field('post_status'),
        #     layout.ButtonHolder(
        #         layout.Submit('submit', 'Create post')
        #     )
        # )
        self.helper.layout = layout.Layout(
            layout.Div(
                'title',
                'content',
                layout.ButtonHolder(
                    layout.Button(
                        'next', 'Next page', css_class='btn-outline-dark'
                    )
                ),
                css_class='py-3',
                css_id='form1'
            ),
            layout.Div(
                'description',
                'hashtags',
                'preview_img_url',
                'post_status',
                layout.Row(
                    layout.Div(
                        layout.Button(
                            'back',
                            'Previous page',
                            css_class='btn-outline-dark'
                        ),
                        css_class='col-md-6'
                    ),
                    layout.Div(
                        layout.Submit('submit', 'Create post'),
                        css_class='col-md-6'
                    )
                ),
                css_class='py-3 d-none',
                css_id='form2'
            ),
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crispy_init()


class TagForm(forms.ModelForm):
    text = forms.CharField(
        max_length=30,
        validators=[
            RegexValidator(
                regex=re.compile(r'^[a-zA-Z0-9 \/-]+$'),
                message='Hashtag doesn\'t comply'
            )
        ])

    class Meta:
        model = Hashtags
        fields = '__all__'
