define(
    ['backbone'],
    function(Backbone) {

        var editPage = function(App, Model, View, name, id) {
            console.log(name + ' by id page');
            self.app.models[name] = new Model({id: id});
            self.app.models[name].fetch();
            self.app.views[name] = new View(App, true);
            self.app.views[name].render();
        };

        var newPage = function(App, Model, View, name) {
            console.log(name + ' new page');
            self.app.models[name] = new Model();
            self.app.views[name] = new View(App, false);
            self.app.views[name].render();
        }

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
            staff_new: function() {
                requirejs(['app/models/staff', 'app/views/staff'],
                          function(Model, View) {
                              newPage(self.app, Model, View, 'staff')});
            },
            staff: function(id) {
                requirejs(['app/models/staff', 'app/views/staff'],
                          function(Model, View) {
                              editPage(self.app, Model, View, 'staff', id)});
            },
            supplier_new: function() {
                requirejs(['app/models/supplier', 'app/views/supplier'],
                          function(Model, View) {
                              newPage(self.app, Model, View, 'supplier')});
            },
            supplier: function(id) {
                requirejs(['app/models/supplier', 'app/views/supplier'],
                          function(Model, View) {
                              editPage(self.app, Model, View, 'supplier', id)});
            }
        });
    }
);
