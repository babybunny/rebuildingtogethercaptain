define(
    ['backbone'],
    function(backbone) {
        var User = backbone.Model.extend({
            // matches first part of 'name' in @endpoints.method
            urlRoot: 'current_user'
        });
        
        return User;
    }
);
