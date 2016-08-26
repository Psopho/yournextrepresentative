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
    
    areas = [
      ["364729","364729 Chatham Islands","O04","Chatham Islands"],
      ["793703","793703 Wellington","O04","Wellington"],
      ["793704","793704 Manawatu-Wanganui","O04","Manawatu-Wanganui"],
      ["793705","793705 West Coast","O04","West Coast"],
      ["793706","793706 Canterbury","O04","Canterbury"],
      ["793707","793707 Otago","O04","Otago"],
      ["793708","793708 Southland","O04","Southland"],
      ["793710","793710 Hawke's Bay","O04","Hawke's Bay"],
      ["793711","793711 Taranaki","O04","Taranaki"],
      ["793841","793841 Bay of Plenty","O04","Bay of Plenty"],
      ["794054","794054 Auckland","O04","Auckland"],
      ["794055","794055 Waikato","O04","Waikato"],
      ["794070","794070 Northland","O04","Northland"],
      ["794411","794411 Gisborne","O04","Gisborne"],
      ["795121","795121 Nelson","O04","Nelson"],
      ["795122","795122 Marlborough","O04","Marlborough"],
      ["795123","795123 Tasman","O04","Tasman"],
      ["801008","801008 Christchurch City","O06","Christchurch City"],
      ["801122","801122 Invercargill City","O06","Invercargill City"],
      ["801123","801123 Westland District","O06","Westland District"],
      ["803381","803381 Ashburton District","O06","Ashburton District"],
      ["803901","803901 Hamilton City","O06","Hamilton City"],
      ["804078","804078 Thames Coromandel District","O06","Thames Coromandel District"],
      ["804079","804079 Hauraki District","O06","Hauraki District"],
      ["804297","804297 Napier City","O06","Napier City"],
      ["805980","805980 Palmerston North City","O06","Palmerston North City"],
      ["806050","806050 Manawatu District","O06","Manawatu District"],
      ["807844","807844 Wellington City","O06","Wellington City"],
      ["807845","807845 Porirua City","O06","Porirua City"],
      ["807846","807846 Lower Hutt City","O06","Lower Hutt City"],
      ["807847","807847 Upper Hutt City","O06","Upper Hutt City"],
      ["807848","807848 Kapiti Coast District","O06","Kapiti Coast District"],
      ["807849","807849 Horowhenua District","O06","Horowhenua District"],
      ["807850","807850 Waipa District","O06","Waipa District"],
      ["807851","807851 Matamata Piako District","O06","Matamata Piako District"],
      ["807852","807852 Kawerau District","O06","Kawerau District"],
      ["807853","807853 Whakatane District","O06","Whakatane District"],
      ["807854","807854 South Waikato District","O06","South Waikato District"],
      ["807855","807855 South Wairarapa District","O06","South Wairarapa District"],
      ["807856","807856 Carterton District","O06","Carterton District"],
      ["807857","807857 Rotorua District","O06","Rotorua District"],
      ["807858","807858 Western Bay of Plenty District","O06","Western Bay of Plenty District"],
      ["807859","807859 Tauranga City","O06","Tauranga City"],
      ["807860","807860 Taupo District","O06","Taupo District"],
      ["807861","807861 Gore District","O06","Gore District"],
      ["807864","807864 Ruapehu District","O06","Ruapehu District"],
      ["807880","807880 Masterton District","O06","Masterton District"],
      ["807881","807881 Tararua District","O06","Tararua District"],
      ["807882","807882 Central Hawke's Bay District","O06","Central Hawke's Bay District"],
      ["807883","807883 Rangitikei District","O06","Rangitikei District"],
      ["807910","807910 Waimakariri District","O06","Waimakariri District"],
      ["807915","807915 Hastings District","O06","Hastings District"],
      ["807916","807916 Selwyn District","O06","Selwyn District"],
      ["807918","807918 Wanganui District","O06","Wanganui District"],
      ["807919","807919 South Taranaki District","O06","South Taranaki District"],
      ["807921","807921 New Plymouth District","O06","New Plymouth District"],
      ["807922","807922 Stratford District","O06","Stratford District"],
      ["807923","807923 Waitomo District","O06","Waitomo District"],
      ["807924","807924 Opotiki District","O06","Opotiki District"],
      ["807925","807925 Wairoa District","O06","Wairoa District"],
      ["807926","807926 Otorohanga District","O06","Otorohanga District"],
      ["807936","807936 Timaru District","O06","Timaru District"],
      ["807937","807937 Mackenzie District","O06","Mackenzie District"],
      ["807941","807941 Waimate District","O06","Waimate District"],
      ["807942","807942 Kaikoura District","O06","Kaikoura District"],
      ["807946","807946 Waitaki District","O06","Waitaki District"],
      ["807971","807971 Dunedin City","O06","Dunedin City"],
      ["807972","807972 Central Otago District","O06","Central Otago District"],
      ["807975","807975 Clutha District","O06","Clutha District"],
      ["807976","807976 Queenstown-Lakes District","O06","Queenstown-Lakes District"],
      ["807977","807977 Hurunui District","O06","Hurunui District"],
      ["808019","808019 Waikato District","O06","Waikato District"],
      ["808021","808021 Kaipara District","O06","Kaipara District"],
      ["808025","808025 Grey District","O06","Grey District"],
      ["808026","808026 Buller District","O06","Buller District"],
      ["808027","808027 Whangarei District","O06","Whangarei District"],
      ["808586","808586 Far North District","O06","Far North District"],
      ["808605","808605 Southland District","O06","Southland District"]
      ]
      
    areaclassification = {
        'O04': 'OSM Administrative Boundary Level 4',
        'O06': 'OSM Administrative Boundary Level 6'
    }
    
    for thearea in areas:
      
      # area
      area, area_created = Area.objects.get_or_create(
        name=thearea[3],
        identifier=thearea[0],
        classification=areaclassification[thearea[2]]
      )
      
      # areatype
      area_type, created = AreaType.objects.get_or_create(
        name=thearea[2],
        source='MapIt'
      )
      
      # areaextra
      if area_created:
        area_extra, area_extra_created = AreaExtra.objects.get_or_create(
          base=area,
          type=area_type
        )
