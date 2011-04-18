# -*- coding: utf-8 -*-

import datetime
import logging
import os

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
    permission_required,)
from django.core.cache import cache
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db import connection
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods

from teagarden import decorators, models


PAGINATION_DEFAULT_LIMIT = 50


def _clean_int(value, default, min_value=None, max_value=None):
    """Helper to cast value to int and to clip it to min or max_value.

    Args:
      value: Any value (preferably something that can be casted to int).
      default: Default value to be used when type casting fails.
      min_value: Minimum allowed value (default: None).
      max_value: Maximum allowed value (default: None).

    Returns:
      An integer between min_value and max_value.
    """
    if not isinstance(value, (int, long)):
        try:
            value = int(value)
        except (TypeError, ValueError), err:
            value = default
    if min_value is not None:
        value = max(min_value, value)
    if max_value is not None:
        value = min(value, max_value)
    return value


def respond(request, template, params=None):
    """Helper to render a response, passing standard stuff to the response.

    :param request: The request object.
    :param template: The template name; '.html' is appended automatically.
    :param params: A dict giving the template parameters; modified in-place.
    :returns: Whatever render_to_response(template, params) returns.
    :raises: Whatever render_to_response(template, params) raises.
    """
    if params is None:
        params = {}
    must_choose_nickname = False
    if request.user is not None:
        account = models.Account.current_user_account
        #must_choose_nickname = not account.user_has_selected_nickname()
    #full_path = request.get_full_path().encode("utf-8")
    #if request.user is None:
        #params['sign_in'] = users.create_login_url(full_path)
    #else:
        #params['sign_out'] = users.create_logout_url(full_path)
    #params['must_choose_nickname'] = must_choose_nickname
    #params['uploadpy_hint'] = uploadpy_hint
    try:
        return render_to_response(template, params,
                                  context_instance=RequestContext(request))
    #except DeadlineExceededError:
        #logging.exception('DeadlineExceededError')
        #return HttpResponse('DeadlineExceededError', status=503)
    #except CapabilityDisabledError, err:
        #logging.exception('CapabilityDisabledError: %s', err)
        #return HttpResponse('Rietveld: App Engine is undergoing maintenance. '
                            #'Please try again in a while. ' + str(err),
                            #status=503)
    except MemoryError:
        logging.exception("MemoryError")
        return HttpResponse("MemoryError", status=503)
    except AssertionError:
        logging.exception("AssertionError")
        return HttpResponse("AssertionError")


def _make_comment(request, obj, message, draft):
    cmt = models.Comment(content_object=obj)
    cmt.is_draft = draft
    cmt.text = message
    cmt.set_timestamps(request.user)
    return cmt


class CommentForm(forms.Form):

    message = forms.CharField(required=False, max_length=2000,
                              label=_(u"Message"),
                              widget=forms.Textarea(attrs={"cols": 60}))


@login_required
def dashboard(request):
    today = datetime.date.today()
    query = models.Comment.objects.select_related().order_by('-created')
    comments_today = query.filter(created__gte=today)
    comments_last_week = query.filter(
        created__lt=today,
        created__gte=today - datetime.timedelta(days=7))
    comments_last_month = query.filter(
        created__lt=today - datetime.timedelta(days=7),
        created__gte=today - datetime.timedelta(days=30))
    return respond(request, 'latest_comments.html', {
        'comments_today': comments_today,
        'comments_last_week': comments_last_week,
        'comments_last_month': comments_last_month})


@login_required
def index(request):
    return dashboard(request)


class TableListForm(forms.Form):

    group = forms.ChoiceField(
        label=_(u"Group"),
        widget=forms.Select(attrs={"onchange": "JS_setGroup(this.value);"}))

    def set_group_choices(self, project):
        choices = []
        bound_field = self["group"]
        choices.append([0, _(u"Show all")])
        groups = models.Group.objects.all()
        groups = groups.filter(Q(tablegroup__table__project=project.id))
        groups = groups.distinct()
        groups.order_by("name")
        for group in groups:
            choices.append([group.id, group.name])
        bound_field.field.choices = choices


