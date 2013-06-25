# -*- coding: utf-8 -*-

"""Middleware classes."""

from django.db.models.signals import pre_save


class UpdateDefaultFieldsMiddleware(object):
    """Middleware to populate the timestamp fields."""

    def process_request(self, request):
        if request.user.is_authenticated():
            user_id = '%s (ID: %s)' % (request.user.username, request.user.id)
        else:
            user_id = None
        def update_default_fields(*args, **kwds):
            instance = kwds['instance']
            if hasattr(instance, 'created_by') and not instance.pk:
                instance.cruser = user_id
            if hasattr(instance, 'modified_by'):
                instance.upduser = user_id
        # store dispatch_uid as request attribute
        request._auto_current_user_uid = id(update_pux_default_fields)
        # connect callback to pre_save signal
        pre_save.connect(update_pux_default_fields, weak=False,
                         dispatch_uid=request._auto_current_user_uid)

    def _disconnect_callback(self, request):
        """Removes callback attached in process_request."""
        dispatch_uid = getattr(request, '_auto_current_user_uid', None)
        if dispatch_uid is not None:
            pre_save.disconnect(dispatch_uid=dispatch_uid)

    def process_response(self, request, response):
        """Removes callback attached in process_request."""
        self._disconnect_callback(request)
        return response

    def process_exception(self, request, exception):
        """Removes callback attached in process_request."""
        # exception unused, pylint: disable=W0613
        self._disconnect_callback(request)
