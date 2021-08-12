odoo.define('audilog_peti', function(require){
    "use strict";

     var models = require('point_of_sale.models');
     models.load_fields("res.partner", ['create_date','create_uid','write_date','write_uid' ]);

     models.load_models({
        model:  'res.users',
        fields: ['name'],
        loaded: function(self, users_create){
            self.users_create = users_create;
        },
    });


});