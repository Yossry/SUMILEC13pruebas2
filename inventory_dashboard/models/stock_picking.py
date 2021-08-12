# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InventoryDashboard(models.Model):
    _inherit = 'stock.picking.type'

    def get_late_picking(self):
        """:return the value for the late picking"""
        for rec in self:
            if rec.count_picking != 0:
                rec.picking_late = (rec.count_picking_late * 100) / rec.count_picking
            else:
                rec.picking_late = 0.0

    def get_backorders(self):
        """:return the value for the backorders"""
        for rec in self:
            if rec.count_picking != 0:
                rec.picking_backorders = (rec.count_picking_backorders * 100) / rec.count_picking
            else:
                rec.picking_backorders = 0.0

    picking_late = fields.Float(compute=get_late_picking, string='Retraso %', default=0.0)
    picking_backorders = fields.Float(compute=get_backorders, string='Pedidos Pendientes %', default=0.0)
    max_rate = fields.Integer(string='Maximum rate', default=100)
