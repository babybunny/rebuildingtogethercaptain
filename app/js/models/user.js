define(
    ['backbone'],
    function(backbone) {
        var User = backbone.Model.extend({
            // matches first part of 'name' in @endpoints.method
            url: 'current_user'
        });
        
        return User;
    }
);
