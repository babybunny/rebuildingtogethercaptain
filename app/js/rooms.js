requirejs.config({
    baseUrl: '/js/lib',
    paths: {
        app: '/js/app',
    },
});

require(
    ['app/routes', 'app/gapi', 
     'app/views/auth', 'app/models/user',
    ], 
    function(Routes, ApiManager, 
             AuthView, User) {
        var Rooms = function() {
            var self = this;
            this.user = new User();
            this.apiManager = new ApiManager(this);
            this.views.auth = new AuthView(this);
            this.apiManager.on('signin', function() { 
                self.user.fetch();            
                self.routes = new Routes(self);
                self.routes.app = self;
                Backbone.history.start({pushState: true});
            });
            console.log('rooms!');
        };
        Rooms.prototype = {
            views: {},
            models: {},
        };
        window.rooms = new Rooms();
    }
);
