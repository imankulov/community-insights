# community-insights

Community insights from meetup.com

## Project initialization (locally)

Create a new API client on meetup.com. The starting point for creating
a client is https://secure.meetup.com/meetup_api/oauth_consumers/.

Use "http://127.0.0.1:8000/meetup/start/" is the value for the "Website"
parameter and "http://127.0.0.1:8000/meetup/callback/" for "Redirect URI".

Configure boto3 to make sure you have access to S3 bucket without providing
requisites in the code. See [boto3 configuration guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html)
for details.

Create a new S3 bucket to store snapshots for groups and their members

Run a local Postgres server, you can start it using docker-compose.yml with 

```bash
docker-compose up -d postgres
```
 
Copy `env.sample` to `.env` and adjust it accordingly, but setting the name for
S3 bucket, meetup API client credentials and database URL if needed

Run the app. Docker endpoint takes care of everything, from database migration,
to creating superuser, to collecting or updating static.

```bash
docker-compose up --build app
```

Obtain access and refresh token from the meetup.com by visiting the
page http://127.0.0.1:8000/meetup/start/. The final message
"meetup.com credentials stored" means that everything went successfully.

Enter the Docker container to perform firtthe

Import meetup categories from the API

```bash
docker-compose exec app ./manage.py sync_categories
```

Go to project admin console to create locations you want to keep track of.
Each location consists of the country code (for example, "PT" for Portugal)
and full name for location (for example, "Porto, Portugal" for the Porto city
or "Lisboa, Portugal" for Lisbon):

http://127.0.0.1:8000/admin/meetup/meetuplocation/

In the same admin console create group filters (pairs of location + topic to
keep track of):

http://127.0.0.1:8000/admin/meetup/meetupgroupfilter/

For example, to keep track of all tech groups in Porto, choose "Tech (34)" and
"Porto, Portugal" and create a new object. You can create as many filters as
you want.

Alternatively, you can load sample locations and group filters for all tech
events in Portugal with

```bash
docker-compose exec app ./manage.py loaddata locations_portugal
```

Get back to the console to load the list of groups.

```bash
docker-compose exec app ./manage.py sync_groups
```

You should be able to see the list of your groups in
the Admin panel http://127.0.0.1:8000/admin/meetup/meetupgroup/ and in the 
S3 bucket.

Then sync group members. It will take a while

```bash
docker-compose exec app ./manage.py sync_group_members
```

## Updating the project

Run periodically (once a day)

```bash
docker-compose exec app ./manage.py sync_groups
```

Run periodically (once in 1-2 hours)

```bash
docker-compose exec app ./manage.py sync_group_members
```

Group members updated every 24 hours.


## Exploring the data with Jupyter Notebooks

You can use Django models from Jupyter Notebook if you properly configure
the environment

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insights.settings')
django.setup()
```

It's quite easy to export data from Django querset to Pandas dataframe using
`DataFrame.from_records`

```python
import pandas as pd
from meetup.models import *
groups = pd.DataFrame.from_records(MeetupGroup.objects.all().values())
```
