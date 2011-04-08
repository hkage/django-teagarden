# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns(
    '',
    (r'^%s' % settings.BASE_URL, include('teagarden.urls')),
)
