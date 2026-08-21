import os
import re
from unittest.mock import MagicMock, patch

from asyncio import iscoroutine

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Parser import Parser
from gdo.base.Render import Mode
from gdo.core.GDO_Session import GDO_Session
from gdo.core.GDT_Password import GDT_Password
from gdo.core.GDT_JSON import GDT_JSON
from gdo.hydra_server.GDO_HydraMonitor import GDO_HydraMonitor
from gdo.hydra_server.GDO_HydraHistory import GDO_HydraHistory
from gdo.hydra_server.method.monitor_cronjob import monitor_cronjob
from gdo.date.Time import Time
from gdo.mail.GDT_Emails import GDT_Emails
from gdotest.TestUtil import GDOTestCase, cli_gizmore, cli_top, reinstall_module


class HydraTest(GDOTestCase):

    def test_00_emails_accepts_csv_and_rejects_invalid_addresses(self):
        emails = GDT_Emails('emails')
        self.assertTrue(emails.validate('a@example.test, b@example.test'))
        self.assertFalse(emails.validate('a@example.test, not-an-email'))

    def test_00_json_stores_port_documents_in_a_native_json_column(self):
        ports = GDT_JSON('ports')
        value = [{'port': 443, 'encryption': 'tls', 'special_flag': 'https'}]
        self.assertTrue(ports.validate(ports.to_val(value)))
        self.assertEqual(value, ports.to_value(ports.to_val(value)))
        self.assertEqual('ports JSON', ports.gdo_column_define())

    def setUp(self):
        super().setUp()
        Application.init(os.path.dirname(__file__ + '/../../../../'))
        loader = ModuleLoader.instance()
        reinstall_module('hydra_server')
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        Application.init_cli()
        loader.init_cli()

    @patch('gdo.hydra_server.method.acquire.Mail.from_bot')
    def test_01_acquire_stores_a_token_and_password_hash(self, from_bot):
        mail = MagicMock()
        from_bot.return_value = mail
        user = cli_gizmore()
        method = Parser(Mode.render_cli, user, user.get_server(), None,
                        GDO_Session.for_user(user)).parse('hydra_server.acquire mogwai mira@example.test')
        result = method.execute()
        while iscoroutine(result):
            result = Application.LOOP.run_until_complete(result)
        output = cli_top(Mode.render_cli)
        match = re.search(r'Monitor ([0-9a-f]{16}) created\. Save this password now; it will not be shown again: ([0-9a-f]{32})', output)
        self.assertIsNotNone(match, output)
        monitor = GDO_HydraMonitor.table().get_by_id(match.group(1))
        self.assertEqual('mogwai', monitor.gdo_val('hm_name'))
        self.assertEqual(match.group(1), monitor.gdo_val('hm_token'))
        self.assertEqual('mira@example.test', monitor.gdo_val('hm_emails'))
        self.assertTrue(GDT_Password.check(monitor.gdo_val('hm_password_hash'), match.group(2)))
        self.assertEqual(1, mail.recipient.call_count)
        self.assertIn(match.group(1), mail.body.call_args.args[0])
        self.assertIn(match.group(2), mail.body.call_args.args[0])
        self.assertIn('/hydra.ping.json', mail.body.call_args.args[0])

        session = GDO_Session.for_user(user)
        method = Parser(Mode.render_cli, user, user.get_server(), None, session).parse(
            f'hydra.token {match.group(1)} {match.group(2)}')
        result = method.execute()
        while iscoroutine(result):
            result = Application.LOOP.run_until_complete(result)
        self.assertEqual(match.group(1), session.get('hydra_monitor_token'))

    def test_02_monitor_cronjob_updates_monitor_and_history(self):
        token = '0123456789abcdef'
        password = 'test-monitor-password'
        GDO_HydraMonitor.blank({
            'hm_token': token,
            'hm_name': 'mogwai',
            'hm_password_hash': GDT_Password.hash(password),
        }).insert()
        user = cli_gizmore()
        method = Parser(Mode.render_cli, user, user.get_server(), None,
                        GDO_Session.for_user(user)).parse(
            f'hydra.ping {token} {password} 12.5 100 200 300 400 50')
        result = method.execute()
        while iscoroutine(result):
            result = Application.LOOP.run_until_complete(result)

        monitor = GDO_HydraMonitor.table().get_by_id(token)
        self.assertEqual(12.5, monitor.gdo_value('hm_curr_cpu'))
        self.assertEqual(300, monitor.gdo_value('hm_curr_hdd'))
        self.assertEqual(400, monitor.gdo_value('hm_max_hdd'))
        self.assertIsNotNone(monitor.gdo_val('hm_last_signal'))
        history = GDO_HydraHistory.table().select().where('hh_monitor', token).first().exec().fetch_object()
        self.assertIsNotNone(history)
        self.assertEqual(50, history.gdo_value('hh_project_used'))

        session = GDO_Session.for_user(user).set('hydra_monitor_token', token).save()
        method = Parser(Mode.render_cli, user, user.get_server(), None, session).parse('hydra_server.edit')
        page = method.execute()
        while iscoroutine(page):
            page = Application.LOOP.run_until_complete(page)
        self.assertIn('mogwai', page.render(Mode.render_cli))

    @patch('gdo.hydra_server.method.monitor_cronjob.Mail.from_bot')
    def test_03_monitor_cronjob_mails_a_down_monitor_once(self, from_bot):
        mail = MagicMock()
        from_bot.return_value = mail
        monitor = GDO_HydraMonitor.blank({
            'hm_token': 'fedcba9876543210',
            'hm_name': 'mogwai',
            'hm_password_hash': GDT_Password.hash('test-monitor-password'),
            'hm_emails': 'ops@example.test, mira@example.test',
            'hm_last_signal': Time.get_date(Application.TIME - 301),
        }).insert()

        monitor_cronjob().gdo_execute()
        self.assertEqual(2, mail.recipient.call_count)
        self.assertTrue(monitor.gdo_val('hm_down_notified'))

        monitor_cronjob().gdo_execute()
        self.assertEqual(2, mail.recipient.call_count)
