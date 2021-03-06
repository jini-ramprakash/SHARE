# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-29 17:56
from __future__ import unicode_literals

import hashlib

from django.db import migrations


SOURCES_TABLES = (
    'share_extradataversion_sources',
    'share_extradata_sources',
    'share_venueversion_sources',
    'share_venue_sources',
    'share_awardversion_sources',
    'share_award_sources',
    'share_tagversion_sources',
    'share_tag_sources',
    'share_linkversion_sources',
    'share_link_sources',
    'share_throughlinksversion_sources',
    'share_throughlinks_sources',
    'share_throughvenuesversion_sources',
    'share_throughvenues_sources',
    'share_throughawardsversion_sources',
    'share_throughawards_sources',
    'share_throughtagsversion_sources',
    'share_throughtags_sources',
    'share_throughawardentitiesversion_sources',
    'share_throughawardentities_sources',
    'share_throughsubjectsversion_sources',
    'share_throughsubjects_sources',
    'share_emailversion_sources',
    'share_email_sources',
    'share_identifierversion_sources',
    'share_identifier_sources',
    'share_personversion_sources',
    'share_person_sources',
    'share_throughidentifiersversion_sources',
    'share_throughidentifiers_sources',
    'share_personemailversion_sources',
    'share_personemail_sources',
    'share_affiliationversion_sources',
    'share_affiliation_sources',
    'share_contributorversion_sources',
    'share_contributor_sources',
    'share_entityversion_sources',
    'share_entity_sources',
    'share_abstractcreativeworkversion_sources',
    'share_abstractcreativework_sources',
    'share_associationversion_sources',
    'share_association_sources'
)


def ReplaceUsers(to_user, *from_users):
    sql = ''
    targets = '({})'.format(', '.join("'providers.{}'".format(x) for x in from_users))

    for table in SOURCES_TABLES:
        column = table.split('_')[1]+ '_id'
        # Add back in when travis gets postgres 9.5+
        # IN (SELECT id FROM share_shareuser WHERE robot IN {targets}) ON CONFLICT DO NOTHING;
        sql += '''
            INSERT INTO
                {table} ({column},  shareuser_id)
            SELECT
                {column}, (SELECT id FROM share_shareuser WHERE robot='providers.{to_user}')
            FROM
                {table} WHERE shareuser_id
            IN (SELECT id FROM share_shareuser WHERE robot IN {targets});

            DELETE FROM
                {table}
            WHERE
                shareuser_id
            IN (SELECT id FROM share_shareuser WHERE robot IN {targets});
        '''.format(**locals())

    for table, column in (('share_celerytask', 'provider_id'), ('share_celerytask', 'started_by_id'), ('share_rawdata', 'source_id'), ('share_normalizeddata', 'source_id')):
        sql += '''
        UPDATE
            {table}
        SET
            {column} = (SELECT id FROM share_shareuser WHERE robot = 'providers.{to_user}')
        WHERE
            {column} IN (SELECT id FROM share_shareuser WHERE robot IN {targets});
        '''.format(**locals())

    sql += '''
    DELETE FROM oauth2_provider_accesstoken WHERE user_id IN (SELECT id FROM share_shareuser WHERE robot IN {targets});
    '''.format(**locals())

    return migrations.RunSQL(sql, '')


class Migration(migrations.Migration):

    dependencies = [
        ('share', '0045_auto_20160927_1436'),
    ]

    operations = [
        ReplaceUsers('io.osf', 'io.osf.preprints', 'io.osf.registrations'),
        migrations.RunSQL([('DELETE FROM share_shareuser WHERE robot = %s', ('providers.io.osf.preprints', ))], ''),
        migrations.RunSQL([('DELETE FROM share_shareuser WHERE robot = %s', ('providers.io.osf.registrations', ))], ''),
    ]
