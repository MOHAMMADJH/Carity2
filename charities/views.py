# charities/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.views.generic import ListView, DetailView
import requests
import json
from .models import Charity, AidType, AidRequest, CharityNews, CharityAssistanceLink
from .forms import AidRequestForm, CharityNewsForm, CharityForm, CharityAssistanceLinkForm
from telegram import Bot
from django.conf import settings
from asgiref.sync import async_to_sync
from django.db.models import Count

from telegram import Bot
from django.conf import settings
import asyncio

async def publish_to_telegram(news):
    try:
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        message = f"""
🗞️ *{news.title}*

{news.content[:500]}...

📍 المصدر: {news.charity.name}
🔗 للمزيد: {news.get_absolute_url()}
"""
        # Send message with optional image
        if news.image:
            with open(news.image.path, 'rb') as photo_file:
                await bot.send_photo(
                    chat_id=settings.TELEGRAM_CHANNEL_ID, 
                    photo=photo_file,
                    caption=message,
                    parse_mode='Markdown',
                    read_timeout=30,
                    connect_timeout=30
                )
        else:
            await bot.send_message(
                chat_id=settings.TELEGRAM_CHANNEL_ID, 
                text=message,
                parse_mode='Markdown',
                read_timeout=30,
                connect_timeout=30
            )
        return True
    except Exception as e:
        print(f"Telegram publishing error: {e}")
        return False

async def publish_to_instagram(news):
    try:
        base_url = f"https://graph.facebook.com/v18.0/{settings.INSTAGRAM_BUSINESS_ACCOUNT_ID}"
        caption = f"{news.title}\n\n{news.content[:200]}...\n\nالمصدر: {news.charity.name}"
        
        if news.image:
            # Create media container
            container_response = requests.post(
                f"{base_url}/media",
                params={
                    'access_token': settings.INSTAGRAM_ACCESS_TOKEN,
                    'image_url': news.image.url,
                    'caption': caption
                }
            )
            
            if container_response.status_code != 200:
                raise Exception(f"Error creating media container: {container_response.text}")
            
            # Publish the container
            publish_response = requests.post(
                f"{base_url}/media_publish",
                params={
                    'access_token': settings.INSTAGRAM_ACCESS_TOKEN,
                    'creation_id': container_response.json().get('id')
                }
            )
            
            if publish_response.status_code != 200:
                raise Exception(f"Error publishing media: {publish_response.text}")
        
        return True
    except Exception as e:
        print(f"Instagram publishing error: {e}")
        return False
        
def home(request):
    featured_charities = Charity.objects.filter(is_active=True)[:3]
    aid_types = AidType.objects.all()
    
    context = {
        'featured_charities': featured_charities,
        'aid_types': aid_types,
    }
    return render(request, 'charities/home.html', context)
    
def charity_list(request):
    charities = Charity.objects.filter(is_active=True)
    return render(request, 'charities/charity_list.html', {'charities': charities})

def charity_detail(request, pk):
    charity = get_object_or_404(Charity, pk=pk)
    aid_types = AidType.objects.all()
    return render(request, 'charities/charity_detail.html', {
        'charity': charity,
        'aid_types': aid_types
    })

def important_links(request):
    """عرض صفحة أهم الروابط والأخبار المهمة"""
    assistance_links = CharityAssistanceLink.objects.filter(is_active=True).select_related('charity')
    latest_news = CharityNews.objects.filter(is_important=True).order_by('-publication_date')[:5]
    return render(request, 'charities/important_links.html', {
        'assistance_links': assistance_links,
        'latest_news': latest_news,
    })

@login_required
def aid_request_create(request):
    if request.method == 'POST':
        form = AidRequestForm(request.POST, request.FILES)
        if form.is_valid():
            aid_request = form.save(commit=False)
            aid_request.requester = request.user
            aid_request.save()
            return redirect('charities:aid_request_list')
    else:
        form = AidRequestForm()
    return render(request, 'charities/aid_request_form.html', {'form': form})

@login_required
def aid_request_list(request):
    if request.user.is_charity_admin():
        aid_requests = AidRequest.objects.filter(charity=request.user.charity)
    else:
        aid_requests = AidRequest.objects.filter(requester=request.user)
    return render(request, 'charities/aid_request_list.html', {'aid_requests': aid_requests})



