from __future__ import unicode_literals
 
from datetime import date 

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify
from django.utils.translation import ugettext as _
from django.utils.six.moves.urllib_parse import urljoin, urlsplit
from django.utils.six import text_type

import requests

from popolo.models import Post, Area, Organization
from candidates.models import PostExtra, AreaExtra, PartySet, PostExtraElection, OrganizationExtra
from elections.models import Election, AreaType


class Command(BaseCommand):

    def handle(self, *args, **options):
        
        remotejsonurl = "https://psopho.co.nz/ynr/posts.json"
        
        defaults = {
            'organization_classification': 'Council',
            'election_date': date(2016, 10, 8),
            'current': True,
            'candidate_membership_role': 'Candidate',
            'area_generation': '7'
        }
        
        areaclassification = {
            'O04': 'OSM Administrative Boundary Level 4',
            'O06': 'OSM Administrative Boundary Level 6'
        }
        
        party_set, created = PartySet.objects.get_or_create(
            slug="localbodyparties",
            name="Local Body Parties"
        )
        try:
            organization_extra = OrganizationExtra.objects.get(
                slug = "independent"
            )
            organization = organization_extra.base
        except OrganizationExtra.DoesNotExist:
            organization = Organization.objects.create(
                name = "Independent",
                classification = "Party"
            )
            organization_extra = OrganizationExtra.objects.create(
                base = organization,
                slug = "independent"
            )
            organization.party_sets.add(party_set)
        
        r = requests.get(remotejsonurl)
        if r.status_code == 404:
            raise CommandError("JSON wasn't found")
        
        for electiondata in r.json():
          
            # organisation
            try:
                organization_extra = OrganizationExtra.objects.get(
                    slug = slugify(electiondata['organization_name'])
                )
                organization = organization_extra.base
            except OrganizationExtra.DoesNotExist:
                organization = Organization.objects.create(
                    name = electiondata['organization_name'],
                    classification = defaults['organization_classification']
                )
                organization_extra = OrganizationExtra.objects.create(
                    base = organization,
                    slug = slugify(electiondata['organization_name'])
                )
              
            # election
            election, created = Election.objects.update_or_create(
                slug = slugify(electiondata['election_name']),
                for_post_role = electiondata['for_post_role'],
                candidate_membership_role = defaults['candidate_membership_role'],
                election_date = defaults['election_date'],
                name = electiondata['election_name'],
                current = defaults['current'],
                organization = organization,
                party_lists_in_use = False,
                area_generation = defaults['area_generation']
            )
            area_type, _ = AreaType.objects.update_or_create(
                name = electiondata['mapit_code'], defaults={'source': 'MapIt'}
            )
            if not election.area_types.filter(name=area_type.name).exists():
                election.area_types.add(area_type)
          
            # area
            area, area_created = Area.objects.get_or_create(
                name = electiondata['mapit_area_name'],
                identifier = electiondata['mapit_area_id'],
                classification = areaclassification[electiondata['mapit_code']]
            )
            
            # areatype
            area_type, created = AreaType.objects.get_or_create(
                name = electiondata['mapit_code'],
                source = 'MapIt'
            )
            
            # areaextra
            if area_created:
                area_extra, area_extra_created = AreaExtra.objects.get_or_create(
                    base = area
                )
            if area_created and area_extra_created:
                area_extra.type = area_type
                area_extra.save()
          
          
            for electionpost in electiondata['posts']:
                
                # post
                post, created = Post.objects.get_or_create(
                    label = electionpost['label'],
                    area = area,
                    organization = organization
                )
                
                # postextra
                post_slug = electiondata['mapit_area_id'] + slugify(electionpost['label'])
                post_extra, created = PostExtra.objects.get_or_create(
                    base = post,
                    slug = post_slug,
                    party_set = party_set
                )
                
                # postextraelection
                PostExtraElection.objects.get_or_create(
                    postextra = post_extra,
                    election = election,
                    winner_count = electionpost['positions']
                )