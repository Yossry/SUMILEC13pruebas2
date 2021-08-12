# -*- coding: utf-8 -*-

from odoo import models, fields, api
from ast import literal_eval


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    def get_stock_picking_action_picking_type(self):
        return self._get_action('stock_menu.stock_picking_action_picking_type_edit')

