define(
    ['backbone',
     'app/models/supplier', 'app/views/supplier',
    ],
    function(Backbone,
             Supplier, SupplierView) {
        return Backbone.Router.extend({
            initialize: function(app) {
                var self = this;
                self.app = app;
            },
            routes: {
                '': 'welcome',                
                'supplier/': 'supplier_new',
                'supplier/:id': 'supplier'
            },
            welcome: function() {
                console.log('welcome page');                
            },
            supplier_new: function(id) {
                console.log('supplier new page');
                rooms.models.supplier = new Supplier();
                rooms.views.supplier = new SupplierView(rooms, false);
                rooms.views.supplier.render();
            },
            supplier: function(id) {
                console.log('supplier by id page');
                rooms.models.supplier = new Supplier({id: id});
                rooms.models.supplier.fetch({data: {id: id}});
                rooms.views.supplier = new SupplierView(rooms, true);
                rooms.views.supplier.render();
            }
        });
    }
);
