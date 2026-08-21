from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_Float import GDT_Float
from gdo.core.GDT_JSON import GDT_JSON
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_Password import GDT_Password
from gdo.core.GDT_Token import GDT_Token
from gdo.core.GDT_User import GDT_User
from gdo.date.GDT_Created import GDT_Created
from gdo.date.GDT_Timestamp import GDT_Timestamp
from gdo.file.GDT_FileSize import GDT_FileSize
from gdo.mail.GDT_Emails import GDT_Emails


class GDO_HydraMonitor(GDO):
    """One token/password monitor, independent of PyGDO user accounts."""

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_Token('hm_token').primary().not_null(),
            GDT_Name('hm_name').not_null(),
            GDT_Password('hm_password_hash').not_null(),
            GDT_Emails('hm_emails'),
            GDT_JSON('hm_ports'),
            GDT_FileSize('hm_curr_hdd'),
            GDT_FileSize('hm_max_hdd'),
            GDT_Float('hm_curr_cpu'),
            GDT_Float('hm_max_cpu'),
            GDT_User('hm_user'),
            GDT_Created('hm_created'),
            GDT_Timestamp('hm_last_signal'),
            GDT_Timestamp('hm_down_notified'),
        ]
