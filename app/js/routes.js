define(function() {
        return Backbone.Router.extend({
                routes: {
                    'room/staff_home': 'staffHome'
                        },

                    initialize: function() {
                },

                    staffHome: function() {
                    console.log('headed to staff home');
                }
            });
    });