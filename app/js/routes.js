define(
    ['backbone'],
    function(Backbone) {

        var editPage = function(App, Model, View, name, attrs) {
            console.log(name + ' by id page');
            self.app.models[name] = new Model(attrs);
            self.app.models[name].fetch();
            self.app.views[name] = new View(App, true);
            self.app.views[name].render();
        };

        var newPage = function(App, Model, View, name, attrs) {
            console.log(name + ' new page');
            self.app.models[name] = new Model(attrs);
            self.app.views[name] = new View(App, false);
            self.app.views[name].render();
        }

        return Backbone.Router.extend({
            initialize: function(app) {
                self.app = app;
            },
            routes: {
                // Overriddden edits
                'room/site/:id': 'edit_site',
                
                // Generic new and edit pages for top-level objects like Supplier, Staff.
                'room/:type/': 'new',
                'room/:type/:id': 'edit',

                // Order flow
                'room/site/:site_id/order_flow/': 'new_order',
                'room/site/:site_id/order_flow/:order_id': 'edit_order',

                // Pages for site expenses like CheckRequest.
                'room/site/:site_id/:type/': 'new_for_site',
                'room/site/:site_id/:type/:id': 'edit_for_site',

            },
            new: function(type) {
                requirejs(['app/models/' + type, 'app/views/' + type],
                          function(Model, View) {
                              newPage(self.app, Model, View, type)});
            },
            edit: function(type, id) {
                requirejs(['app/models/' + type, 'app/views/' + type],
                          function(Model, View) {
                              editPage(self.app, Model, View, type, {id: id})});
            },
            new_for_site: function(site_id, type) {
                requirejs(['app/models/' + type, 'app/views/' + type],
                          function(Model, View) {
                              newPage(self.app, Model, View, type, {site: site_id})});
            },
            edit_for_site: function(site_id, type, id) {
                requirejs(['app/models/' + type, 'app/views/' + type],
                          function(Model, View) {
                              editPage(self.app, Model, View, type, {site: site_id, id: id})});
            },
            new_order: function(site_id) {
                requirejs(['app/views/order_flow'],
                          function(OrderFlow) {
                              console.log('new order flow');
                              self.app.views['order_flow'] = new OrderFlow(site_id);
                          });
            },
            edit_order: function(site_id, order_id) {
                requirejs(['app/views/order_flow'],
                          function(OrderFlow) {
                              console.log('edit order flow');
                              self.app.views['order_flow'] = new OrderFlow(site_id, order_id);
                          });
            },
            edit_site: function(site_id) {
                console.log('edit site');
                requirejs(['app/views/site_flow'],
                          function(Flow) {
                              console.log('edit site flow');
                              self.app.views['site_flow'] = new Flow(self.app, site_id);
                          });
            },
                
        });
    }
);
