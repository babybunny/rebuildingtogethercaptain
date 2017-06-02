requirejs.config({
    baseUrl: 'js/lib',
    paths: {
        app: '../app',
    },
});

require(
    ['backbone',
     'underscore-min',
     'app/gapi',
     'app/views/welcome_auth',
     'app/models/user'
    ], 
    function(Backbone, _,
             ApiManager, WelcomeAuthView, User) {
        var Welcome = function() {
            var self = this;
            this.user = new User();
            this.apiManager = new ApiManager(this);
            this.welcome_auth = new WelcomeAuthView(this);
            
            this.apiManager.on('signin', function() { 
                self.user.fetch();            
            });
            this.user.on('change', function() {
                console.log('user change');                
                if (!self.apiManager.loginState.get('state')) {
                    return;
                }
                if (self.user.has('staff_key') || self.user.has('captain_key')) {
                    console.log('user is known');
                    var loc = window.location;
                    // Go to /, which will redirect users who are logged in.
                    var new_loc = loc.protocol + '//' + loc.host + '/';
                    window.location = new_loc;
                } else {
                    console.log('user is not known');
                }
            });
        };
        window.welcome = new Welcome();
    }
);
