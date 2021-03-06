# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-23 15:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('share', '0043_auto_20160830_2102'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
                DROP TRIGGER IF EXISTS share_link_change ON share_link;

                UPDATE share_link SET url = 'http://dx.doi.org/' || share_link.url WHERE share_link.url LIKE '10.%' AND share_link.type = 'doi';
                UPDATE share_link SET url = replace(upper(share_link.url), 'HTTP://DX.DOI.ORG/', 'http://dx.doi.org/')  WHERE share_link.type = 'doi';

                CREATE TRIGGER share_link_change
                BEFORE INSERT OR UPDATE ON share_link
                FOR EACH ROW
                EXECUTE PROCEDURE before_share_link_change();
            '''),
    ]
