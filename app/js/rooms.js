requirejs.config({
    baseUrl: 'js/lib',
    paths: {
        app: '../app',
    },
});

require(
    ['app/routes', 'app/gapi', 
     'app/views/auth',
     'app/models/user'
    ], 
    function(Routes, ApiManager, 
             AuthView, 
             User) {
        var Rooms = function() {
            var self = this;
            this.user = new User();
            this.apiManager = new ApiManager(this);
            this.views.auth = new AuthView(this);
            this.routes = new Routes();
            this.routes.app = this;
            // Backbone.history.start({pushState: true});
            
            this.apiManager.on('signin', function() { 
                self.user.fetch();            
            });
        };
        Rooms.prototype = {
            views: {},
        };
        window.rooms = new Rooms();
    }
);
