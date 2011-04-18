# -*- coding: utf-8 -*-

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

import models


class CommentFeed(Feed):
    title = _(u'Current comments feed')
    link = '/rss/comments'
    description = 'Comments feed'

    def item_author_name(self, item):
        return item.created_by

    def items(self):
        return models.Comment.objects.order_by('-created')[:10]

    def item_link(self, item):
        return item.content_object.get_absolute_url()

    def item_pubdate(self, item):
        return item.created

    def item_title(self, item):
        return _(u'Comment on \'%s\'') % item.content_object

    def item_description(self, item):
        return item.text

    def item_author_link(self, obj):
        return reverse('teagarden.views.show_user', args=[obj.created_by_id])

    def item_author_email(self, obj):
        return obj.created_by.email

    def title(self):
        return _(u'Teagaden comments feed')