class UserProfileForm(forms.Form):

    first_name = forms.CharField(label=_(u"First name"), max_length=30,
                                 required=False)
    last_name = forms.CharField(label=_(u"Last name"), max_length=30,
                                required=False)
    email = forms.EmailField(label=_(u"E-mail"), required=True)


@login_required
@decorators.table_required
def discard_table_comment(request, cmt_id):
    q = models.TableComment.objects.filter(id=int(cmt_id))
    if q.count() == 0:
        raise HttpResponseNotFound("No comment exists with that id (%s)" %
                                   cmt_id)
    cmt = q[0]
    cmt.delete()
    return HttpResponseRedirect("/table/%s" % cmt.table.id)


def _edit_settings(request):
    user = request.user
    if request.method != "POST":
        form = UserProfileForm(initial={
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email})
        return respond(request, "settings.html", {
            "form": form})
    form = UserProfileForm(request.POST)
    if form.is_valid():
        #messages.success(request, _(u"Your profile has been sucessfully updated."))
        user.first_name = form.cleaned_data["first_name"]
        user.last_name = form.cleaned_data["last_name"]
        user.email = form.cleaned_data["email"]
        user.save()
        messages.error(request, _(u"Failure"))
        return HttpResponseRedirect("/dashboard")
    else:
        return respond(request, "settings.html", {"form": form})


@login_required
def edit_settings(request):
    return _edit_settings(request)


@decorators.comment_owner_required
def discard_comment(request):
    cmt = request.comment
    cmt.delete()
    return HttpResponseRedirect(cmt.content_object.get_absolute_url())
    #return HttpResponseRedirect(reverse("teagarden.views.dashboard"))


@decorators.comment_owner_required
def publish_comment(request):
    """Publish a comment."""
    cmt = request.comment
    cmt.is_draft = False
    cmt.set_timestamps(request.user)
    cmt.save()
    return HttpResponseRedirect(cmt.content_object.get_absolute_url())
    #return HttpResponseRedirect(reverse("teagarden.views.dashboard"))


@login_required
@decorators.table_required
def publish_table_comment(request):
    """Publish all field comments and write a table comment."""
    form = CommentForm()
    if request.method == "POST":
        if "cancel" in request.POST:
            return HttpResponseRedirect(reverse("teagarden.views.table",
                args=[request.table.id]))
        form = CommentForm(request.POST)
        if form.is_valid():
            cmt = _make_comment(request, request.table,
                                form.cleaned_data['message'], False)
            cmt.save()
            return HttpResponseRedirect(reverse("teagarden.views.table",
                args=[request.table.id]))
    return respond(request, "publish.html", {"table": request.table,
        "form": form})


@login_required
@decorators.field_required
def publish_field_comment(request):
    """Create a new field comment."""
    form = CommentForm()
    if request.method == "POST":
        if "cancel" in request.POST:
            return HttpResponseRedirect(reverse("teagarden.views.field",
                args=[request.field.id]))
        form = CommentForm(request.POST)
        if form.is_valid():
            cmt = _make_comment(request, request.field,
                                form.cleaned_data['message'], False)
            cmt.save()
            return HttpResponseRedirect(reverse("teagarden.views.field",
                args=[request.field.id]))
    return respond(request, 'publish.html', {'field': request.field,
        'form': form})


@require_http_methods(['POST'])
@login_required
@decorators.table_required
def create_comment(request):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if not form.is_valid():
            pass
        cmt = _make_comment(request, request.table,
                            form.cleaned_data["message"], False)
        cmt.save()
        return HttpResponseRedirect(reverse("teagarden.views.table",
            args=[request.table.id]))


