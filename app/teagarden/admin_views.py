# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

import models


def set_project(request):
    project_id = request.POST.get("project")
    last_page = request.POST.get("last_page")
    try:
        project_id = int(project_id)
    except (ValueError, TypeError):
        project_id = 0
    request.session["project"] = project_id
    if project_id:
        project = get_object_or_404(models.Project, id=project_id)
        messages.success(request, _("Filter for project '%s' applied.") % project)
    if last_page:
        return HttpResponseRedirect(last_page)
    else:
        return HttpResponseRedirect(reverse("admin:index"))
