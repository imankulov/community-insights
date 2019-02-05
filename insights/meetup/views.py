import requests
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from insights.meetup.models import APICredentials


def start(request):
    redirect_url = ('https://secure.meetup.com/oauth2/authorize?client_id={}&'
                    'response_type=code&'
                    'redirect_uri={}').format(settings.MEETUP_OAUTH_CLIENT_ID,
                                              get_oauth_redirect(request))
    return HttpResponseRedirect(redirect_url)


def callback(request):
    code = request.GET['code']
    resp = requests.post(
        'https://secure.meetup.com/oauth2/access',
        data={
            'client_id': settings.MEETUP_OAUTH_CLIENT_ID,
            'client_secret': settings.MEETUP_OAUTH_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'redirect_uri': get_oauth_redirect(request),
            'code': code,
        })
    if resp.status_code != 200:
        return HttpResponse(resp.content)

    json_resp = resp.json()
    APICredentials.update_from_oauth(json_resp)
    return HttpResponse('meetup.com credentials stored')


def get_oauth_redirect(request):
    return request.build_absolute_uri(reverse('meetup-callback'))
