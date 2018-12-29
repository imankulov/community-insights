import datetime

import pytz
import requests
import attr
from attr import NOTHING
from django.conf import settings
from django.utils import timezone
from django.db import models, transaction

from meetup.api_models import APICategory, APIGroup, APIGroupMember

API_CREDENTIALS_DATABASE_ID = 1
YEAR2000 = pytz.utc.localize(datetime.datetime(2000, 1, 1))


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


class MeetupCategory(models.Model):
    """
    Meetup category. The id of meetup.com is directly mapped to the id of the
    object. Can be populated with "manage.py sync_categories"
    """
    shortname = models.CharField(max_length=1000)
    name = models.CharField(max_length=1000)

    @classmethod
    def from_api(cls, obj: APICategory):
        return MeetupCategory.objects.update_or_create(
            id=obj.id,
            defaults={
                'shortname': obj.shortname,
                'name': obj.name,
            })[0]

    def __str__(self):
        return f'{self.name} ({self.id})'

    class Meta:
        verbose_name = 'Meetup category'
        verbose_name_plural = 'Meetup categories'


class MeetupLocationManager(models.Manager):

    def get_by_natural_key(self, country, location):
        return self.get(country=country, location=location)


class MeetupLocation(models.Model):
    """
    Location model is used as a foreign key in GroupFilter to search for groups
    in "./manage.py sync_groups"
    """
    objects = MeetupLocationManager()

    country = models.CharField(max_length=4)
    location = models.CharField(max_length=100)

    def natural_key(self):
        return self.country, self.location

    class Meta:
        unique_together = (('country', 'location'),)

    def __str__(self):
        return f'{self.country}, {self.location}'


class MeetupGroupFilterManager(models.Manager):

    def get_by_natural_key(self, category, location):
        return self.get(category=category, location=location)

    def get_active(self):
        return self.get_queryset().filter(active=True).select_related(
            'category', 'location')


class MeetupGroupFilter(models.Model):
    """
    Filter which is created manually to keep track of groups we are interested
    in. All active filters are used when running "./manage.py sync_groups" to
    copy the information to Django models.
    """
    objects = MeetupGroupFilterManager()

    category = models.ForeignKey(MeetupCategory, on_delete=models.CASCADE)
    location = models.ForeignKey(MeetupLocation, on_delete=models.CASCADE)
    active = models.BooleanField(default=True, db_index=True)

    def natural_key(self):
        return self.category, self.location

    class Meta:
        unique_together = (('category', 'location'),)

    def __str__(self):
        ret = f'{self.category.name} in {self.location.location}'
        if not self.active:
            ret += ' (inactive)'
        return ret


class MeetupGroupManager(models.Manager):
    def members_update_required(self):
        return self.get_queryset().filter(
            members_next_update__lte=timezone.now(), visibility='public')


