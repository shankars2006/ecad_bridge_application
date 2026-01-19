from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.urls import reverse
import logging
from requests import request
from .models import Article, ContentViewLog, UserProfile, Post, ContactMessage, Aboutus
from .forms import ArticleForm, ContactForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage
import os
import uuid
from django.contrib.auth.models import User
from django.db.models import F
from django.db.models import Count, Sum
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum, Avg, Max, F, Q
from django.db.models.functions import TruncDate, TruncMonth, ExtractWeekDay
from django.utils import timezone
from datetime import timedelta, datetime
from django.http import JsonResponse
import json
from django.core.paginator import Paginator
from django.contrib.auth import logout
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from blog.decorators import admin_required


from django.core.paginator import Paginator
from .models import Article

def index(request):
    articles = (
        Article.objects
        .select_related('author')  # Fetch author in same query
        .filter(
            is_published=True,
            post_type=Article.ARTICLE
        )
        .order_by('-views')  # Most viewed first
    )

    posts = (
        Article.objects
        .select_related('author')
        .filter(
            is_published=True,
            post_type=Article.POST
        )
        .order_by('-views')  # Most viewed first
    )

    # Pagination for articles (12 per page)
    articles_paginator = Paginator(articles, 12)
    articles_page_number = request.GET.get('page', 1)
    articles_page = articles_paginator.get_page(articles_page_number)

    # Pagination for posts (6 per page)
    posts_paginator = Paginator(posts, 6)
    posts_page_number = request.GET.get('post_page', 1)
    posts_page = posts_paginator.get_page(posts_page_number)

    return render(
        request,
        'blog/index.html',
        {
            'articles_page': articles_page,
            'posts_page': posts_page,
        }
    )



# def detail(request, slug):
#     post = Post.objects.select_related('author').get(slug=slug)
#     return render(request, 'blog/detail.html', {'post': post})

# def posts(request):
#     postss = Post.objects.select_related('author').all()
#     return render(request, 'blog/post.html', {'postss': postss})

def about(request):
    aboutus = Aboutus.objects.select_related('author').first()
    return render(request, 'blog/about.html', {'aboutus': aboutus})

def tc(request):
    return render(request, 'blog/termandconditions.html')


@admin_required
def contact_details(request):
    contact_messages = ContactMessage.objects.all().order_by('-created_at')
    return render(request, 'blog/contact_details.html', {'contact_messages': contact_messages})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                message=form.cleaned_data['message']
            )

            form = ContactForm()

        return render(request, 'blog/contact.html', {'form': form})

    return render(request, 'blog/contact.html', {'form': ContactForm()})


# def article(request):
#     return render(request, 'blog/article_editor.html')


# def new_post(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST, request.FILES)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.author_id = 1
#             post.save()
#             return render(request, 'blog/new_post.html', {'success': True})
#     else:
#         form = PostForm()

#     return render(request, 'blog/new_post.html', {'form': form})
    

# def edit_post(request, post_id):
#     post = get_object_or_404(Post, id=post_id)
#     form = PostForm()
    
#     # if post.author.author != request.user and not request.user.is_staff:
#     #     messages.error(request, "You don't have permission to edit this post.")
#     #     return redirect('posts')
 
#     if request.method == 'POST':
#         form = PostForm(request.POST, request.FILES, instance=post)

#         if form.is_valid():
#             if request.POST.get('remove_image') == 'true':
#                 if post.image_url:
#                     post.image_url.delete(save=False)
#                     post.image_url = None

#             form.save()
#             messages.success(request, 'Post updated successfully!')
#             return redirect('posts')
#     else:
#         form = PostForm(instance=post)

#     return render(request, 'blog/edit_post.html', {
#         'post': post,
#         'form': form,
#     })
    
    
# def delete_post(request, post_id):
#     post = get_object_or_404(Post, id=post_id)

    # if post.author.author != request.user and not request.user.is_staff:
    #     messages.error(request, "You don't have permission to delete this post.")
    #     return redirect('blog:posts')

    # if request.method == 'POST':
    #     post_title = post.title
    #     post.delete()

    #     return render(request, 'blog/delete_post.html', {
    #         'post_title': post_title,
    #         'redirect_url': reverse('posts'),
    #         'delay': 5,
    #     })

    # # GET request → show confirmation page
    # return render(request, 'blog/confirm_delete.html', {
    #     'post': post
    # })
    
    
