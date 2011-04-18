# -*- coding: utf-8 -*-

"""Custom decorators"""

import logging
import urllib

from django.contrib.auth.decorators import (
    login_required,)
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseRedirect,
    HttpResponseForbidden)
from django.shortcuts import get_object_or_404

from teagarden import models


def field_required(func):
    def field_wrapper(request, field_id, *args, **kwds):
        request.field = get_object_or_404(models.Field, id=field_id)
        return func(request, *args, **kwds)
    return field_wrapper


def project_required(func):
    def project_wrapper(request, project_id, *args, **kwds):
        request.project = get_object_or_404(models.Project, id=project_id)
        return func(request, *args, **kwds)
    return project_wrapper


def table_required(func):
    def table_wrapper(request, table_id, *args, **kwds):
        request.table = get_object_or_404(models.Table, id=table_id)
        return func(request, *args, **kwds)
    return table_wrapper


def user_key_required(func):
    """Decorator that processes the user handler argument."""

    def user_key_wrapper(request, user_key, *args, **kwds):
        user_key = urllib.unquote(user_key)
        if "@" in user_key:
            request.user_to_show = models.Account.objects.filter(
                email=user_key)[0]
        else:
            users = models.Account.objects.filter(id=user_key)
            if not users:
                logging.info("Account not found for nickname %s" % user_key)
                return HttpResponseNotFound('No user found with that key (%s)' %
                                            user_key)
            request.user_to_show = users[0]
        return func(request, *args, **kwds)
    return user_key_wrapper


def comment_required(func):
    """Decorator that processes the booking_id handler argument."""
    def comment_wrapper(request, comment_id, *args, **kwds):
        request.comment = get_object_or_404(models.Comment, id=comment_id)
        return func(request, *args, **kwds)
    return comment_wrapper


def comment_owner_required(func):
    """Decorator that processes the booking_id argument and insists you own it."""
    @login_required
    @comment_required
    def comment_owner_wrapper(request, *args, **kwds):
        if request.comment.created_by != request.user:
            return HttpResponseForbidden('You do not own this comment')
        return func(request, *args, **kwds)
    return comment_owner_wrapper
