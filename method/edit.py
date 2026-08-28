from gdo.base.GDT import GDT
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.hydra_server.GDO_HydraHistory import GDO_HydraHistory
from gdo.hydra_server.GDO_HydraMonitor import GDO_HydraMonitor
from gdo.message.GDT_HTML import GDT_HTML
from gdo.ui.GDT_Card import GDT_Card
from gdo.core.GDT_Container import GDT_Container


class edit(MethodForm):
    """Edit the monitor selected by the preceding token login."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_needs_authentication(self) -> bool:
        return False

    def monitor(self) -> GDO_HydraMonitor | None:
        return GDO_HydraMonitor.table().get_by_id(self._env_session.get('hydra_monitor_token'))

    def gdo_parameters(self) -> list[GDT]:
        monitor = self.monitor()
        return [] if monitor is None else [
            monitor.column('hm_name'),
            monitor.column('hm_emails'),
            monitor.column('hm_ports'),
        ]

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_fields(*self.parameters().values())
        super().gdo_create_form(form)

    def gdo_execute(self) -> GDT:
        if self.monitor() is None:
            return self.err('err_hydra_monitor_session')
        return super().gdo_execute()

    def form_submitted(self) -> GDT:
        monitor = self.monitor()
        for key in ('hm_name', 'hm_emails', 'hm_ports'):
            if value := self.param_val(key):
                monitor.save_val(key, value)
        return self.render_page()

    def render_page(self) -> GDT:
        monitor = self.monitor()
        card = GDT_Card().gdo(monitor).title('hydra_monitor', (monitor.get_id(),))
        card.get_content().add_fields(
            monitor.column('hm_name'), monitor.column('hm_emails'),
            monitor.column('hm_curr_cpu'), monitor.column('hm_curr_hdd'),
            monitor.column('hm_last_signal'), monitor.column('hm_created'),
        )
        return GDT_Container().vertical().add_fields(card, self.get_form(), self.history_graph(monitor))

    @staticmethod
    def history_graph(monitor: GDO_HydraMonitor) -> GDT_HTML:
        history = GDO_HydraHistory.table().select().where('hh_monitor', monitor.get_id()).order('hh_created DESC').limit(24).exec().fetch_all()
        values = [float(row.gdo_value('hh_cpu_load') or 0) for row in reversed(history)]
        if not values:
            return GDT_HTML().html('<p>No monitor samples recorded yet.</p>')
        divisor = max(1, len(values) - 1)
        points = ' '.join(f'{index * 300 / divisor:.1f},{100 - min(100, max(0, value)):.1f}' for index, value in enumerate(values))
        return GDT_HTML().html(
            '<svg class="hydra-history" viewBox="0 0 300 100" role="img" aria-label="CPU history">'
            f'<polyline fill="none" stroke="currentColor" points="{points}"/>'
            '</svg>')
