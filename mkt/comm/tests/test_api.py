from django.core.urlresolvers import reverse

from nose.tools import eq_
from test_utils import RequestFactory

from amo.tests import addon_factory
from comm.models import (CommunicationNote, CommunicationThread,
                         CommunicationThreadCC)
from mkt.api.tests.test_oauth import RestOAuth
from mkt.comm.api import ThreadPermission
from mkt.site.fixtures import fixture
from mkt.webapps.models import Webapp


class TestThreadDetail(RestOAuth):
    fixtures = fixture('webapp_337141', 'user_2519')

    def setUp(self):
        super(TestThreadDetail, self).setUp()
        self.addon = Webapp.objects.get(pk=337141)

    def check_permissions(self):
        req = RequestFactory().get(reverse('comm-thread-detail',
                                           kwargs={'pk': self.thread.pk}))
        req.user = self.user
        req.amo_user = self.profile
        req.groups = req.amo_user.groups.all()

        return ThreadPermission().has_object_permission(
            req, 'comm-thread-detail', self.thread)

    def test_response(self):
        thread = CommunicationThread.objects.create(addon=self.addon)
        CommunicationNote.objects.create(thread=thread,
            author=self.profile, note_type=0, body='something')
        res = self.client.get(reverse('comm-thread-detail',
                                      kwargs={'pk': thread.pk}))
        eq_(res.status_code, 200)
        eq_(len(res.json['notes']), 1)

    def test_cc(self):
        self.thread = CommunicationThread.objects.create(addon=self.addon)
        # Test with no CC.
        assert not self.check_permissions()

        # Test with CC created.
        CommunicationThreadCC.objects.create(thread=self.thread,
            user=self.profile)
        assert self.check_permissions()

    def test_addon_dev_allowed(self):
        self.thread = CommunicationThread.objects.create(addon=self.addon,
            read_permission_developer=True)
        self.addon.addonuser_set.create(user=self.profile)
        assert self.check_permissions()

    def test_addon_dev_denied(self):
        # Test when the user is a developer of a different add-on.
        self.thread = CommunicationThread.objects.create(addon=self.addon,
            read_permission_developer=True)
        addon = addon_factory()
        self.profile.addonuser_set.create(addon=addon)
        assert not self.check_permissions()

    def test_read_public(self):
        self.thread = CommunicationThread.objects.create(addon=self.addon,
            read_permission_public=True)
        assert self.check_permissions()

    def test_read_moz_contact(self):
        thread = CommunicationThread.objects.create(addon=self.addon,
            read_permission_mozilla_contact=True)
        thread.addon.mozilla_contact = self.user.email
        thread.addon.save()
        self.thread = thread
        assert self.check_permissions()

    def test_read_reviewer(self):
        self.grant_permission(self.profile, 'Apps:Review')
        self.thread = CommunicationThread.objects.create(addon=self.addon,
            read_permission_reviewer=True)
        assert self.check_permissions()

    def test_read_senior_reviewer(self):
        self.grant_permission(self.profile, 'Apps:ReviewEscalated')
        self.thread = CommunicationThread.objects.create(addon=self.addon,
            read_permission_senior_reviewer=True)
        assert self.check_permissions()

    def test_read_staff(self):
        self.grant_permission(self.profile, 'Admin:%')
        self.thread = CommunicationThread.objects.create(addon=self.addon,
            read_permission_staff=True)
        assert self.check_permissions()


class TestThreadList(RestOAuth):
    fixtures = fixture('webapp_337141', 'user_2519')

    def setUp(self):
        super(TestThreadList, self).setUp()
        self.addon = Webapp.objects.get(pk=337141)
        self.list_url = reverse('comm-thread-list')

    def test_response(self):
        """Test the list response, we don't want public threads in
        the list."""
        CommunicationThread.objects.create(addon=self.addon,
            read_permission_public=True)
        thread = CommunicationThread.objects.create(addon=self.addon)
        CommunicationNote.objects.create(author=self.profile, thread=thread,
            note_type=0)
        res = self.client.get(self.list_url)
        eq_(res.status_code, 200)
        eq_(len(res.json['objects']), 1)

    def test_addon_filter(self):
        thread = CommunicationThread.objects.create(addon=self.addon)
        CommunicationNote.objects.create(author=self.profile, thread=thread,
            note_type=0, body='something')

        res = self.client.get(self.list_url, {'app': '337141'})
        eq_(res.status_code, 200)
        eq_(len(res.json['objects']), 1)

        # This add-on doesn't exist.
        res = self.client.get(self.list_url, {'app': '1000'})
        eq_(res.status_code, 404)


class TestNote(RestOAuth):
    fixtures = fixture('webapp_337141', 'user_2519')

    def setUp(self):
        super(TestNote, self).setUp()
        addon = Webapp.objects.get(pk=337141)
        self.thread = CommunicationThread.objects.create(addon=addon)

    def test_response(self):
        note = CommunicationNote.objects.create(author=self.profile,
            thread=self.thread, note_type=0, body='something')
        res = self.client.get(reverse('comm-note-detail',
                                      kwargs={'pk': note.id}))
        eq_(res.status_code, 200)
        eq_(res.json['body'], 'something')