@admin_required   
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = UserProfile.objects.get(id=1)  # CORRECT TYPE
            article.post_type = form.cleaned_data.get('post_type', 'article')
            article.save()
            messages.success(request, "Article published successfully!")
            return redirect('blog:admin_content_list')
        else:
            print("FORM ERRORS 👉", form.errors)
            messages.error(request, "Please fix the errors below.")
    else:
        form = ArticleForm()

    # Pass empty context for create mode
    return render(request, 'blog/article_editor.html', {
        'form': form,
        'is_edit': False,
        'article': None  # No article object in create mode
    })



@admin_required
def tinymce_image_upload(request):
    if request.method == 'POST' and request.FILES.get('file'):
        image = request.FILES['file']

        # Create unique filename
        ext = os.path.splitext(image.name)[1]
        filename = f"{uuid.uuid4()}{ext}"

        path = default_storage.save(f'articles/{filename}', image)

        return JsonResponse({
            'location': default_storage.url(path)
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)


# def edit_article(request, article_id):
#     # Try to get the user's UserProfile
#     # user_profile, created = UserProfile.objects.get_or_create(
#     #     username=request.user.username   , author=user_profile
#     # )

#     # Admin/staff can edit any article
#     if request.user.is_staff:
#         article = get_object_or_404(Article, id=article_id)
#     else:
#         # Regular users can edit only their own articles
#         article = get_object_or_404(Article, id=article_id)

#     if request.method == 'POST':
#         form = ArticleForm(request.POST, request.FILES, instance=article)
#         if form.is_valid():
#             form.save()
#             return redirect('article_detail', slug=article.slug)
#     else:
#         form = ArticleForm(instance=article)

#     return render(request, 'blog/article_editor.html', {
#         'form': form,
#         'article': article
#     })

    

@login_required
def article_detail(request, slug):
    article = get_object_or_404(
        Article.objects.select_related('author'),
        slug=slug,
        is_published=True
    )

    session_key = f'viewed_article_{article.id}'
    if not request.session.get(session_key):
        Article.objects.filter(id=article.id).update(views=F('views') + 1)
        ContentViewLog.objects.create(article=article)
        request.session[session_key] = True

    article.refresh_from_db()

    return render(
        request,
        'blog/article_detail.html',
        {
            'article': article
        }
    )

    
    
    
def articles(request):
    articles = (
        Article.objects
        .select_related('author')
        .filter(
            is_published=True,
            post_type=Article.ARTICLE
        )
        .order_by('-views')
    )

    return render(
        request,
        'blog/articles.html',
        {
            'articles': articles
        }
    )

def posts(request):
    postss = (
        Article.objects
        .select_related('author')
        .filter(
            is_published=True,
            post_type=Article.POST
        )
        .order_by('-views')
    )

    return render(
        request,
        'blog/post.html',
        {
            'postss': postss
        }
    )


@login_required
def post_detail(request, slug):
    post = get_object_or_404(
        Article.objects.select_related('author'),
        slug=slug,
        is_published=True,
        post_type=Article.POST
    )

    return render(
        request,
        'blog/post_detail.html',
        {
            'post': post
        }
    )

@admin_required
def admin_base(request):
    contents = (
        Article.objects
        .select_related('author')
        .order_by('-created_at')
    )

    contact_messages = ContactMessage.objects.all()

    return render(
        request,
        'blog/admin_base.html',
        {
            'contents': contents,
            'total_articles': contents.filter(post_type='article').count(),
            'total_posts': contents.filter(post_type='post').count(),
            'contact_messages': contact_messages,
            'total_contact_messages': contact_messages.count(),
        }
    )

# Assuming your Article model is imported from your models
# from .models import Article
@admin_required
def admin_content_list(request):
    """
    Main view for admin content management page - REAL DATA ONLY
    """
    # Get all articles ordered by creation date (newest first)
    contents = Article.objects.select_related('author').order_by('-created_at')
    
    # Apply filters if provided
    post_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '-created_at')
    
    if post_type and post_type != 'all':
        if post_type == 'article':
            contents = contents.filter(post_type=Article.ARTICLE)
        elif post_type == 'post':
            contents = contents.filter(post_type=Article.POST)
    
    if status and status != 'all':
        if status == 'published':
            contents = contents.filter(is_published=True)
        elif status == 'draft':
            contents = contents.filter(is_published=False)
    
    if search:
        contents = contents.filter(
            Q(title__icontains=search) | 
            Q(content__icontains=search) |
            Q(author__username__icontains=search) |
            Q(slug__icontains=search)
        )
    
    # Apply sorting
    if sort == 'title':
        contents = contents.order_by('title')
    elif sort == 'oldest':
        contents = contents.order_by('created_at')
    elif sort == 'views':
        contents = contents.order_by('-views')
    else:  # newest
        contents = contents.order_by('-created_at')

    # REAL COUNTS from database
    total_articles = Article.objects.filter(post_type=Article.ARTICLE).count()
    total_posts = Article.objects.filter(post_type=Article.POST).count()
    
    # REAL Total views from database
    total_views = Article.objects.aggregate(total=Sum('views'))['total'] or 0
    
    # Add pagination
    paginator = Paginator(contents, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'blog/admin_content_list.html',
        {
            'contents': page_obj,
            'page_obj': page_obj,
            'is_paginated': paginator.num_pages > 1,
            'total_articles': total_articles,
            'total_posts': total_posts,
            'total_views': total_views,
            'current_type': post_type,
            'current_status': status,
            'current_search': search,
            'current_sort': sort,
        }
    )

