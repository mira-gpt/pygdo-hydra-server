from gdo.base.GDT import GDT
from gdo.base.Application import Application
from gdo.base.Method import Method
from gdo.base.Util import Random
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_Password import GDT_Password
from gdo.core.GDT_Token import GDT_Token
from gdo.hydra_server.GDO_HydraMonitor import GDO_HydraMonitor
from gdo.mail.GDT_Emails import GDT_Emails
from gdo.mail.Mail import Mail


class acquire(Method):
    """Create one random token/password monitor and reveal both exactly once."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_in_channels(self) -> bool:
        return False

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Name('name').initial('my-monitor').not_null().positional(),
            GDT_Emails('emails').not_null().positional(),
        ]

    def gdo_execute(self) -> GDT:
        token = GDT_Token.random()
        password = Random.token(16)
        monitor = GDO_HydraMonitor.blank({
            'hm_name': self.param_value('name'),
            'hm_token': token,
            'hm_password_hash': GDT_Password.hash(password),
            'hm_emails': self.param_value('emails'),
        }).insert()
        self.send_credentials(monitor, password)
        return self.msg('msg_hydra_monitor_acquired', (monitor.get_id(), password))

    @staticmethod
    def send_credentials(monitor: GDO_HydraMonitor, password: str) -> None:
        url = f"https://{Application.config('core.domain')}/hydra.ping.json"
        mail = Mail.from_bot()
        for email in monitor.gdo_val('hm_emails').split(','):
            mail.recipient(email.strip())
        mail.subject(f"Hydra monitor credentials: {monitor.gdo_val('hm_name')}")
        mail.body(
            f"Your Hydra monitor is ready.<br><br>"
            f"URL: <a href=\"{url}\">{url}</a><br>"
            f"Token: <code>{monitor.get_id()}</code><br>"
            f"Password: <code>{password}</code><br><br>"
            f"Keep the password private; it cannot be displayed again.")
        mail.send()
