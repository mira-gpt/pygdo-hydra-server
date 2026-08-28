from gdo.base.GDT import GDT
from gdo.core.MethodCronjob import MethodCronjob
from gdo.date.Time import Time
from gdo.hydra_server.GDO_HydraMonitor import GDO_HydraMonitor
from gdo.hydra_server.module_hydra_server import module_hydra_server
from gdo.mail.Mail import Mail


class cronjob(MethodCronjob):
    """Alert monitor contacts once when a monitor stops reporting."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_execute(self) -> GDT:
        threshold = module_hydra_server.instance().cfg_monitor_down_after()
        notified = 0
        for monitor in GDO_HydraMonitor.table().select().exec().fetch_all():
            if not monitor.gdo_val('hm_emails') or monitor.gdo_val('hm_down_notified'):
                continue
            last_signal = monitor.column('hm_last_signal')
            elapsed = last_signal.get_elapsed() if last_signal.get_val() else monitor.column('hm_created').get_elapsed()
            if elapsed < threshold:
                continue
            self.send_down_mail(monitor, elapsed)
            monitor.save_val('hm_down_notified', Time.get_date())
            notified += 1
        return self.msg('msg_hydra_monitor_down_checked', (notified,))

    @staticmethod
    def send_down_mail(monitor: GDO_HydraMonitor, elapsed: float) -> None:
        mail = Mail.from_bot()
        for email in monitor.gdo_val('hm_emails').split(','):
            mail.recipient(email.strip())
        mail.subject(f"Hydra monitor down: {monitor.gdo_val('hm_name')}")
        mail.body(
            f"The Hydra monitor <strong>{monitor.gdo_val('hm_name')}</strong> "
            f"has not reported for {Time.human_duration(elapsed)}.")
        mail.send()
