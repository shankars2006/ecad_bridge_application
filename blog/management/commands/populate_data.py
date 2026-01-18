from django.core.management.base import BaseCommand
from blog.models import Post


class Command(BaseCommand):
    help = "Populate the database with initial blog posts"

    def handle(self, *args, **kwargs):
        
        #Delete existing posts to avoid duplicates
        Post.objects.all().delete()
        
        
        
        
        

        titles = [
            "Understanding Django Models",
            "A Guide to Django Views",
            "Working with Django Templates",
            "Django Forms: An Introduction",
            "Deploying Django Applications",
        ]

        contents = [
            "Django models are the single, definitive source of information about your data. "
            "They contain the essential fields and behaviors of the data you’re storing.",

            "Django views are Python functions or classes that receive web requests "
            "and return web responses.",

            "Django templates are a powerful way to separate the presentation of your web pages "
            "from the Python code that powers your application.",

            "Django forms provide a way to handle user input, validate data, "
            "and render HTML forms easily.",

            "Deploying Django applications can be done using various methods, "
            "including platforms like Heroku, AWS, or traditional web servers.",
        ]

        image_urls = [
            "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=1200&q=80",
            "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=1200&q=80",
            "https://images.unsplash.com/photo-1487058792275-0ad4aaf24ca7?w=1200&q=80",
            "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1200&q=80",
            "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=1200&q=80",
        ]

        for title, content, image_url in zip(titles, contents, image_urls):
            Post.objects.create(
                title=title,
                content=content,
                image_url=image_url,
                display_homepage=False,
                top_post=False,
            )

        self.stdout.write(
            self.style.SUCCESS("Successfully populated the database with blog posts")
        )