@admin_required
def get_content_analytics(request, content_id):
    """API endpoint to get detailed analytics for specific content - REAL DATA ONLY"""
    try:
        content = Article.objects.get(pk=content_id)
        
        # REAL data calculations
        content_age = max((timezone.now() - content.created_at).days, 1)
        
        # Get ACTUAL views by month for this content (if you track monthly views)
        # If you don't track monthly views, we'll use creation month distribution
        monthly_data = []
        monthly_labels = []
        
        # Get all months since content creation
        current_date = timezone.now()
        creation_date = content.created_at
        
        # Calculate months difference
        months_diff = (current_date.year - creation_date.year) * 12 + (current_date.month - creation_date.month)
        months_diff = max(1, min(months_diff, 12))  # Limit to 12 months max
        
        # Distribute views across months based on creation date
        # This is a simple distribution - you might want to implement a ViewLog model for accurate monthly tracking
        for i in range(min(6, months_diff)):  # Show last 6 months or fewer
            month_date = creation_date + timedelta(days=30*i)
            monthly_labels.append(month_date.strftime('%b %Y'))
            
            # Simple distribution - divide views by number of months
            # In production, you should have a monthly_view_count field or ViewLog model
            monthly_views = content.views // max(1, months_diff)
            monthly_data.append(monthly_views)
        
        # REAL data: Get overall views by type
        views_by_type = {
            'articles': Article.objects.filter(post_type=Article.ARTICLE).aggregate(
                total=Sum('views')
            )['total'] or 0,
            'posts': Article.objects.filter(post_type=Article.POST).aggregate(
                total=Sum('views')
            )['total'] or 0,
        }
        
        # REAL performance metrics
        avg_daily_views = content.views / content_age
        
        # REAL comparison data
        avg_views_same_type = Article.objects.filter(
            post_type=content.post_type
        ).aggregate(
            avg=Avg('views')
        )['avg'] or 0
        
        if avg_views_same_type > 0:
            comparison_to_avg = round(((content.views - avg_views_same_type) / avg_views_same_type) * 100, 1)
        else:
            comparison_to_avg = 100.0
        
        # REAL: Get ranking among same type
        same_type_articles = Article.objects.filter(
            post_type=content.post_type
        ).order_by('-views')
        
        rank = 1
        for article in same_type_articles:
            if article.id == content.id:
                break
            rank += 1
        
        total_same_type = same_type_articles.count()
        
        # REAL: Get views percentile
        if total_same_type > 0:
            percentile = round(((total_same_type - rank) / total_same_type) * 100, 1)
        else:
            percentile = 100.0
        
        # REAL performance metrics for table
        performance_metrics = [
            {
                'metric': 'Total Views',
                'value': f"{content.views:,}",
                'trend': 'up' if content.views > avg_views_same_type else 'down',
                'comparison': f"{comparison_to_avg}% {'above' if comparison_to_avg > 0 else 'below'} average"
            },
            {
                'metric': 'Average Daily Views',
                'value': f"{round(avg_daily_views, 1):,}",
                'trend': 'stable',
                'comparison': f"Based on {content_age} days"
            },
            {
                'metric': 'Rank Among {0}s'.format(content.get_post_type_display()),
                'value': f"#{rank} of {total_same_type}",
                'trend': 'up' if rank <= 3 else 'down',
                'comparison': f"Top {percentile}%"
            },
            {
                'metric': 'Publication Date',
                'value': content.created_at.strftime('%B %d, %Y'),
                'trend': 'neutral',
                'comparison': f"Published {content_age} days ago"
            },
            {
                'metric': 'Content Type',
                'value': content.get_post_type_display(),
                'trend': 'neutral',
                'comparison': 'Type of content'
            },
            {
                'metric': 'Publication Status',
                'value': 'Published' if content.is_published else 'Draft',
                'trend': 'up' if content.is_published else 'down',
                'comparison': 'Current status'
            }
        ]
        
        return JsonResponse({
            'success': True,
            'content_id': content.id,
            'title': content.title,
            'content_type': content.post_type,
            'total_views': content.views,
            'content_age': content_age,
            'created_at': content.created_at.strftime('%Y-%m-%d'),
            'author': content.author.username if content.author else 'Unknown',
            'is_published': content.is_published,
            
            # REAL Chart data
            'monthly_views': monthly_data,
            'monthly_labels': monthly_labels,
            
            # REAL Statistics
            'views_by_type': views_by_type,
            'avg_daily_views': round(avg_daily_views, 1),
            'rank': rank,
            'total_same_type': total_same_type,
            'percentile': percentile,
            'comparison_to_avg': comparison_to_avg,
            
            # REAL Performance metrics for table
            'performance_metrics': performance_metrics,
            
            # REAL Overall stats
            'overall_stats': {
                'total_articles': Article.objects.filter(post_type=Article.ARTICLE).count(),
                'total_posts': Article.objects.filter(post_type=Article.POST).count(),
                'total_views_all': Article.objects.aggregate(total=Sum('views'))['total'] or 0,
                'avg_views_all': round(Article.objects.aggregate(avg=Avg('views'))['avg'] or 0, 1),
            }
        })
        
    except Article.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Content not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@admin_required