class CharityNewsListView(ListView):
    model = CharityNews
    template_name = 'charities/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 9

    def get_queryset(self):
        # استثناء الأخبار العاجلة والمهمة من القائمة الرئيسية
        queryset = CharityNews.objects.all()

        # تصفية حسب الوسم إذا تم تحديده
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__icontains=tag)
        
        # استثناء الأخبار العاجلة والمهمة
        queryset = queryset.exclude(
            is_breaking=True
        ).exclude(
            is_important=True,
            important_until__gte=timezone.now()
        ).order_by('-publication_date')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # الأخبار العاجلة - آخر خبر عاجل فقط
        context['breaking_news'] = CharityNews.objects.filter(
            is_breaking=True
        ).order_by('-publication_date')[:1]
        
        # الأخبار المهمة
        context['important_news'] = CharityNews.objects.filter(
            is_important=True,
            is_breaking=False,  # استثناء الأخبار العاجلة من المهمة
            important_until__gte=timezone.now()
        ).order_by('-publication_date')[:6]
        
        # الأخبار الأكثر قراءة
        context['most_read_news'] = CharityNews.objects.order_by('-views_count')[:5]
        
        # جمع كل الوسوم الفريدة
        all_tags = set()
        for news in CharityNews.objects.exclude(tags=''):
            all_tags.update(news.get_tags_list())
        context['all_tags'] = sorted(all_tags)
        
        # الوسم المحدد حالياً
        context['selected_tag'] = self.request.GET.get('tag')
        
        return context

class CharityNewsDetailView(DetailView):
    model = CharityNews
    template_name = 'charities/news_detail.html'
    context_object_name = 'news'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.increment_views()  # زيادة عداد المشاهدات
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['important_news'] = CharityNews.objects.filter(
            is_important=True,
            important_until__gte=timezone.now()
        ).exclude(pk=self.object.pk)[:3]
        
        # الأخبار المشابهة (نفس الوسوم)
        news_tags = self.object.get_tags_list()
        if news_tags:
            similar_news = CharityNews.objects.exclude(pk=self.object.pk)
            for tag in news_tags:
                similar_news = similar_news.filter(tags__icontains=tag)
            context['similar_news'] = similar_news[:3]
        
        return context


# @login_required
# def charity_dashboard(request):
#     charities = Charity.objects.all()
#     return render(request, 'charities/charity_dashboard.html', {'charities': charities})

@login_required
def charity_dashboard(request):
    """عرض قائمة الجمعيات في لوحة التحكم"""
    charities = Charity.objects.annotate(
        news_count=Count('charitynews'),
        aid_requests_count=Count('aidrequest')
    ).order_by('-created_at')
    
    return render(request, 'charities/dashboard/charities_list.html', {
        'charities': charities
    })

@login_required
def charity_create(request):
    if request.method == 'POST':
        form = CharityForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('charities:charity_dashboard')
    else:
        form = CharityForm()
    return render(request, 'charities/charity_form.html', {'form': form})

@login_required
def charity_edit(request, pk):
    charity = get_object_or_404(Charity, pk=pk)
    if request.method == 'POST':
        form = CharityForm(request.POST, request.FILES, instance=charity)
        if form.is_valid():
            form.save()
            return redirect('charities:charity_dashboard')
    else:
        form = CharityForm(instance=charity)
    return render(request, 'charities/charity_form.html', {'form': form})

@login_required
def charity_delete(request, pk):
    charity = get_object_or_404(Charity, pk=pk)
    if request.method == 'POST':
        charity.delete()
        return redirect('charities:charity_dashboard')
    return render(request, 'charities/charity_confirm_delete.html', {'charity': charity})

# @login_required
# def news_dashboard(request):
#     """عرض قائمة الأخبار في لوحة التحكم"""
#     news_list = CharityNews.objects.all().order_by('-publication_date')
#     return render(request, 'charities/dashboard/news_list.html', {
#         'news_list': news_list
#     })

@login_required
def news_dashboard(request):
    """عرض قائمة الأخبار في لوحة التحكم"""
    news_list = CharityNews.objects.select_related('charity').order_by('-publication_date')
    return render(request, 'charities/dashboard/news_list.html', {
        'news_list': news_list
    })

