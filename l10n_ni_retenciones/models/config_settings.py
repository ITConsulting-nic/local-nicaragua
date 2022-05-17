from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    report_retenciones = fields.Boolean()

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            report_retenciones=bool(get_param('l10n_ni_retenciones.report_retenciones'))
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        report_retenciones = self.report_retenciones
        set_param('l10n_ni_retenciones.report_retenciones', report_retenciones)
