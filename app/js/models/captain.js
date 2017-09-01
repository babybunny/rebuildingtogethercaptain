define(
    ['backbone'],
    function(Backbone) {
        var Model = Backbone.Model.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/wsgi_service.captain_',
            defaults: {
                tshirt_size: 'Large'
            }
        });

        return Model;
    }
);