@login_required
def news_create(request):
    if request.method == 'POST':
        form = CharityNewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save()
            
            # Handle Telegram publishing
            if form.cleaned_data.get('telegram_enabled'):
                success = async_to_sync(publish_to_telegram)(news)
                if success:
                    messages.success(request, 'تم نشر الخبر بنجاح على تلجرام')
                else:
                    messages.error(request, 'حدث خطأ أثناء النشر على تلجرام')
            
            # Handle Instagram publishing
            if form.cleaned_data.get('instagram_enabled'):
                success = async_to_sync(publish_to_instagram)(news)
                if success:
                    messages.success(request, 'تم نشر الخبر بنجاح على انستقرام')
                else:
                    messages.error(request, 'حدث خطأ أثناء النشر على انستقرام')
            
            messages.success(request, 'تم إضافة الخبر بنجاح')
            return redirect('charities:news_dashboard')
    else:
        form = CharityNewsForm()
    
    return render(request, 'charities/dashboard/news_form.html', {
        'form': form,
        'title': 'إضافة خبر جديد'
    })

@login_required
def news_update(request, pk):
    news = get_object_or_404(CharityNews, pk=pk)
    if request.method == 'POST':
        form = CharityNewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            news = form.save()
            
            # Check if Telegram publishing is enabled
            if form.cleaned_data.get('telegram_enabled'):
                success = async_to_sync(publish_to_telegram)(news)
                if success:
                    messages.success(request, 'تم نشر الخبر بنجاح على تلجرام')
                else:
                    messages.error(request, 'حدث خطأ أثناء النشر على تلجرام')

            # Check if Instagram publishing is enabled
            if form.cleaned_data.get('instagram_enabled'):
                success = async_to_sync(publish_to_instagram)(news)
                if success:
                    messages.success(request, 'تم نشر الخبر بنجاح على إنستجرام')
                else:
                    messages.error(request, 'حدث خطأ أثناء النشر على إنستجرام')

            return redirect('charities:news_dashboard')
    # ... rest of the view remains the same

@login_required
def news_edit(request, pk):
    """تعديل خبر"""
    news = get_object_or_404(CharityNews, pk=pk)
    if request.method == 'POST':
        form = CharityNewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            news = form.save()
            
            # Check if Telegram publishing is enabled
            if form.cleaned_data.get('telegram_enabled'):
                success = async_to_sync(publish_to_telegram)(news)
                if success:
                    messages.success(request, 'تم نشر الخبر بنجاح على تلجرام')
                else:
                    messages.error(request, 'حدث خطأ أثناء النشر على تلجرام')

            # Check if Instagram publishing is enabled
            if form.cleaned_data.get('instagram_enabled'):
                success = async_to_sync(publish_to_instagram)(news)
                if success:
                    messages.success(request, 'تم نشر الخبر بنجاح على إنستجرام')
                else:
                    messages.error(request, 'حدث خطأ أثناء النشر على إنستجرام')

            messages.success(request, 'تم تحديث الخبر بنجاح')
            return redirect('charities:news_dashboard')
    else:
        form = CharityNewsForm(instance=news)
    
    return render(request, 'charities/dashboard/news_form.html', {
        'form': form,
        'news': news,
        'title': 'تعديل الخبر'
    })

@login_required
def news_delete(request, pk):
    """حذف خبر"""
    news = get_object_or_404(CharityNews, pk=pk)
    if request.method == 'POST':
        news.delete()
        return redirect('charities:news_dashboard')
    return render(request, 'charities/dashboard/news_confirm_delete.html', {
        'news': news
    })

@login_required
def main_dashboard(request):
    """عرض لوحة التحكم الرئيسية"""
    context = {
        'charities_count': Charity.objects.count(),
        'active_charities': Charity.objects.filter(is_active=True).count(),
        'news_count': CharityNews.objects.count(),
        'aid_requests_count': AidRequest.objects.count(),
        'recent_news': CharityNews.objects.order_by('-publication_date')[:5],
        'recent_aid_requests': AidRequest.objects.order_by('-created_at')[:5],
        'recent_charities': Charity.objects.order_by('-created_at')[:5],
    }
    return render(request, 'charities/dashboard/main_dashboard.html', context)

@login_required
def assistance_links_list(request):
    """عرض قائمة روابط المساعدة في لوحة التحكم"""
    links = CharityAssistanceLink.objects.all().select_related('charity').order_by('-created_at')
    return render(request, 'charities/dashboard/assistance_links_list.html', {
        'links': links
    })

