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
        
        parties = ["None","Committed to Ashburton - NZ","Working for Community Putting People First","Committed to Community","Ban 1080 Political Party","STOP","Positive Change for CHB","Change For The Better","Stand up for Dunedin","Green Dunedin","The People's Choice","Community Voice .nz","The People's Choice - Independent","United Future","Awake at the Wheel","Awanui Progressive and Ratepayers Inc.","Haititai Marangai Marae","Doubtless Bay Promotions Inc.","Whatuwhiwhi Ratepayers & Citizens Assn.","Community First Kaikohe Hokianga","Green Party","Labour","Team Fred Allen","Love Hamilton","No Water Meters","Community Voice","Leading the way for Central Hawke's Bay","Independent Maori","The Man with a Plan","Healthy Hutt","Rate Restraint","ANZASW-Taranaki Branch","100% Pure Taranaki","Better Health Group","Mana Movement","Ngai Tai Torere","A Fresh Voice","A New Partnership","Team God","Refresh Tasman","Refreshing Council for positive change","On the Job","Friendship House","Raglan Residents & Ratepayers","Green Party of Aotearoa New Zealand","Rates Control Team","Whanganui Beyond 2030","Totally Independent","Keep the Progress Up","Go-Whangarei","TogetherTahi","Tu Kotahi","Independent - Tohunga - Maori Researcher","Te Ropu Awangawanga - CONCERN","Rotorua District Residents and Ratepayers","A Practical Man","Elect for Professional Governance","A Common Sense Solution For Rotorua","Community Works","Vote Webber Vote Better","Vote Rotorua Lakes Community","Independent Rural","Your Local Rural Advocate","Best for Christchurch","Economic Euthenics","Keep Our Assets Canterbury","Best Value for Christchurch","The Right Choice for Papanui & Christchurch","Papanui First","Independent Citizens","The People's Choice - Labour","Eastborn","Connected Communities, Thriving Christchurch","Independent - Let's Get It Done","Strong Communities for a Stronger Christchurch","True Independent","Our Community My Priority","Your Fresh Voice for Riccarton","Best for Riccarton","For Communities You'll Love To Live In","The Busbug Bus Users Group","TLC Set Us Free","Caring for our community","Safe Turangi","Vibrant, clean & safe Feilding Initiative","More Democracy Less Bureaucracy","Energy and Experience","Community Focused Leadership","Experienced Positive Leadership","Together we can build a better city","Effectiveness, Efficiency, Growth","Real Change in TCC - Guaranteed","Looking After Locals","Delivering for the Mount and Papamoa","Re-elect for Effective Governance","For progress - with prudent financial managment","I Am Listening","The Voice of Common Sense","A New Perspective","Have your say, For your City","The people The place The future","Committed to Tauranga","Independent - Keeping it real","Smart Thinking Beyond Elections","Re-elect For Sound Financial Management","PICK RICK - Let's Get Real","Real Change in TCC - It starts here","A friend you can trust","Building Our Community. Valuing People","Fighting for the Ratepayers","Working for Growth and Development","Our Families, Our Future","Working for Masterton","Caring about our community","A better return to the community","Working for the Wairarapa","Your Voice On The Trust","Working for us","Forward Together","Representing Napiers Youth","Money Free Party New Zealand","A Strong Voice for Nelson","Caring Communities & A Vibrant City","Leading Nelson Forward","Grow Porirua, not the Council","Our City, Our Home, Our Future","Make Porirua great again","Independent Socialist","New Zealand Labour Party","The Localisation Party","Freeze rates and cut waste","Local Champion for Your Northern Suburbs","A fresh voice for change and affordable rates","A more responsive Council","The Independent Choice","Connecting Communities","Red/Green Independent","Hold us to Account","To be added","Independent","Communist League","STOP","Auckland Legalise Cannabis","Christians Against Abortion","Greater Auckland","Auckland Future","Putting People First","City Vision","C&R - Communities & Residents","Team Franklin","Labour","Green Party","Respect Our Community Campaign","Manurewa-Papakura Action Team","Taking the Shore Forward","Shore Action","A Positive Voice for the Shore","United Future","Community Voice","Independent - West at Heart","Labour - Future West","WestWards","Shadbolt's Independent","Community First","Affiliation","Team George Wood","Community Before Council","People over Politics","People and Penlink First","Positively Penlink","Vision & Voice - Botany","Practical Not Political","Ratepayers and Residents","Vision & Voice - Howick","Vision & Voice - Pakuranga","Kaipātiki Voice","Manurewa Action Team","It's Worth It Manurewa","Maungakiekie Community Voices","Otara Independents","Papatoetoe Independents","Papakura First","Papakura Action Team","Roskill Community Voice","Community Independent","Rodney First","Wellsford Sport Collective","Future West","Community Central","Whau Local Independents"]
        
        for theparty in parties:
        
            party_set, created = PartySet.objects.get_or_create(
                slug="localbodyparties",
                name="Local Body Parties"
            )
            try:
                organization_extra = OrganizationExtra.objects.get(
                    slug = slugify(theparty)
                )
                organization = organization_extra.base
            except OrganizationExtra.DoesNotExist:
                organization = Organization.objects.create(
                    name = theparty,
                    classification = "Party"
                )
                organization_extra = OrganizationExtra.objects.create(
                    base = organization,
                    slug = slugify(theparty)
                )
                organization.party_sets.add(party_set)