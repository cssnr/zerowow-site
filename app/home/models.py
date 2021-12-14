from django.db import models
from .managers import GuildProfileManager, GuildNewsManager


class GuildProfile(models.Model):
    id = models.CharField(primary_key=True, max_length=32, verbose_name='Discord ID')
    main_char = models.CharField(unique=True, max_length=32, verbose_name='Main Character')
    main_class = models.CharField(max_length=32, verbose_name='Main Class')
    main_role = models.CharField(max_length=32, verbose_name='Main Role')
    user_description = models.TextField(blank=True, verbose_name='User Description')
    show_in_roster = models.BooleanField(default=True, verbose_name='Show in Roster')
    twitch_username = models.CharField(blank=True, max_length=32, verbose_name='Twitch Username')
    live_on_twitch = models.BooleanField(default=False, verbose_name='Twitch Live Status')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = GuildProfileManager()

    def __str__(self):
        return '{} - {}'.format(self.main_char, self.main_class)

    class Meta:
        verbose_name = 'Guild Profile'
        verbose_name_plural = 'Guild Profiles'


class GuildNews(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64, verbose_name='Title', help_text='The Title of the post.')
    display_name = models.CharField(max_length=32, verbose_name='Display Name',
                                    help_text='This should be your primary alias.')
    description = models.TextField(verbose_name='Description Body',
                                   help_text='The entire body and full text of the post. Newlines are allowed.')
    published = models.BooleanField(default=False, verbose_name='Published',
                                    help_text='The post will not show up unless this is checked.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = GuildNewsManager()

    def __str__(self):
        return '{} - {}'.format(self.display_name, self.title)

    class Meta:
        verbose_name = 'Guild News'
        verbose_name_plural = 'Guild News'


class GuildApplicants(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    DECLINED = 'declined'
    APP_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (DECLINED, 'Declined'),
    ]
    id = models.AutoField(primary_key=True)
    char_name = models.CharField(max_length=32, verbose_name='Character Name')
    char_role = models.CharField(max_length=32, verbose_name='Character Role')
    warcraft_logs = models.URLField(verbose_name='Warcraft Logs URL')
    speed_test = models.URLField(verbose_name='Speed Test URL')
    spoken_langs = models.CharField(max_length=32, verbose_name='Spoken Languages')
    native_lang = models.CharField(max_length=32, verbose_name='Native Language')
    raid_1 = models.BooleanField(default=False, verbose_name='Raid 1')
    raid_2 = models.BooleanField(default=False, verbose_name='Raid 2')
    raid_exp = models.TextField(blank=True, verbose_name='Raid Experience')
    why_join = models.TextField(blank=True, verbose_name='Why Zero')
    contact_info = models.CharField(max_length=128, verbose_name='Contact Information')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    app_status = models.CharField(
        max_length=8,
        choices=APP_STATUS_CHOICES,
        default=PENDING,
    )

    def __str__(self):
        return '{} - {}'.format(self.char_name, self.char_role)

    class Meta:
        verbose_name = 'Guild Applicants'
        verbose_name_plural = 'Guild Applicants'


class TwitchToken(models.Model):
    id = models.AutoField(primary_key=True)
    access_token = models.CharField(blank=True, max_length=32)
    expiration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.access_token