@login_required
def assistance_link_create(request):
    """إضافة رابط مساعدة جديد"""
    if request.method == 'POST':
        form = CharityAssistanceLinkForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة الرابط بنجاح')
            return redirect('assistance_links_list')
    else:
        form = CharityAssistanceLinkForm()
    
    return render(request, 'charities/dashboard/assistance_links_form.html', {
        'form': form,
        'title': 'إضافة رابط مساعدة جديد'
    })

@login_required
def assistance_link_edit(request, pk):
    """تعديل رابط مساعدة"""
    link = get_object_or_404(CharityAssistanceLink, pk=pk)
    if request.method == 'POST':
        form = CharityAssistanceLinkForm(request.POST, instance=link)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الرابط بنجاح')
            return redirect('assistance_links_list')
    else:
        form = CharityAssistanceLinkForm(instance=link)
    
    return render(request, 'charities/dashboard/assistance_links_form.html', {
        'form': form,
        'title': 'تعديل رابط المساعدة'
    })

@login_required
def assistance_link_delete(request, pk):
    """حذف رابط مساعدة"""
    link = get_object_or_404(CharityAssistanceLink, pk=pk)
    if request.method == 'POST':
        link.delete()
        messages.success(request, 'تم حذف الرابط بنجاح')
        return redirect('assistance_links_list')
    return render(request, 'charities/dashboard/assistance_link_confirm_delete.html', {
        'link': link
    })
@login_required
def social_media_publish(request, model_type, pk):
    """نشر المحتوى على وسائل التواصل الاجتماعي"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'يجب استخدام طريقة POST'})

    # تحديد النموذج المناسب
    models_map = {
        'news': CharityNews,
        'charity': Charity,
        'assistance': CharityAssistanceLink
    }
    
    Model = models_map.get(model_type)
    if not Model:
        return JsonResponse({'status': 'error', 'message': 'نوع المحتوى غير صالح'})
    
    try:
        instance = Model.objects.get(pk=pk)
        
        # التحقق من تفعيل النشر الاجتماعي
        if not instance.social_publish:
            return JsonResponse({'status': 'error', 'message': 'النشر الاجتماعي غير مفعل لهذا المحتوى'})
        
        success_platforms = []
        error_platforms = []
        
        # تحضير بيانات النشر
        title = getattr(instance, 'title', '') or getattr(instance, 'name', '')
        description = instance.social_description or getattr(instance, 'description', '') or getattr(instance, 'content', '')
        image_url = instance.social_image.url if instance.social_image else None
        
        # نشر على فيسبوك
        if instance.facebook_enabled and hasattr(settings, 'FACEBOOK_ACCESS_TOKEN'):
            try:
                fb_response = publish_to_facebook(title, description, image_url)
                if fb_response.get('success'):
                    success_platforms.append('facebook')
                else:
                    error_platforms.append(('facebook', fb_response.get('error')))
            except Exception as e:
                error_platforms.append(('facebook', str(e)))
        
        # نشر على تويتر
        if instance.twitter_enabled and hasattr(settings, 'TWITTER_ACCESS_TOKEN'):
            try:
                twitter_response = publish_to_twitter(title, description, image_url)
                if twitter_response.get('success'):
                    success_platforms.append('twitter')
                else:
                    error_platforms.append(('twitter', twitter_response.get('error')))
            except Exception as e:
                error_platforms.append(('twitter', str(e)))
        
        # نشر على تلقرام
        if instance.telegram_enabled and hasattr(settings, 'TELEGRAM_BOT_TOKEN'):
            try:
                telegram_response = publish_to_telegram(title, description, image_url)
                if telegram_response.get('success'):
                    success_platforms.append('telegram')
                else:
                    error_platforms.append(('telegram', telegram_response.get('error')))
            except Exception as e:
                error_platforms.append(('telegram', str(e)))
        
        # نشر على إنستجرام
        if instance.instagram_enabled and hasattr(settings, 'INSTAGRAM_ACCESS_TOKEN'):
            try:
                instagram_response = publish_to_instagram(title, description, image_url)
                if instagram_response.get('success'):
                    success_platforms.append('instagram')
                else:
                    error_platforms.append(('instagram', instagram_response.get('error')))
            except Exception as e:
                error_platforms.append(('instagram', str(e)))
        
        # تحديث وقت آخر نشر
        instance.last_social_publish = timezone.now()
        instance.save()
        
        return JsonResponse({
            'status': 'success',
            'success_platforms': success_platforms,
            'error_platforms': error_platforms
        })
        
    except Model.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'المحتوى غير موجود'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
