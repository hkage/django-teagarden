# -*- coding: utf-8 -*-

"""View definitions."""

from django.views.generic import TemplateView


class IndexView(TemplateView):

    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return self.render_to_response(context)
