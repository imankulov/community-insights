"""
A set of functions to work with Meetup API.

Credentials don't have to be set explicitly. Functions use APICredentials
model to manage them
"""
from typing import Iterable, Union, List
from urllib.parse import urlencode

import requests
from requests.utils import parse_header_links

from insights.meetup.api_models import APIGroupMember, APIGroup, APICategory
from insights.meetup.models import APICredentials

DEFAULT_PAGE_SIZE = 2000


def categories(page_size=DEFAULT_PAGE_SIZE) -> Iterable[APICategory]:
    """
    Get the list of group categories
    """
    return iter_api_v2(
        'https://api.meetup.com/2/categories',
        page_size=page_size,
        wrap=APICategory.from_dict)


def find_groups(category: Union[int, List[int]] = None,
                country: str = None,
                lat: int = None,
                lon: int = None,
                location: str = None,
                page_size=DEFAULT_PAGE_SIZE) -> Iterable[APIGroup]:
    """
    Find groups, filtering them by given characteristics (mainly location and
    optionally a category)
    """
    params = {'fallback_suggestions': 0, 'self_groups': 'include'}
    if category:
        if isinstance(category, list):
            category = ','.join(str(c) for c in category)
        params['category'] = category
    if country:
        params['country'] = country
    if lat:
        params['lat'] = lat
    if lon:
        params['lon'] = lon
    if location:
        params['location'] = location
    return iter_api_v3(
        'https://api.meetup.com/find/groups',
        params,
        page_size=page_size,
        wrap=APIGroup.from_dict)


def group_members(urlname: str,
                  page_size=DEFAULT_PAGE_SIZE) -> Iterable[APIGroupMember]:
    """
    Take the group urlname (for example, "pyporto") and return an iterator
    with current information on all members of the meetup.com community.

    Returned objects are JSON-encoded representations of users from meetup.com
    API: https://www.meetup.com/meetup_api/docs/:urlname/members/
    """
    endpoint = f'https://api.meetup.com/{urlname}/members'
    fields = [
        'messaging_pref',
        'privacy',
    ]
    return iter_api_v3(
        endpoint, {'fields': ','.join(fields)},
        page_size=page_size,
        wrap=APIGroupMember.from_dict)


def iter_api_v3(endpoint, params=None, page_size=DEFAULT_PAGE_SIZE, wrap=None):
    """
    Helper function to iterate over API results (v3 version of the API)
    """
    effective_params = urlencode(dict(params or {}, page=page_size))
    url = f'{endpoint}?{effective_params}'
    while True:
        token = APICredentials.get_access_token()
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        json_resp = resp.json()
        for result in json_resp:
            if wrap:
                result = wrap(result)
            yield result

        # No "Link" to iterate
        if 'Link' not in resp.headers:
            break

        # Parse link and see if there's a "next" element
        links = parse_header_links(resp.headers['Link'])
        for link in links:
            if link.get('rel') == 'next':
                url = link['url']
                break
        else:
            break


def iter_api_v2(endpoint, params=None, page_size=DEFAULT_PAGE_SIZE, wrap=None):
    """
    Helper function to iterate over API results (v2 version of the API)
    """
    effective_params = urlencode(dict(params or {}, page=page_size))
    url = f'{endpoint}?{effective_params}'
    while True:
        token = APICredentials.get_access_token()
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        json_resp = resp.json()
        for result in json_resp['results']:
            if wrap:
                result = wrap(result)
            yield result

        url = json_resp['meta'].get('next')
        if not url:
            break