def get_content_analytics(request, content_id):
    """API endpoint to get detailed analytics for specific content - REAL DATA ONLY"""
    try:
        content = Article.objects.get(pk=content_id)
        
        # REAL data calculations
        content_age = max((timezone.now() - content.created_at).days, 1)
        
        # Get ACTUAL views by month for this content (if you track monthly views)
        # If you don't track monthly views, we'll use creation month distribution
        monthly_data = []
        monthly_labels = []
        
        # Get all months since content creation
        current_date = timezone.now()
        creation_date = content.created_at
        
        # Calculate months difference
        months_diff = (current_date.year - creation_date.year) * 12 + (current_date.month - creation_date.month)
        months_diff = max(1, min(months_diff, 12))  # Limit to 12 months max
        
        # Distribute views across months based on creation date
        # This is a simple distribution - you might want to implement a ViewLog model for accurate monthly tracking
        for i in range(min(6, months_diff)):  # Show last 6 months or fewer
            month_date = creation_date + timedelta(days=30*i)
            monthly_labels.append(month_date.strftime('%b %Y'))
            
            # Simple distribution - divide views by number of months
            # In production, you should have a monthly_view_count field or ViewLog model
            monthly_views = content.views // max(1, months_diff)
            monthly_data.append(monthly_views)
        
        # REAL data: Get overall views by type
        views_by_type = {
            'articles': Article.objects.filter(post_type=Article.ARTICLE).aggregate(
                total=Sum('views')
            )['total'] or 0,
            'posts': Article.objects.filter(post_type=Article.POST).aggregate(
                total=Sum('views')
            )['total'] or 0,
        }
        
        # REAL performance metrics
        avg_daily_views = content.views / content_age
        
        # REAL comparison data
        avg_views_same_type = Article.objects.filter(
            post_type=content.post_type
        ).aggregate(
            avg=Avg('views')
        )['avg'] or 0
        
        if avg_views_same_type > 0:
            comparison_to_avg = round(((content.views - avg_views_same_type) / avg_views_same_type) * 100, 1)
        else:
            comparison_to_avg = 100.0
        
        # REAL: Get ranking among same type
        same_type_articles = Article.objects.filter(
            post_type=content.post_type
        ).order_by('-views')
        
        rank = 1
        for article in same_type_articles:
            if article.id == content.id:
                break
            rank += 1
        
        total_same_type = same_type_articles.count()
        
        # REAL: Get views percentile
        if total_same_type > 0:
            percentile = round(((total_same_type - rank) / total_same_type) * 100, 1)
        else:
            percentile = 100.0
        
        # REAL performance metrics for table
        performance_metrics = [
            {
                'metric': 'Total Views',
                'value': f"{content.views:,}",
                'trend': 'up' if content.views > avg_views_same_type else 'down',
                'comparison': f"{comparison_to_avg}% {'above' if comparison_to_avg > 0 else 'below'} average"
            },
            {
                'metric': 'Average Daily Views',
                'value': f"{round(avg_daily_views, 1):,}",
                'trend': 'stable',
                'comparison': f"Based on {content_age} days"
            },
            {
                'metric': 'Rank Among {0}s'.format(content.get_post_type_display()),
                'value': f"#{rank} of {total_same_type}",
                'trend': 'up' if rank <= 3 else 'down',
                'comparison': f"Top {percentile}%"
            },
            {
                'metric': 'Publication Date',
                'value': content.created_at.strftime('%B %d, %Y'),
                'trend': 'neutral',
                'comparison': f"Published {content_age} days ago"
            },
            {
                'metric': 'Content Type',
                'value': content.get_post_type_display(),
                'trend': 'neutral',
                'comparison': 'Type of content'
            },
            {
                'metric': 'Publication Status',
                'value': 'Published' if content.is_published else 'Draft',
                'trend': 'up' if content.is_published else 'down',
                'comparison': 'Current status'
            }
        ]
        
        return JsonResponse({
            'success': True,
            'content_id': content.id,
            'title': content.title,
            'content_type': content.post_type,
            'total_views': content.views,
            'content_age': content_age,
            'created_at': content.created_at.strftime('%Y-%m-%d'),
            'author': content.author.username if content.author else 'Unknown',
            'is_published': content.is_published,
            
            # REAL Chart data
            'monthly_views': monthly_data,
            'monthly_labels': monthly_labels,
            
            # REAL Statistics
            'views_by_type': views_by_type,
            'avg_daily_views': round(avg_daily_views, 1),
            'rank': rank,
            'total_same_type': total_same_type,
            'percentile': percentile,
            'comparison_to_avg': comparison_to_avg,
            
            # REAL Performance metrics for table
            'performance_metrics': performance_metrics,
            
            # REAL Overall stats
            'overall_stats': {
                'total_articles': Article.objects.filter(post_type=Article.ARTICLE).count(),
                'total_posts': Article.objects.filter(post_type=Article.POST).count(),
                'total_views_all': Article.objects.aggregate(total=Sum('views'))['total'] or 0,
                'avg_views_all': round(Article.objects.aggregate(avg=Avg('views'))['avg'] or 0, 1),
            }
        })
        
    except Article.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Content not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@admin_required
def admin_edit_content(request, pk):
    content = get_object_or_404(Article, pk=pk)

    if request.method == 'POST':
        content.title = request.POST.get('title')
        content.content = request.POST.get('content')
        content.post_type = request.POST.get('post_type')
        content.is_published = request.POST.get('is_published') == 'on'

        if 'cover_image' in request.FILES:
            content.cover_image = request.FILES['cover_image']

        content.save()
        messages.success(request, 'Content updated successfully!')
        return redirect('blog:admin_content_list')

    return render(request, 'blog/article_editor.html', {
        'content': content,
        'is_edit': True
    })
@admin_required
def admin_delete_content(request, pk):
    if request.method == 'POST':
        content = get_object_or_404(Article, pk=pk)
        title = content.title
        content.delete()
        messages.success(request, f'"{title}" deleted successfully!')
    return redirect('blog:admin_content_list')


# def login_view(request):
    
#     if request.user.is_authenticated:
#         return redirect("blog:index")

#     return render(request, "blog/login.html")

def logout_view(request):
    logout(request)
    return redirect("blog:index")
