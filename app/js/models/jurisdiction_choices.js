define(
    ['backbone'],
    function(Backbone) {
        var Model = Backbone.Model.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/choices_api.jurisdiction_choices_',
        });
        
        return Model;
    }
);
