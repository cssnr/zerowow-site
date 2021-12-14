import datetime
import logging
import httpx
from celery import shared_task
from django.conf import settings
from django.utils.timezone import now
from home.models import TwitchToken, GuildProfile, GuildApplicants

logger = logging.getLogger('celery')


@shared_task(name='notify_guild_app')
def notify_guild_app(app_id):
    logger.info('notify_guild_app: executed')
    app = GuildApplicants.objects.get(id=app_id)
    message = ('New Guild Application: **{char_name} - {char_role}**\n'
               'Warcraft Logs: {warcraft_logs}\n'
               'Raid Experience:```\n{raid_exp}\n```').format(**app.__dict__)
    send_discord_message(settings.DISCORD_CHANNEL_ID, message)
    return 'Finished'


@shared_task(name='check_twitch_live')
def check_twitch_live():
    logger.debug('check_twitch_live: executed')
    access_token = get_twitch_token()
    logger.debug(access_token)

    profiles = GuildProfile.objects.all()
    twitch_usernames = [u.twitch_username for u in profiles if u.twitch_username]

    url = 'https://api.twitch.tv/helix/streams'
    params = {'user_login': twitch_usernames}
    headers = {
        'Client-ID': settings.TWITCH_CLIENT_ID,
        'Authorization': 'Bearer {}'.format(access_token),
    }
    r = httpx.get(url, params=params, headers=headers)
    if not r.is_success:
        r.raise_for_status()

    data = r.json()['data']
    live_users = [u['user_name'].lower() for u in data]
    for user in profiles:
        if not user.twitch_username:
            continue
        if user.twitch_username.lower() in live_users:
            user.live_on_twitch = True
        else:
            user.live_on_twitch = False
        user.save()
    return f'Processed {len(profiles)} user profiles.'


def get_twitch_token():
    token, created = TwitchToken.objects.get_or_create()
    if token and token.access_token and token.expiration_date:
        if token.expiration_date > now():
            return token.access_token

    url = 'https://id.twitch.tv/oauth2/token'
    data = {
        'client_id': settings.TWITCH_CLIENT_ID,
        'client_secret': settings.TWITCH_CLIENT_SECRET,
        'grant_type': 'client_credentials',
    }
    r = httpx.post(url, data=data)
    logger.debug(r.status_code)
    if not r.is_success:
        logger.info(r.content)
        r.raise_for_status()

    token_info = r.json()
    logger.debug(token_info)
    exp_date = now() + datetime.timedelta(0, token_info['expires_in'] - 300)
    token.access_token = token_info['access_token']
    token.expiration_date = exp_date
    token.save()
    return token.access_token


def send_discord_message(channel_id, message):
    url = '{}/channels/{}/messages'.format(
        settings.DISCORD_API_URL,
        channel_id,
    )
    headers = {
        'Authorization': 'Bot {}'.format(settings.DISCORD_BOT_TOKEN),
    }
    data = {'content': message}
    r = httpx.post(url, headers=headers, data=data, timeout=10)
    logger.debug(r.status_code)
    if not r.is_success:
        logger.info(r.content)
        r.raise_for_status()
    return r
