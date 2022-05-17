from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    factura_venta = fields.Boolean()
    nota_credito = fields.Boolean()
    nota_debito = fields.Boolean()
    # etc = fields.Boolean()
    recibo_caja = fields.Boolean()
    # constancia_retención = fields.Boolean()


    @api.model
    def get_values(self):
        res = super(AccountConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            factura_venta=bool(get_param('l10n_ni_formatos_dgi.factura_venta')),
            nota_credito=bool(get_param('l10n_ni_formatos_dgi.nota_credito')),
            nota_debito=bool(get_param('l10n_ni_formatos_dgi.nota_debito')),
            # etc=bool(get_param('l10n_ni_formatos_dgi.etc')),
            recibo_caja=bool(get_param('l10n_ni_formatos_dgi.recibo_caja')),
            # constancia_retención=bool(get_param('l10n_ni_formatos_dgi.constancia_retención')),

        )
        return res

    def set_values(self):
        super(AccountConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param

        factura_venta = self.factura_venta
        nota_credito = self.nota_credito
        # etc = self.etc
        nota_debito = self.nota_debito
        recibo_caja = self.recibo_caja
        # constancia_retención = self.constancia_retención




        set_param('l10n_ni_formatos_dgi.factura_venta', factura_venta)
        set_param('l10n_ni_formatos_dgi.nota_credito', nota_credito)
        set_param('l10n_ni_formatos_dgi.nota_debito', nota_debito)
        # set_param('l10n_ni_formatos_dgi.etc', etc)
        set_param('l10n_ni_formatos_dgi.recibo_caja', recibo_caja)
        # set_param('l10n_ni_formatos_dgi.constancia_retención', constancia_retención)