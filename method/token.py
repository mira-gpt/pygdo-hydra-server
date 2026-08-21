from gdo.base.GDT import GDT
from gdo.core.GDT_Secret import GDT_Secret
from gdo.core.GDT_Token import GDT_Token
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.hydra_server.GDO_HydraMonitor import GDO_HydraMonitor


class token(MethodForm):
    """Log into exactly one monitor and keep its token in the HTTP session."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'hydra.token'

    def gdo_needs_authentication(self) -> bool:
        return False

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Token('token').not_null().positional(),
            GDT_Secret('password').not_null().positional(),
        ]

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_fields(*self.parameters().values())
        super().gdo_create_form(form)

    def form_submitted(self) -> GDT:
        monitor = GDO_HydraMonitor.table().get_by_id(self.param_value('token'))
        if monitor is None or not monitor.column('hm_password_hash').check(
                monitor.gdo_val('hm_password_hash'), self.param_value('password')):
            return self.err('err_hydra_monitor_credentials')
        self._env_session.set('hydra_monitor_token', monitor.get_id()).save()
        return self.redirect(self.gdo_module().href('edit'))