@login_required
@decorators.project_required
def project(request):
    # TODO: Join Comments/drafts to speed up the select
    group_id = _clean_int(request.GET.get("group"), 0, 0)
    type_id = _clean_int(request.GET.get("type"), 0, 0)
    tables = models.Table.objects.select_related()
    if group_id:
        tables = tables.filter(Q(tablegroup__group=group_id))
        #tables = models.Group.objects.all()
        #tables = tables.filter(Q(tablegroup__table__project=project.id))
        tables = tables.distinct()
        #tables.order_by("name")
    else:
        #tables = models.Table.objects.select_related()
        tables = tables.filter(project=request.project.id)
        #tables = tables.order_by("name")
        #tables = tables.filter(Q())
    if type_id:
        tables = tables.filter(type=type_id)
    tables.order_by("name")
    form = TableListForm(initial={"group": group_id})
    form.set_group_choices(request.project)

    types = models.TableType.objects.all()
    types = types.order_by("name")

    return respond(request, "project.html", {
        "form": form,
        "project": request.project,
        "tables": tables,
        "types": types})


@login_required
def projects(request):
    projects = models.Project.objects.all()
    projects = projects.order_by("name")
    return respond(request, "projects.html", {"projects": projects})


def _show_user(request):
    num_tables = models.Table.objects.filter(
        created_by=request.user_to_show).count()
    num_fields = models.Field.objects.filter(
        created_by=request.user_to_show).count()
    num_comments = models.Comment.objects.filter(
        created_by=request.user_to_show).count()
    return respond(request, "user.html", {'user_to_show': request.user_to_show,
                                          'num_tables': num_tables,
                                          'num_fields': num_fields,
                                          'num_comments': num_comments})


@login_required
@decorators.user_key_required
def show_user(request):
    """Displays the user profile."""
    return _show_user(request)


@login_required
def starred_objects(request):
    starred_tables = models.Table.get_starred(request.user).select_related()
    starred_fields = models.Field.get_starred(request.user).select_related()
    return respond(request, "starred_objects.html", {
        "starred_tables": starred_tables,
        "starred_fields": starred_fields})


@login_required
@decorators.table_required
def table(request):
    #fields = models.Field.objects.filter(table=request.table.id)
    #fields = fields.order_by("position")
    fields = models.Field.objects.select_related()
    #fields = fields.filter(Q(fieldcomment__field__table=request.table))
    fields = fields.filter(table=request.table.id).order_by("position")
    # fields = fields.aggregate(Count())
    comments = []
    draft_count = 0
    for cmt in request.table.get_comments():
        if (not cmt.is_draft
            or (cmt.is_draft and cmt.created_by == request.user)):
            comments.append(cmt)
        if cmt.is_draft and cmt.created_by == request.user:
            draft_count += 1
    references = models.Table.objects.all()
    # fields = related name
    references = references.filter(Q(fields__foreign__table=request.table.id))
    references = references.distinct()
    references = references.order_by("name")
    return respond(request, "table.html", {
        "comments": comments,
        "comment_count": len(comments) - draft_count,
        "draft_count": draft_count,
        "fields": fields,
        "references": references,
        "table": request.table})


def _user_popup(request):
    user = request.user_to_show
    popup_html = cache.get("user_popup:%d" % user.id)
    if popup_html is None:
        logging.debug("Missing cache entry for user_popup:%d", user.id)
        popup_html = render_to_response("user_popup.html", {"user": user})
        cache.set("user_popup:%d" % user.id, popup_html, 60)
    return popup_html


@decorators.user_key_required
def user_popup(request):
    """Pop up to show the user info."""
    try:
        return _user_popup(request)
    except Exception, err:
        logging.exception('Exception in user_popup processing:')
        # Return HttpResponse because the JS part expects a 200 status code.
        return HttpResponse('<font color="red">Error: %s; please report!</font>' %
                            err.__class__.__name__)


@login_required
@decorators.table_required
def star_table(request):
    request.table.add_star(request.user)
    return respond(request, 'table_star.html', {'table': request.table})


@login_required
@decorators.table_required
def unstar_table(request):
    request.table.remove_star(request.user)
    return respond(request, 'table_star.html', {'table': request.table})


@login_required
@decorators.field_required
def star_field(request):
    request.field.add_star(request.user)
    return respond(request, 'field_star.html', {'field': request.field})


@login_required
@decorators.field_required
def unstar_field(request):
    request.field.remove_star(request.user)
    return respond(request, 'field_star.html', {'field': request.field})


@login_required
@decorators.field_required
def field(request):
    """Displays the details and comments of a field."""
    return respond(request, 'field.html', {'field': request.field})

