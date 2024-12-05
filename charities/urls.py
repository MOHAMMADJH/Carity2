# charities/urls.py
from django.urls import path
from . import views
from .views import CharityNewsListView, CharityNewsDetailView
from .views import charity_dashboard, charity_create, charity_edit, charity_delete,social_media_publish

app_name = 'charities'

urlpatterns = [
    path('', views.home, name='home'),
    path('charities/', views.charity_list, name='charity_list'),
    path('news/', CharityNewsListView.as_view(), name='news_list'),
    path('charity/<int:pk>/', views.charity_detail, name='charity_detail'),
    path('news/<int:pk>/', CharityNewsDetailView.as_view(), name='news_detail'),
    path('aid-request/', views.aid_request_create, name='aid_request_create'),
    path('aid-requests/', views.aid_request_list, name='aid_request_list'),
    path('important-links/', views.important_links, name='important_links'),
    path('dashboard/', views.main_dashboard, name='main_dashboard'),
    path('dashboard/charities/', views.charity_dashboard, name='charity_dashboard'),
    path('dashboard/charities/create/', charity_create, name='charity_create'),
    path('dashboard/charities/edit/<int:pk>/', charity_edit, name='charity_edit'),
    path('dashboard/charities/delete/<int:pk>/', charity_delete, name='charity_delete'),
    path('dashboard/news/', views.news_dashboard, name='news_dashboard'),
    path('dashboard/news/create/', views.news_create, name='news_create'),
    path('dashboard/news/<int:pk>/edit/', views.news_edit, name='news_edit'),
    path('dashboard/news/<int:pk>/delete/', views.news_delete, name='news_delete'),
    # روابط المساعدة في لوحة التحكم
    path('dashboard/assistance-links/list/', views.assistance_links_list, name='assistance_links_list'),
    path('dashboard/assistance-links/create/', views.assistance_link_create, name='assistance_link_create'),
    path('dashboard/assistance-links/<int:pk>/edit/', views.assistance_link_edit, name='assistance_link_edit'),
    path('dashboard/assistance-links/<int:pk>/delete/', views.assistance_link_delete, name='assistance_link_delete'),
    
    path('publish/<str:model_type>/<int:pk>/', views.social_media_publish, name='social_media_publish'),
]