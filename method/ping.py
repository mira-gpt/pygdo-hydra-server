from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_Float import GDT_Float
from gdo.core.GDT_Secret import GDT_Secret
from gdo.core.GDT_Token import GDT_Token
from gdo.date.Time import Time
from gdo.file.GDT_FileSize import GDT_FileSize
from gdo.hydra_server.GDO_HydraHistory import GDO_HydraHistory
from gdo.hydra_server.GDO_HydraMonitor import GDO_HydraMonitor


class ping(Method):
    """Accept one authenticated resource sample from a Hydra client cronjob."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_in_channels(self) -> bool:
        return False

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Token('token').not_null().positional(),
            GDT_Secret('password').not_null().positional(),
            GDT_Float('cpu_load').min(0).max(100).not_null().positional(),
            GDT_FileSize('ram_used').not_null().positional(),
            GDT_FileSize('ram_total').not_null().positional(),
            GDT_FileSize('disk_used').not_null().positional(),
            GDT_FileSize('disk_total').not_null().positional(),
            GDT_FileSize('project_used').not_null().positional(),
        ]

    def gdo_execute(self) -> GDT:
        monitor = GDO_HydraMonitor.table().get_by_id(self.param_value('token'))
        if monitor is None or not monitor.column('hm_password_hash').check(
                monitor.gdo_val('hm_password_hash'), self.param_value('password')):
            return self.err('err_hydra_monitor_credentials')

        monitor.save_values({
            'hm_curr_cpu': self.param_value('cpu_load'),
            'hm_curr_hdd': self.param_value('disk_used'),
            'hm_max_hdd': self.param_value('disk_total'),
            'hm_last_signal': Time.get_date(),
            'hm_down_notified': None,
        })
        GDO_HydraHistory.blank({
            'hh_monitor': monitor.get_id(),
            'hh_cpu_load': str(self.param_value('cpu_load')),
            'hh_ram_used': str(self.param_value('ram_used')),
            'hh_ram_total': str(self.param_value('ram_total')),
            'hh_disk_used': str(self.param_value('disk_used')),
            'hh_disk_total': str(self.param_value('disk_total')),
            'hh_project_used': str(self.param_value('project_used')),
        }).insert()
        return self.msg('msg_hydra_ping', (monitor.get_id(),))
