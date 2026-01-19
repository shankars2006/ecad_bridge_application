from django.urls import path
from . import views


# app_name = 'blog'
app_name = 'blog'
urlpatterns = [
    path('', views.index, name='index'),
    path('Terms&Conditions', views.tc, name='tc'),
    path('posts', views.posts, name='posts'),
    path('detail/<str:slug>', views.post_detail, name='detail'),
    path('contact', views.contact, name='contact'),
    path('about', views.about, name='about'),
    path('article/create/', views.create_article, name='create_article'),
    path('upload-image/', views.tinymce_image_upload, name='tinymce_image_upload'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('contact_details', views.contact_details, name='contact_details'),
    path('articles', views.articles, name='articles'),
    path('admin_base', views.admin_base, name='admin_base'),
    path('admin_base/content/', views.admin_content_list, name='admin_content_list'),
    path('admin_base/content/edit/<int:pk>/', views.admin_edit_content, name='admin_edit_content'),
    path('admin_base/content/delete/<int:pk>/', views.admin_delete_content, name='admin_delete_content'),
    path('api/content/<int:content_id>/analytics/', views.get_content_analytics, name='content_analytics'),
    # path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    ]