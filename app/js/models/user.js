define(
    function() {
        var User = Backbone.Model.extend({
            // matches first part of 'name' in @endpoints.method
            url: 'current_user'
        });
        
        User.prototype.home = function() {
            if(this.get('staff_key')) {
                console.log('user is staff, going home');
                this.trigger('home:staff');
            } else {
                console.log('user is nobody, going home');
            }
        };
        
        return User;
    }
);
