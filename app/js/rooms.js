define(
    ['app/routes', 'app/gapi', 
     'app/views/auth', 'app/views/staff',
     'app/models/user'
    ], 
    function(Routes, ApiManager, 
             AuthView, StaffView, 
             User) {
        var Rooms = function() {
            var self = this;
            this.apiManager = new ApiManager(this);
            this.views.auth = new AuthView(this);
            this.views.staff = new StaffView(this);
            this.user = new User();
            this.routes = new Routes();
            this.routes.app = this;
            // Backbone.history.start({pushState: true});
            
            this.apiManager.on('signin', function() { 
                self.user.fetch();            
            });
            this.user.on('change', self.user.home);
            this.user.on('home:staff', function() {
                console.log('got user event');
                var loc = window.location;
                // needs to match 'StaffHome' Route in main.py
                var new_loc = loc.protocol + '//' + loc.host + '/staff_home';
                window.location = new_loc;
                //self.routes.navigate('room/staff_home', {trigger: true});
            });               
        };
        Rooms.prototype = {
            views: {},
        };
        return Rooms;
    }
);
