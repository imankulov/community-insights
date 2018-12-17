import datetime

import requests
from django.conf import settings
from django.utils import timezone
from django.db import models, transaction


API_CREDENTIALS_DATABASE_ID = 1


class APICredentials(models.Model):
    """
    A singleton to store API credentials
    """

    @classmethod
    @transaction.atomic
    def update_from_oauth(cls, oauth_response):
        """
        Classmethod to set access and refresh token from OAuth 2.0 response
        """
        expires_at = timezone.now() + datetime.timedelta(
            seconds=oauth_response['expires_in'] // 2)
        return APICredentials.objects.update_or_create(
            id=API_CREDENTIALS_DATABASE_ID,
            defaults=dict(
                access_token=oauth_response['access_token'],
                refresh_token=oauth_response['refresh_token'],
                expires_at=expires_at))

    @classmethod
    def get_access_token(cls):
        """
        Classmethod to return the access token, and refresh it if needed
        """
        # we expect to have exactly one object
        cred = APICredentials.objects.get(id=API_CREDENTIALS_DATABASE_ID)
        if cred.expires_at < timezone.now():
            cred.refresh()
        return cred.access_token

    def refresh(self):
        """
        Connect the server to get the fresh access token from the refresh
        token and save it locally
        """
        url = 'https://secure.meetup.com/oauth2/access'
        resp = requests.post(
            url,
            data={
                'client_id': settings.MEETUP_OAUTH_CLIENT_ID,
                'client_secret': settings.MEETUP_OAUTH_CLIENT_SECRET,
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
            })
        resp.raise_for_status()
        oauth_response = resp.json()
        self.access_token = oauth_response['access_token']
        self.expires_at = timezone.now() + datetime.timedelta(
            seconds=oauth_response['expires_in'] // 2)
        self.save()

    access_token = models.CharField(max_length=1000)
    expires_at = models.DateTimeField()
    refresh_token = models.CharField(max_length=1000)

    class Meta:
        verbose_name = 'API credentials'
        verbose_name_plural = 'API credentials'
