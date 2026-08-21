from gdo.base.GDO import GDO
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.date.GDT_Duration import GDT_Duration


class module_hydra_server(GDO_Module):
    """Hydra server: monitors are addressed solely by bearer tokens."""

    def gdo_classes(self) -> list[type[GDO]]:
        from gdo.hydra_server.GDO_HydraMonitor import GDO_HydraMonitor
        from gdo.hydra_server.GDO_HydraHistory import GDO_HydraHistory
        return [GDO_HydraMonitor, GDO_HydraHistory]

    def gdo_dependencies(self) -> list:
        return ['bootstrap5', 'mail']

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Duration('monitor_down_after').not_null().units(2, False).initial('5m'),
        ]

    def cfg_monitor_down_after(self) -> int:
        return self.get_config_value('monitor_down_after')
