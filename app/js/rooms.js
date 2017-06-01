define(
    ['app/routes', 'app/gapi', 
     'app/views/auth', 'app/views/welcome_auth', 'app/views/staff',
     'app/models/user'
    ], 
    function(Routes, ApiManager, 
             AuthView, WelcomeAuthView, StaffView, 
             User) {
        var Rooms = function() {
            var self = this;
            this.user = new User();
            this.apiManager = new ApiManager(this);
            this.views.auth = new AuthView(this);
            this.views.welcome_auth = new WelcomeAuthView(this);
            this.views.staff = new StaffView(this);
            this.routes = new Routes();
            this.routes.app = this;
            // Backbone.history.start({pushState: true});
            
            this.apiManager.on('signin', function() { 
                self.user.fetch();            
            });
            this.user.on('change', function() {
                console.log('user change');
            });
            this.user.on('user:is:staff', function() {
                var loc = window.location;
                var new_loc = loc.protocol + '//' + loc.host + '/';
                window.location = new_loc;
            });               
        };
        Rooms.prototype = {
            views: {},
        };
        return Rooms;
    }
);
