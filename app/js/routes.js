define(
    ['backbone',
     'app/models/supplier', 'app/views/supplier',
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
            staff_new: function() {
                requirejs(['app/models/staff', 'app/views/staff'],
                          function(Model, View) {
                              console.log('staff new page');
                              self.app.models.staff = new Model();
                              self.app.views.staff = new View(self.app, false);
                              self.app.views.staff.render();
                          });
            },
            staff: function(id) {
                requirejs(['app/models/staff', 'app/views/staff'],
                          function(Model, View) {
                              console.log('staff by id page');
                              self.app.models.staff = new Model({id: id});
                              self.app.models.staff.fetch({data: {id: id}});
                              self.app.views.staff = new View(self.app, true);
                              self.app.views.staff.render();
                          });
            }
        });
    }
);
