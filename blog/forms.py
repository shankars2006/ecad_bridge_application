from django import forms

from blog.models import Post, ContactMessage, Aboutus, Article

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label='name', required=True)
    email = forms.EmailField(label='email', required=True)
    message = forms.CharField(widget=forms.Textarea, label='message', required=True)
    
    
# class PostForm(forms.ModelForm):
#     title = forms.CharField(max_length=200, required=True)
#     content = forms.CharField(required=True)
#     image_url = forms.ImageField(required=False)
#     display_homepage = forms.BooleanField(required=False, initial=False)
#     top_post = forms.BooleanField(required=False, initial=False)

#     class Meta:
#         model = Post
#         fields = ['title', 'content', 'display_homepage', 'top_post', 'image_url']

#     def clean(self):
#         cleaned_data = super().clean()
#         title = cleaned_data.get('title')
#         content = cleaned_data.get('content')

#         if title and len(title) < 5:
#             raise forms.ValidationError("Title must be at least 5 characters long.")

#         if content and len(content) < 20:
#             raise forms.ValidationError("Content must be at least 20 characters long.")

#         return cleaned_data  

#     def save(self, commit=True):
#         post = super().save(commit=False)

#         # Default image
#         image_url = self.cleaned_data.get('image_url')
#         if not image_url:
#             image_url = (
#                 "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/"
#                 "No_image_available.svg/500px-No_image_available.svg.png"
#             )

#         post.image_url = image_url

#         if commit:
#             post.save()
#         return post

   
# class ArticleForm(forms.ModelForm):
#     class Meta:
#         model = Article
#         fields = ['title', 'content', 'cover_image', 'post_type']
#         widgets = {
#             'title': forms.TextInput(attrs={
#                 'placeholder': 'Enter a descriptive title for your article',
#                 'class': 'form-input',
#                 'required': True
#             }),
#             'content': forms.Textarea(attrs={
#                 'id': 'editor'  # IMPORTANT: matches TinyMCE selector
#             }),
#             'post_type': forms.HiddenInput(),  # We'll handle this via toggle
#         }
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Set initial value for post_type if not provided
#         if not self.initial.get('post_type'):
#             self.initial['post_type'] = 'article'

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'cover_image', 'post_type']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'tinymce'}),
            'post_type': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.fields['post_type'].initial = Article.ARTICLE

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()

        if len(title) < 5:
            raise forms.ValidationError(
                "Title must be at least 5 characters long."
            )

        return title

    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()

        if len(content) < 50:
            raise forms.ValidationError(
                "Content must be at least 50 characters long."
            )

        return content
   