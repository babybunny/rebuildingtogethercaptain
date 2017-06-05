define(
    ['backbone'],
    function(Backbone) {
        var Model = Backbone.Model.extend({
            // matches first part of 'name' in @endpoints.method
            urlRoot: 'supplier'
        });
        
        return Model;
    }
);
