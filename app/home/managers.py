from django.db import models


class GuildProfileManager(models.Manager):
    def get_active(self):
        return self.filter(show_in_roster=True)

    def get_live(self):
        return self.filter(live_on_twitch=True)


class GuildNewsManager(models.Manager):
    def get_active(self):
        return self.filter(published=True)
