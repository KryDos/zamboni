import hashlib

from django import http
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import etag

import commonware.log
import jingo
from session_csrf import anonymous_csrf_exempt
from tower import ugettext as _

import amo
from abuse.models import send_abuse_report
from access import acl
from addons.decorators import addon_view_factory
from amo.decorators import login_required, permission_required
from amo.utils import paginate
from devhub.models import ActivityLog
from reviews.models import GroupedRating, Review
from reviews.views import get_flags

from mkt.site import messages
from mkt.site.forms import AbuseForm
from mkt.webapps.models import Webapp

log = commonware.log.getLogger('z.detail')

addon_view = addon_view_factory(qs=Webapp.objects.valid)
addon_all_view = addon_view_factory(qs=Webapp.objects.all)


@addon_all_view
def detail(request, addon, add_review=False):
    """Product details page."""
    reviews = Review.objects.valid().filter(addon=addon, is_latest=True)
    # Mature regions show only reviews from within that region.
    if not request.REGION.adolescent:
        reviews = reviews.filter(client_data__region=request.REGION.id)
    reviewed_filter = dict(user=request.user.id)
    if addon.is_packaged:
        reviewed_filter['version'] = addon.current_version
    num_reviews = 6 if request.TABLET or not request.MOBILE else 2
    user_review = reviews.filter(**reviewed_filter)
    ctx = {
        'product': addon,
        'reviews': reviews[:num_reviews],
        'flags': get_flags(request, reviews),
        'has_review': request.user.is_authenticated() and
                      user_review.exists(),
        'grouped_ratings': GroupedRating.get(addon.id),
        'details_page': True,
        'add_review': add_review,
    }
    if ctx['has_review']:
        ctx['my_review'] = user_review[0]
    if addon.is_public():
        ctx['abuse_form'] = AbuseForm(request=request)
    return jingo.render(request, 'detail/app.html', ctx)


def manifest(request, uuid):
    """Returns the "mini" manifest for packaged apps.

    If not a packaged app, returns a 404.

    """
    addon = get_object_or_404(Webapp, guid=uuid, is_packaged=True)
    is_avail = addon.status in [amo.STATUS_PUBLIC, amo.STATUS_BLOCKED]
    package_etag = hashlib.sha256()

    if not addon.is_packaged or addon.disabled_by_user or not is_avail:
        raise http.Http404

    else:
        manifest_content = addon.get_cached_manifest()
        package_etag.update(manifest_content)

        if addon.is_packaged:
            # Update the hash with the content of the package itself.
            package_file = addon.get_latest_file()
            if package_file:
                package_etag.update(package_file.hash)

    manifest_etag = package_etag.hexdigest()

    @etag(lambda r, a: manifest_etag)
    def _inner_view(request, addon):
        response = http.HttpResponse(
            manifest_content,
            content_type='application/x-web-app-manifest+json; charset=utf-8')
        return response

    return _inner_view(request, addon)


@addon_all_view
def privacy(request, addon):
    is_dev = request.check_ownership(addon, require_owner=False,
                                     ignore_disabled=True)
    if not (addon.is_public() or acl.check_reviewer(request) or is_dev):
        raise http.Http404
    if not addon.privacy_policy:
        return http.HttpResponseRedirect(addon.get_url_path())
    return jingo.render(request, 'detail/privacy.html', {'product': addon})


@anonymous_csrf_exempt
@addon_view
def abuse(request, addon):
    form = AbuseForm(request.POST or None, request=request)
    if request.method == 'POST' and form.is_valid():
        send_abuse_report(request, addon, form.cleaned_data['text'])
        messages.success(request, _('Abuse reported.'))
        return redirect(addon.get_url_path())
    else:
        return jingo.render(request, 'detail/abuse.html',
                            {'product': addon, 'abuse_form': form})


@login_required
@permission_required('AccountLookup', 'View')
@addon_all_view
def app_activity(request, addon):
    """Shows the app activity age for single app."""

    user_items = ActivityLog.objects.for_apps([addon]).exclude(
        action__in=amo.LOG_HIDE_DEVELOPER)
    admin_items = ActivityLog.objects.for_apps([addon]).filter(
        action__in=amo.LOG_HIDE_DEVELOPER)

    user_items = paginate(request, user_items, per_page=20)
    admin_items = paginate(request, admin_items, per_page=20)

    return jingo.render(request, 'detail/app_activity.html',
                        {'admin_items': admin_items,
                         'product': addon,
                         'user_items': user_items})
