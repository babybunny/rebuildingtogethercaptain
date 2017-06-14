define(
    ['backbone',
     'app/models/supplier', 'app/views/supplier',
     'app/models/staff', 'app/views/staff',
    ],
    function(Backbone,
             Supplier, SupplierView,
             Staff, StaffView) {
        return Backbone.Router.extend({
            initialize: function(app) {
                self.app = app;
            },
            routes: {
                'room/supplier/': 'supplier_new',
                'room/supplier/:id': 'supplier',
                'room/staff/': 'staff_new',
                'room/staff/:id': 'staff'
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
            },
            staff_new: function(id) {
                console.log('staff new page');
                self.app.models.staff = new Staff();
                self.app.views.staff = new StaffView(self.app, false);
                self.app.views.staff.render();
            },
            staff: function(id) {
                console.log('staff by id page');
                self.app.models.staff = new Staff({id: id});
                self.app.models.staff.fetch({data: {id: id}});
                self.app.views.staff = new StaffView(self.app, true);
                self.app.views.staff.render();
            }
        });
    }
);
