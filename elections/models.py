from __future__ import unicode_literals

from collections import defaultdict
from datetime import date

from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from popolo.models import Organization

from compat import python_2_unicode_compatible


class ElectionQuerySet(models.QuerySet):
    def current(self, current=True):
        return self.filter(current=current)

    def get_by_slug(self, election):
        return get_object_or_404(self, slug=election)

    def by_date(self):
        return self.order_by(
            'election_date'
        )

class ElectionManager(models.Manager):
    def elections_for_area_generations(self):
        generations = defaultdict(list)
        for election in self.current():
            for area_type in election.area_types.all():
                area_tuple = (area_type.name, election.area_generation)
                generations[area_tuple].append(election)

        return generations

    def are_upcoming_elections(self):
        today = date.today()
        return self.current().filter(election_date__gte=today).exists()


# FIXME: shouldn't AreaType also have the MapIt generation?
# FIXME: at the moment name is a code (like WMC); ideally that would
# be a code field and the name field would be "Westminster Consituency"
@python_2_unicode_compatible
class AreaType(models.Model):
    name = models.CharField(max_length=128)
    source = models.CharField(max_length=128, blank=True,
                              help_text=_("e.g MapIt"))

    def __str__(self):
        return self.name

    def area_choices(self):
        return self.areas.all() \
            .order_by('base__name') \
            .values_list('id', 'base__name')


@python_2_unicode_compatible
class Election(models.Model):
    slug = models.CharField(max_length=128, unique=True)
    for_post_role = models.CharField(max_length=128)
    winner_membership_role = \
        models.CharField(max_length=128, null=True, blank=True)
    candidate_membership_role = models.CharField(max_length=128)
    election_date = models.DateField()
    name = models.CharField(max_length=128)
    current = models.BooleanField()
    use_for_candidate_suggestions = models.BooleanField(default=False)
    area_types = models.ManyToManyField(AreaType, blank=True)
    area_generation = models.CharField(max_length=128, blank=True)
    organization = models.ForeignKey(Organization, null=True, blank=True)
    party_lists_in_use = models.BooleanField(default=False)
    people_elected_per_post = models.IntegerField(
        default=1,
        help_text=_("The number of people who are elected to this post in the "
                    "election.  -1 means a variable number of winners")
    )
    default_party_list_members_to_show = models.IntegerField(default=0)
    show_official_documents = models.BooleanField(default=False)
    ocd_division = models.CharField(max_length=250, blank=True)

    description = models.CharField(max_length=500, blank=True)

    objects = ElectionManager.from_queryset(ElectionQuerySet)()

    def __str__(self):
        return self.name

    @classmethod
    def group_and_order_elections(cls, include_posts=False):
        """Group elections in a helpful order

        We should order and group elections in the following way:

          Group by current=True, then current=False
            Group by for_post_role (ordered alphabetically)
              Order election by election date (new to old) then election name

        If the parameter include_posts is set to True, then the posts
        will be included as well.

        e.g. An example of the returned data structure:

        [
          {
            'current': True,
            'roles': [
              {
                'role': 'Member of Parliament',
                'elections': [
                  {
                    'election': <Election: 2015 General Election>,
                    'posts': [
                      <PostExtra: Member of Parliament for Aberavon>,
                      <PostExtra: Member of Parliament for Aberconwy>,
                      ...
                    ]
                  }
                ]
              },
              {
                'role': 'Member of the Scottish Parliament',
                'elections': [
                  {
                    'election': <Election: 2016 Scottish Parliament Election (Regions)>,
                     'posts': [
                       <PostExtra: Member of the Scottish Parliament for Central Scotland>,
                       <PostExtra: Member of the Scottish Parliament for Glasgow>,
                       ...
                     ]
                  },
                  {
                    'election': <Election: 2016 Scottish Parliament Election (Constituencies)>,
                    'posts': [
                      <PostExtra: Member of the Scottish Parliament for Aberdeen Central>,
                      <PostExtra: Member of the Scottish Parliament for Aberdeen Donside>,
                      ...
                    ]
                  }
                ]
              }
            ]
          },
          {
            'current': False,
            'roles': [
              {
                'role': 'Member of Parliament',
                'elections': [
                  {
                    'election': <Election: 2010 General Election>,
                    'posts': [
                      <PostExtra: Member of Parliament for Aberavon>,
                      <PostExtra: Member of Parliament for Aberconwy>,
                      ...
                    ]
                  }
                ]
              }
            ]
          },
        ]

        """
        from candidates.models import PostExtra
        result = [
            {'current': True, 'roles': []},
            {'current': False, 'roles': []},
        ]
        role = None
        qs = cls.objects.order_by(
            '-current', 'for_post_role', '-election_date', 'name'
        )
        # If we've been asked to include posts as well, add a prefetch
        # to the queryset:
        if include_posts:
            qs = qs.prefetch_related(
                models.Prefetch(
                    'posts',
                    PostExtra.objects.select_related('base') \
                        .order_by('base__label'),
                )
            )
        # The elections and posts are already sorted into the right
        # order, but now need to be grouped into the useful
        # data structure described in the docstring.
        last_current = None
        for election in qs:
            current_index = 1 - int(election.current)
            roles = result[current_index]['roles']
            # If the role has changed, or we've switched from current
            # elections to past elections, create a new array of
            # elections to append to:
            if (role is None) or role['role'] != election.for_post_role or \
               (last_current is not None and last_current != election.current):
                role = {
                    'role': election.for_post_role,
                    'elections': []
                }
                roles.append(role)
            d = {
                'election': election
            }
            if include_posts:
                d['posts'] = list(election.posts.all())
            role['elections'].append(d)
            last_current = election.current
        return result
