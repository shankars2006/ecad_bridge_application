from django.db import models
from django.utils.text import slugify
import uuid



class UserProfile(models.Model):
    username = models.CharField(max_length=150)
    designation = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class Post(models.Model):
    author = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    image_url = models.ImageField(blank=True, null=True, upload_to='post/images/')
    created_at = models.DateTimeField(auto_now_add=True)
    display_homepage = models.BooleanField(default=False)
    top_post = models.BooleanField(default=False)

    slug = models.SlugField(unique=True, max_length=220)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)
    @property
    def formatted_image_url(self):
        url = self.image_url if self.image_url and self.image_url.__str__().startswith(('http', 'https')) else str(self.image_url.url) if self.image_url else None
        return url
    

    def __str__(self):
        return self.title
    
    
    
class ContactMessage(models.Model):
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
    
    
class Aboutus(models.Model):
    author = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='aboutus',
        null=True,
        blank=True
    )
    content = models.TextField()
    mission = models.TextField()
    vision = models.TextField()
    Authintro = models.TextField()

    def __str__(self):
        return "About Us Content"


class Article(models.Model):
    ARTICLE = 'article'
    POST = 'post'
    POST_TYPE_CHOICES = [
        (ARTICLE, 'Article'),
        (POST, 'Post'),
    ]
    
    author = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='article'
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=191, unique=True, db_index=True)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    post_type = models.CharField(
        max_length=10,
        choices=POST_TYPE_CHOICES,
        default=ARTICLE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    cover_image = models.ImageField(upload_to='article/covers/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    @property
    def formatted_image_url(self):
        url = self.cover_image if self.cover_image and self.cover_image.__str__().startswith(('http', 'https')) else str(self.cover_image.url) if self.cover_image else None
        return url


class ContentViewLog(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='view_logs'
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['article', 'viewed_at']),
        ]