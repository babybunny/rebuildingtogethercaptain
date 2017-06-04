define(
    ['backbone'],
    function(Backbone) {
        return Backbone.Router.extend({
            routes: {
                '': 'welcome',                
            },
            welcome: function() {
                console.log('welcome page');                
            }
        });
    }
);
