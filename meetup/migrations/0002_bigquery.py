from django.db import migrations
from django.conf import settings
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

client = bigquery.Client()


def create_groups_table(apps, schema_editor):
    dataset_ref = client.dataset(settings.BIGQUERY_DATASET_ID)
    # Only define fields that are required and not strings (because
    # non-required strings will be populated automatically)
    schema = [
        bigquery.SchemaField('date', 'DATE', mode='REQUIRED'),
        bigquery.SchemaField('id', 'INT64', mode='REQUIRED'),
        bigquery.SchemaField('urlname', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('created', 'TIMESTAMP'),
        bigquery.SchemaField('lat', 'FLOAT64'),
        bigquery.SchemaField('lon', 'FLOAT64'),
        bigquery.SchemaField('members', 'INT64'),
        bigquery.SchemaField('organizer_id', 'INT64'),
        bigquery.SchemaField('next_event_yes_rsvp_count', 'INT64'),
        bigquery.SchemaField('next_event_time', 'TIMESTAMP'),
        bigquery.SchemaField('category_id', 'INT64'),
        bigquery.SchemaField('meta_category_id', 'INT64'),
    ]
    table_ref = dataset_ref.table('groups')
    table = bigquery.Table(table_ref, schema=schema)

    # define partitioning by date
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY, field='date')

    # define clustering by urlname
    table.clustering_fields = ['urlname']

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

    # Only define fields that are required and not strings (because
    # non-required strings will be populated automatically)
    schema = [
        bigquery.SchemaField('date', 'DATE', mode='REQUIRED'),
        bigquery.SchemaField('id', 'INT64', mode='REQUIRED'),
        bigquery.SchemaField('joined', 'TIMESTAMP'),
        bigquery.SchemaField('lat', 'FLOAT64'),
        bigquery.SchemaField('lon', 'FLOAT64'),
        bigquery.SchemaField('group_id', 'INT64', mode='REQUIRED'),
        bigquery.SchemaField('group_urlname', 'STRING', mode='REQUIRED'),
        bigquery.SchemaField('is_pro_admin', 'BOOL'),
    ]
    table_ref = dataset_ref.table('members')
    table = bigquery.Table(table_ref, schema=schema)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY, field='date')

    # define partitioning by date
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY, field='date')

    # define clustering by group urlname
    table.clustering_fields = ['group_urlname']

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
