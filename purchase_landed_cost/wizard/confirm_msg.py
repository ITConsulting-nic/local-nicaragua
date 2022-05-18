# Copyright 2014-2016 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3
from odoo import _, api, fields, models
import logging
_logger = logging.getLogger(__name__)

class ConfirmNsg(models.TransientModel):
    _name = "confirm.msg"
    _description = "mensage de confirmacion"


    def btn_approve_picking_import(self):
        #self._get_tasa()
        view_id = self.env.ref('purchase_landed_cost.picking_import_wizard_view').id
        return {
            'name': 'Import incoming shipment',
            'type': 'ir.actions.act_window',
            'views_type': 'form',
            'views_mode': 'form',
            'res_model': 'picking.import.wizard',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'context': self.env.context,
        }

    def btn_approve_picking_import_list(self):

        #self._get_tasa()
        view_id = self.env.ref('purchase_landed_cost.import_invoice_line_wizard_view').id
        return {
            'name': 'Import supplier invoice line',
            'type': 'ir.actions.act_window',
            'views_type': 'form',
            'views_mode': 'form',
            'res_model': 'import.invoice.line.wizard',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'context': self.env.context,
        }