class MeetupGroup(models.Model):
    """
    Model which mirrors the group object from meetup.com API
    from https://www.meetup.com/pt-BR/meetup_api/docs/:urlname/

    The only option which is supposed to be changed from inside the app is
    the "members_next_update" attribute, which keeps track of when the upcoming
    sync of members has to be performed.

    Groups populated from the API with "./manage.py sync_groups"
    """
    objects = MeetupGroupManager()

    name = models.CharField(max_length=1000)
    status = models.CharField(max_length=1000)
    urlname = models.CharField(max_length=100, db_index=True)
    description = models.TextField()
    created = models.DateTimeField()
    city = models.CharField(max_length=1000)
    untranslated_city = models.CharField(max_length=1000)
    country = models.CharField(max_length=1000)
    state = models.CharField(max_length=1000)
    join_mode = models.CharField(max_length=1000)
    visibility = models.CharField(max_length=50)
    lat = models.FloatField(max_length=1000)
    lon = models.FloatField(max_length=1000)
    members = models.PositiveIntegerField()
    who = models.CharField(max_length=1000)
    organizer_id = models.PositiveIntegerField()
    organizer_name = models.CharField(max_length=1000)
    timezone = models.CharField(max_length=1000)
    next_event_id = models.CharField(max_length=1000, null=True)
    next_event_name = models.CharField(max_length=1000, null=True)
    next_event_yes_rsvp_count = models.PositiveIntegerField(null=True)
    next_event_time = models.DateTimeField(null=True)
    category_id = models.PositiveIntegerField()
    category_shortname = models.CharField(max_length=1000)
    meta_category_id = models.PositiveIntegerField()
    meta_category_shortname = models.CharField(max_length=1000)

    members_next_update = models.DateTimeField(default=YEAR2000)

    class Meta:
        indexes = [
            models.Index(fields=['members_next_update', 'visibility']),
        ]

    @classmethod
    def from_api(cls, obj: APIGroup):
        """
        Create a model instance from meetup API object.
        We use api_instance "id" as unique key
        """
        obj_dict = attr.asdict(obj)

        kwargs = {}
        defaults = {}
        for field in cls._meta.fields:
            if field.primary_key:
                kwargs[field.name] = obj_dict[field.name]
            else:
                if field.name in obj_dict:
                    default_value = obj_dict[field.name]
                    if default_value is not NOTHING:
                        defaults[field.name] = default_value

        return cls.objects.update_or_create(defaults=defaults, **kwargs)[0]

    def __str__(self):
        return f'{self.name}'


class MeetupUser(models.Model):
    """
    Model which mirrors user object of the meetup.com API
    from https://www.meetup.com/pt-BR/meetup_api/docs/2/member/

    Users are generated automatically with
    `./manage.py sync_group_members`
    """
    name = models.CharField(max_length=1000)
    status = models.CharField(max_length=1000)
    joined = models.DateTimeField()
    city = models.CharField(max_length=1000)
    country = models.CharField(max_length=1000)
    lat = models.FloatField()
    lon = models.FloatField()
    is_pro_admin = models.BooleanField(default=False)
    messaging_pref = models.CharField(max_length=1000)
    privacy_bio = models.CharField(max_length=1000)
    privacy_groups = models.CharField(max_length=1000)
    privacy_topics = models.CharField(max_length=1000)

    def __str__(self):
        return f'{self.name}'


class MeetupGroupMemberManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('user', 'group')


class MeetupGroupMember(models.Model):
    """
    Group-specific information for user. Populated and updated automatically
    with `./manage.py sync_group_members`
    """
    objects = MeetupGroupMemberManager()

    user = models.ForeignKey(MeetupUser, on_delete=models.CASCADE)
    group = models.ForeignKey(MeetupGroup, on_delete=models.CASCADE)

    status = models.CharField(max_length=1000)
    visited = models.DateTimeField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    role = models.CharField(max_length=1000, null=True)

    @classmethod
    def from_api(cls, group: MeetupGroup, obj: APIGroupMember):
        """
        Get or create MeetupUser and MeetupGroupMember instances from the
        API. Return the MeetupGroupMember instance
        """
        # Create a user
        obj_dict = attr.asdict(obj)
        user_kwargs = {}
        user_defaults = {}
        for field in MeetupUser._meta.fields:
            if field.primary_key:
                user_kwargs[field.name] = obj_dict[field.name]
            else:
                default_value = obj_dict[field.name]
                if default_value is not NOTHING:
                    user_defaults[field.name] = obj_dict[field.name]
        user = MeetupUser.objects.update_or_create(
            defaults=user_defaults, **user_kwargs)[0]

        # Now create a GroupMember instance
        role = obj.group_role
        if role is NOTHING:
            role = None
        return cls.objects.update_or_create(
            user=user,
            group=group,
            defaults={
                'status': obj.group_status,
                'visited': obj.group_visited,
                'created': obj.group_created,
                'updated': obj.group_updated,
                'role': role,
            })[0]

    def __str__(self):
        return f'{self.user.name} in {self.group.name}'
