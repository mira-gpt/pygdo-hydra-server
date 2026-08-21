from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Float import GDT_Float
from gdo.core.GDT_Token import GDT_Token
from gdo.core.GDT_UInt import GDT_UInt
from gdo.date.GDT_Created import GDT_Created


class GDO_HydraHistory(GDO):
    """One append-only resource sample reported by a monitor client."""

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('hh_id'),
            GDT_Token('hh_monitor').not_null(),
            GDT_Float('hh_cpu_load').precision(3),
            GDT_UInt('hh_ram_used').bytes(8),
            GDT_UInt('hh_ram_total').bytes(8),
            GDT_UInt('hh_disk_used').bytes(8),
            GDT_UInt('hh_disk_total').bytes(8),
            GDT_UInt('hh_project_used').bytes(8),
            GDT_Created('hh_created'),
        ]
