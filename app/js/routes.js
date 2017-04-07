define(
    ['app/views/staff'],
    function(StaffView) {
        return Backbone.Router.extend({
            routes: {
                'room/staff_home': 'staffHome',
                '': 'welcome',                
            },
            
            staffHome: function() {
                console.log('headed to staff home');
                rooms.views.staff.render()
            },
            welcome: function() {
                console.log('welcome page');                
            }
        });
    }
);
