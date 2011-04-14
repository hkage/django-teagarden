# -*- coding: utf-8 -*-

import os

from django.conf import settings
import django.template

import models


counter = 0

IS_DEV = 'TEAGARDEN_DEBUG' in os.environ.keys()


def library(request):
    """Method to add the applications library to the builtins.

    :param request: A request instance
    :returns: A parameter dictionary
    """
    _library_name = __name__.rsplit('.', 1)[0] + '.library'
    if not django.template.libraries.get(_library_name, None):
        django.template.add_to_builtins(_library_name)
    global counter
    counter += 1
    params = {}
    if request.user is not None:
        account = models.Account.current_user_account
    params["request"] = request
    params["user"] = request.user
    params["account"] = account
    params["counter"] = counter
    params["is_dev"] = IS_DEV
    params["BASE_URL"] = settings.BASE_URL
    if request.session.get("project", 0):
        params["selected_project"] = request.session["project"]
    # Support a list of all projects foer the global admin filter
    if "/admin/" in request.path:
        query = models.Project.objects.all().order_by("name")
        params["projects"] = query
    return params
