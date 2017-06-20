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
                'room/:type/': 'new',
                'room/:type/:id': 'edit',
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
        });
    }
);
