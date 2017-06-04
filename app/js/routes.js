define(
    ['backbone'],
    function(Backbone) {
        return Backbone.Router.extend({
            routes: {
                '': 'welcome',                
                'supplier/:id': 'supplier'
            },
            welcome: function() {
                console.log('welcome page');                
            },
            supplier: function() {
                console.log('supplier page');                
            }
        });
    }
);
