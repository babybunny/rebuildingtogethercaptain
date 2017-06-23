define(
    ['backbone'],
    function(Backbone) {
        var Model = Backbone.Model.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/wsgi_service.checkrequest_',
        });
        
        return Model;
    }
);
