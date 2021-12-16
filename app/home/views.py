import logging
import httpx
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render
from .forms import ProfileForm, ApplicantsForm
from .models import GuildProfile, GuildNews, GuildApplicants
from .tasks import notify_guild_app

logger = logging.getLogger('app')


def is_guild_member(user):
    return user.guild_member


def is_guild_officer(user):
    return user.guild_officer


def home_view(request):
    # View: /
    if request.user.is_authenticated:
        user_profile = GuildProfile.objects.filter(
            id=request.user.username
        ).first()
    else:
        user_profile = None

    live_users = GuildProfile.objects.get_live()
    if live_users:
        live_user = live_users[0]
    else:
        live_user = None

    guild_news = GuildNews.objects.get_active().order_by('-pk')[:2]

    data = {
        'user_profile': user_profile,
        'guild_news': guild_news,
        'live_user': live_user,
    }
    return render(request, 'home.html', data)


def news_view(request):
    # View: /roster/
    guild_news = GuildNews.objects.get_active().order_by('-pk')[:50]
    return render(request, 'news.html', {'guild_news': guild_news})


def roster_view(request):
    # View: /roster/
    guild_roster = GuildProfile.objects.get_active().order_by('created_at')
    return render(request, 'roster.html', {'guild_roster': guild_roster})


@login_required
@user_passes_test(is_guild_member, login_url='/')
def profile_view(request):
    # View: /profile/
    if not request.method == 'POST':
        user_profile = GuildProfile.objects.filter(
            id=request.user.username
        ).first()
        user_profile = {} if not user_profile else user_profile
        data = {'user_profile': user_profile}
        return render(request, 'profile.html', data)

    else:
        try:
            logger.debug(request.POST)
            form = ProfileForm(request.POST)
            if form.is_valid():
                user_profile, created = GuildProfile.objects.get_or_create(
                    id=request.user.username)
                user_profile.main_char = form.cleaned_data['main_char']
                user_profile.main_class = form.cleaned_data['main_class']
                user_profile.main_role = form.cleaned_data['main_role']
                user_profile.user_description = form.cleaned_data['user_description']
                user_profile.twitch_username = form.cleaned_data['twitch_username']
                user_profile.show_in_roster = bool(form.cleaned_data['show_in_roster'])
                user_profile.save()
                return JsonResponse({}, status=200)
            else:
                return JsonResponse(form.errors, status=400)
        except Exception as error:
            logger.warning(error)
            return JsonResponse({'err_msg': str(error)}, status=400)


def apply_view(request):
    # View: /apply/
    if not request.method == 'POST':
        return render(request, 'apply.html')
    else:
        logger.debug(request.POST)
        form = ApplicantsForm(request.POST)
        if form.is_valid():
            if not google_verify(request):
                data = {'err_msg': 'Google CAPTCHA not verified.'}
                return JsonResponse(data, status=400)
            new_app = GuildApplicants(
                char_name=form.cleaned_data['char_name'],
                char_role=form.cleaned_data['char_role'],
                warcraft_logs=form.cleaned_data['warcraft_logs'],
                speed_test=form.cleaned_data['speed_test'],
                spoken_langs=form.cleaned_data['spoken_langs'],
                native_lang=form.cleaned_data['native_lang'],
                raid_1=form.cleaned_data['raid_1'],
                raid_2=form.cleaned_data['raid_2'],
                raid_exp=form.cleaned_data['raid_exp'],
                why_join=form.cleaned_data['why_join'],
                contact_info=form.cleaned_data['contact_info'],
            )
            new_app.save()
            request.session['application_submitted'] = True
            logger.debug('new_app.id: %s', new_app.id)
            notify_guild_app.delay(new_app.id)
            return JsonResponse({}, status=200)
        else:
            return JsonResponse(form.errors, status=400)


def google_verify(request):
    if 'gverified' in request.session and request.session['gverified']:
        return True
    try:
        url = 'https://www.google.com/recaptcha/api/siteverify'
        data = {
            'secret': settings.GOOGLE_SITE_SECRET,
            'response': request.POST['g-recaptcha-response']
        }
        r = httpx.post(url, data=data, timeout=6)
        j = r.json()
        logger.debug(j)
        if j['success']:
            request.session['gverified'] = True
            return True
        else:
            return False
    except Exception as error:
        logger.exception(error)
        return False
