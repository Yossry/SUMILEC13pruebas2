from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    lot_ids = fields.Many2many('stock.production.lot', string="Crate", copy=False)
    assign_lot = fields.Boolean(string='Assign Lot')
    
    def create_stock_move_line(self):
        for move in self:
            if move.move_line_ids:
                if move.sale_line_id and move.sale_line_id.lot_ids:
                    move.move_line_ids.unlink()
                    for lot_id in move.sale_line_id.lot_ids:
                        vals = {
                                'move_id': move.id,
                                'product_id': move.product_id.id,
                                'product_uom_id': move.product_uom.id,
                                'location_id': move.location_id.id,
                                'location_dest_id': move.location_dest_id.id,
                                'picking_id': move.picking_id.id,
                                'lot_id':lot_id.id,
                                }
                        self.env['stock.move.line'].create(vals)
     
    def _action_assign(self):
        res = super(StockMove, self)._action_assign()
        for move in self:
            if not move.assign_lot:
                move.create_stock_move_line()
                move.assign_lot = True
        return res