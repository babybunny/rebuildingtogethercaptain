define(
    ['backbone'],
    function(Backbone) {
        var Model = Backbone.Model.extend({
            // matches first part of method name in @remote.method
            urlRoot: 'TODO',  # will be like '/wsgi_service.supplier_'
            initialize: function(name) {
                this.urlRoot = '/wsgi_service.' + name + '_';
            }
        });
        
        return Model;
    }
);
