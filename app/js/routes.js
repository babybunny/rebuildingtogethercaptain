define(
    ['backbone',
     'app/models/supplier', 'app/views/supplier',
    ],
    function(Backbone,
             Supplier, SupplierView) {
        return Backbone.Router.extend({
            initialize: function(app) {
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
                self.app.models.supplier = new Supplier();
                self.app.views.supplier = new SupplierView(self.app, false);
                self.app.views.supplier.render();
            },
            supplier: function(id) {
                console.log('supplier by id page');
                self.app.models.supplier = new Supplier({id: id});
                self.app.models.supplier.fetch({data: {id: id}});
                self.app.views.supplier = new SupplierView(self.app, true);
                self.app.views.supplier.render();
            }
        });
    }
);
