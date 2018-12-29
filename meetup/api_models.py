import attr

from meetup.api_utils import dpath_get, dpath_get_datetime


@attr.s
class APIObject(object):
    @classmethod
    def from_dict(cls, obj):
        ret = {}
        for field in attr.fields(cls):
            if not field.init:
                continue
            dict_getter = field.metadata.get('dict_getter')
            if dict_getter is None:
                dict_getter = dpath_get(f'/{field.name}')
            value = dict_getter(obj, field)
            ret[field.name] = value
        return cls(**ret)


@attr.s
class APICategory(APIObject):
    id = attr.ib()
    shortname = attr.ib()
    name = attr.ib()


@attr.s
class APIGroup(APIObject):
    id = attr.ib()
    name = attr.ib()
    status = attr.ib()
    urlname = attr.ib()
    description = attr.ib(repr=False)
    created = attr.ib(metadata={'dict_getter': dpath_get_datetime('/created')})
    city = attr.ib()
    untranslated_city = attr.ib()
    country = attr.ib()
    state = attr.ib()
    join_mode = attr.ib()
    visibility = attr.ib()
    lat = attr.ib()
    lon = attr.ib()
    members = attr.ib()
    who = attr.ib()
    organizer_id = attr.ib(
        metadata={'dict_getter': dpath_get('/organizer/id')})
    organizer_name = attr.ib(
        metadata={'dict_getter': dpath_get('/organizer/name')})
    timezone = attr.ib()
    next_event_id = attr.ib(
        metadata={'dict_getter': dpath_get('/next_event/id')})
    next_event_name = attr.ib(
        metadata={'dict_getter': dpath_get('/next_event/name')})
    next_event_yes_rsvp_count = attr.ib(
        metadata={'dict_getter': dpath_get('/next_event/yes_rsvp_count')})
    next_event_time = attr.ib(
        metadata={'dict_getter': dpath_get_datetime('/next_event/time')})
    category_id = attr.ib(metadata={'dict_getter': dpath_get('/category/id')})
    category_shortname = attr.ib(
        metadata={'dict_getter': dpath_get('/category/shortname')})
    meta_category_id = attr.ib(
        metadata={'dict_getter': dpath_get('/meta_category/id')})
    meta_category_shortname = attr.ib(
        metadata={'dict_getter': dpath_get('/meta_category/shortname')})


@attr.s
class APIGroupMember(APIObject):
    id = attr.ib()
    name = attr.ib()
    status = attr.ib()
    joined = attr.ib(metadata={'dict_getter': dpath_get_datetime('/joined')})
    city = attr.ib()
    country = attr.ib()
    lat = attr.ib()
    lon = attr.ib()
    group_status = attr.ib(
        metadata={'dict_getter': dpath_get('/group_profile/status')})
    group_visited = attr.ib(
        metadata={'dict_getter': dpath_get_datetime('/group_profile/visited')})
    group_created = attr.ib(
        metadata={'dict_getter': dpath_get_datetime('/group_profile/created')})
    group_updated = attr.ib(
        metadata={'dict_getter': dpath_get_datetime('/group_profile/updated')})
    group_role = attr.ib(
        metadata={'dict_getter': dpath_get('/group_profile/role')})
    group_id = attr.ib(
        metadata={'dict_getter': dpath_get('/group_profile/group/id')})
    group_urlname = attr.ib(
        metadata={'dict_getter': dpath_get('/group_profile/group/urlname')})
    group_link = attr.ib(
        metadata={'dict_getter': dpath_get('/group_profile/link')})
    is_pro_admin = attr.ib()
    messaging_pref = attr.ib()
    privacy_bio = attr.ib(metadata={'dict_getter': dpath_get('/privacy/bio')})
    privacy_groups = attr.ib(
        metadata={'dict_getter': dpath_get('/privacy/groups')})
    privacy_topics = attr.ib(
        metadata={'dict_getter': dpath_get('/privacy/topics')})
