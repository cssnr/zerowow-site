import httpx
import logging
import urllib.parse
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import Group
from django.shortcuts import HttpResponseRedirect, redirect
from django.views.decorators.http import require_http_methods
from .models import CustomUser

logger = logging.getLogger('app')


def oauth_start(request):
    """
    View  /oauth/
    """
    request.session['login_redirect_url'] = get_next_url(request)
    params = {
        'client_id': settings.OAUTH_CLIENT_ID,
        'redirect_uri': settings.OAUTH_REDIRECT_URI,
        'response_type': 'code',
        'scope': settings.OAUTH_SCOPE,
    }
    url_params = urllib.parse.urlencode(params)
    url = f'https://discord.com/api/oauth2/authorize?{url_params}'
    return HttpResponseRedirect(url)


def oauth_callback(request):
    """
    View  /oauth/callback/
    """
    if 'code' not in request.GET:
        messages.warning(request, 'Uer aborted or error during login.')
        return HttpResponseRedirect(get_login_redirect_url(request))
    try:
        auth_data = get_access_token(request.GET['code'])
        profile = get_user_profile(auth_data)
        user = login_user(request, profile)
        messages.info(request, f'Successfully logged in as {user.first_name}.')
    except Exception as error:
        logger.exception(error)
        messages.error(request, f'Exception during login: {error}')
    return HttpResponseRedirect(get_login_redirect_url(request))


@require_http_methods(['POST'])
def oauth_logout(request):
    """
    View  /oauth/logout/
    """
    next_url = get_next_url(request)
    # Hack to prevent login loop when logging out on a secure page
    logger.debug('next_url: %s', next_url.split('/')[1])
    if next_url.split('/')[1] in ['profile']:
        next_url = '/'
    request.session['login_next_url'] = next_url
    logout(request)
    messages.info(request, f'Successfully logged out.')
    return redirect(next_url)


def login_user(request, profile):
    """
    Login or create user
    """
    user, _ = CustomUser.objects.get_or_create(username=profile['id'])
    update_profile(user, profile)
    login(request, user)
    return user


def get_access_token(code):
    """
    Post OAuth code and Return access_token
    """
    url = f'{settings.DISCORD_API_URL}/oauth2/token'
    data = {
        'client_id': settings.OAUTH_CLIENT_ID,
        'client_secret': settings.OAUTH_CLIENT_SECRET,
        'grant_type': settings.OAUTH_GRANT_TYPE,
        'redirect_uri': settings.OAUTH_REDIRECT_URI,
        'code': code,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = httpx.post(url, data=data, headers=headers, timeout=10)
    if not r.is_success:
        logger.info('status_code: %s', r.status_code)
        logger.error('content: %s', r.content)
        r.raise_for_status()
    return r.json()


def get_user_profile(data):
    """
    Get Profile for Authenticated User
    """
    url = f'{settings.DISCORD_API_URL}/users/@me'
    headers = {'Authorization': f"Bearer {data['access_token']}"}
    r = httpx.get(url, headers=headers, timeout=10)
    if not r.is_success:
        logger.info('status_code: %s', r.status_code)
        logger.error('content: %s', r.content)
        r.raise_for_status()
    p = r.json()

    # get guild information
    url = '{}/guilds/{}/members/{}'.format(
        settings.DISCORD_API_URL,
        settings.DISCORD_SERVER_ID,
        p['id'],
    )
    headers = {
        'Authorization': 'Bot {}'.format(settings.DISCORD_BOT_TOKEN),
    }
    r = httpx.get(url, headers=headers, timeout=10)
    logger.debug('status_code: %s', r.status_code)
    logger.debug('content: %s', r.content)
    guild = r.json() if r.is_success else None

    return {
        'id': p['id'],
        'username': p['username'],
        'discriminator': p['discriminator'],
        'avatar': p['avatar'],
        'access_token': data['access_token'],
        'refresh_token': data['refresh_token'],
        'expires_in': datetime.now() + timedelta(0, data['expires_in']),
        'guild_member': settings.DISCORD_MEMBER_ROLE in guild['roles'] if guild else False,
        'guild_officer': settings.DISCORD_OFFICER_ROLE in guild['roles'] if guild else False,
        'discord_roles': guild['roles'] if guild else [],
    }


def update_profile(user, profile):
    """
    Update Django user profile with provided data
    """
    try:
        officers, _ = Group.objects.get_or_create(name='Officers')
        if profile['guild_officer']:
            logger.debug('Adding user to officers group: %s', user)
            officers.user_set.add(user)
        else:
            logger.debug('Removing user from officers group: %s', user)
            officers.user_set.remove(user)
    except Exception as error:
        logger.exception(error)

    member = profile['guild_member'] or profile['guild_officer']

    user.first_name = profile['username']
    user.last_name = profile['discriminator']
    user.avatar_hash = profile['avatar']
    user.access_token = profile['access_token']
    user.guild_member = member
    user.guild_officer = profile['guild_officer']
    user.is_staff = profile['guild_officer']
    user.save()
    return


def get_next_url(request):
    """
    Determine 'next' parameter
    """
    if 'next' in request.GET:
        return request.GET['next']
    if 'next' in request.POST:
        return request.POST['next']
    if 'next_url' in request.session:
        return request.session['next_url']
    return '/'


def get_login_redirect_url(request):
    """
    Determine 'login_redirect_url' parameter
    """
    next_url = '/'
    if 'login_redirect_url' in request.session:
        next_url = request.session['login_redirect_url']
    return next_url
