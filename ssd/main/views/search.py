#
# Copyright 2013 - Tom Alessi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Views for the SSD Project that pertain to search functionality only

"""


import datetime
import pytz
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.utils import timezone as jtz
from ssd.main.models import Event
from ssd.main.forms import SearchForm
from ssd.main.forms import IGSearchForm
from ssd.main import config_value



def igsearch(request):
    """Incident Search View (Graph)

    Show incidents for a specific date, when clicked through from the summary graph

    """

    form = IGSearchForm(request.GET)

    if form.is_valid():
        # Obtain the cleaned data (only validate the dates)
        date = form.cleaned_data['date']

        # Give the date a timezone so search is accurate
        # If the timezone is not set, give the local server timezone
        if request.COOKIES.get('timezone') == None:
            set_timezone = settings.TIME_ZONE
        else:
            set_timezone = request.COOKIES.get('timezone')

        # Combine the dates and times into datetime objects
        start = datetime.datetime.combine(date, datetime.datetime.strptime('00:00:00','%H:%M:%S').time())
        end = datetime.datetime.combine(date, datetime.datetime.strptime('23:59:59','%H:%M:%S').time())

        # Set the timezone
        tz = pytz.timezone(set_timezone)
        start = tz.localize(start)
        end = tz.localize(end)

        results = Event.objects.filter(incident__date__range=[start,end]
                                              ).values('incident__date',
                                                       'incident_id',
                                                       'incident__closed',
                                                       'incident__detail'
                                                      ).distinct().order_by('-incident__date')

        # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
        jtz.activate(set_timezone)

        # Print the page
        return render_to_response(
           'search/isearch_results.html',
           {
              'title':'System Status Dashboard | Incident Search',
              'results':results
           },
           context_instance=RequestContext(request)
        )
    
    # Invalid form
    else:
        return HttpResponseRedirect('/') 


