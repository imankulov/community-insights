from django.db import migrations
from django.conf import settings
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

client = bigquery.Client()


def create_groups_table(apps, schema_editor):
    dataset_ref = client.dataset(settings.BIGQUERY_DATASET_ID)
    schema = [
        bigquery.SchemaField('date', 'DATE', mode='REQUIRED'),
        bigquery.SchemaField('id', 'INT64', mode='REQUIRED'),
        bigquery.SchemaField('name', 'STRING'),
        bigquery.SchemaField('status', 'STRING'),
        bigquery.SchemaField('urlname', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('description', 'STRING'),
        bigquery.SchemaField('created', 'DATETIME'),
        bigquery.SchemaField('city', 'STRING'),
        bigquery.SchemaField('untranslated_city', 'STRING'),
        bigquery.SchemaField('country', 'STRING'),
        bigquery.SchemaField('state', 'STRING'),
        bigquery.SchemaField('join_mode', 'STRING'),
        bigquery.SchemaField('visibility', 'STRING'),
        bigquery.SchemaField('lat', 'FLOAT64'),
        bigquery.SchemaField('lon', 'FLOAT64'),
        bigquery.SchemaField('members', 'INT64'),
        bigquery.SchemaField('who', 'STRING'),
        bigquery.SchemaField('organizer_id', 'INT64'),
        bigquery.SchemaField('organizer_name', 'STRING'),
        bigquery.SchemaField('timezone', 'STRING'),
        bigquery.SchemaField('next_event_id', 'STRING'),
        bigquery.SchemaField('next_event_name', 'STRING'),
        bigquery.SchemaField('next_event_yes_rsvp_count', 'INT64'),
        bigquery.SchemaField('next_event_time', 'DATETIME'),
        bigquery.SchemaField('category_id', 'INT64'),
        bigquery.SchemaField('category_shortname', 'STRING'),
        bigquery.SchemaField('meta_category_id', 'INT64'),
        bigquery.SchemaField('meta_category_shortname', 'STRING'),
    ]
    table_ref = dataset_ref.table('groups')
    table = bigquery.Table(table_ref, schema=schema)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY, field='date')

    client.create_table(table)


def delete_groups_table(apps, schema_editor):
    dataset_ref = client.dataset(settings.BIGQUERY_DATASET_ID)
    table_ref = dataset_ref.table('groups')
    try:
        client.delete_table(table_ref)
    except NotFound:
        pass


def create_members_table(apps, schema_editor):
    dataset_ref = client.dataset(settings.BIGQUERY_DATASET_ID)
    schema = [
        bigquery.SchemaField('date', 'DATE', mode='REQUIRED'),
        bigquery.SchemaField('id', 'INT64', mode='REQUIRED'),
        bigquery.SchemaField('name', 'STRING'),
        bigquery.SchemaField('status', 'STRING'),
        bigquery.SchemaField('joined', 'DATETIME'),
        bigquery.SchemaField('city', 'STRING'),
        bigquery.SchemaField('country', 'STRING'),
        bigquery.SchemaField('lat', 'FLOAT64'),
        bigquery.SchemaField('lon', 'FLOAT64'),
        bigquery.SchemaField('group_status', 'STRING'),
        bigquery.SchemaField('group_visited', 'STRING'),
        bigquery.SchemaField('group_created', 'STRING'),
        bigquery.SchemaField('group_updated', 'STRING'),
        bigquery.SchemaField('group_role', 'STRING'),
        bigquery.SchemaField('group_id', 'INT64', mode='REQUIRED'),
        bigquery.SchemaField('group_urlname', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('group_link', 'STRING'),
        bigquery.SchemaField('is_pro_admin', 'BOOL'),
        bigquery.SchemaField('messaging_pref', 'STRING'),
        bigquery.SchemaField('privacy_bio', 'STRING'),
        bigquery.SchemaField('privacy_groups', 'STRING'),
        bigquery.SchemaField('privacy_topics', 'STRING'),
    ]
    table_ref = dataset_ref.table('members')
    table = bigquery.Table(table_ref, schema=schema)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY, field='date')

    client.create_table(table)


def delete_members_table(apps, schema_editor):
    dataset_ref = client.dataset(settings.BIGQUERY_DATASET_ID)
    table_ref = dataset_ref.table('members')
    try:
        client.delete_table(table_ref)
    except NotFound:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('meetup', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_groups_table, delete_groups_table),
        migrations.RunPython(create_members_table, delete_members_table),
    ]
