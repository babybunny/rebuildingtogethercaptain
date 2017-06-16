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
                'room/:type/': 'new',
                'room/:type/:id': 'edit',
            },
            new: function(type) {
                requirejs(['app/models/' + type, 'app/views/' + type],
                          function(Model, View) {
                              newPage(self.app, Model, View, type)});
            },
            edit: function(type, id) {
                requirejs(['app/models/' + type, 'app/views/' + type],
                          function(Model, View) {
                              editPage(self.app, Model, View, type, id)});
            },
        });
    }
);
