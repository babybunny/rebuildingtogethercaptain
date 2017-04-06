define(['app/gapi', 'app/views/auth', 'app/models/user', 'app/routes'], 
       function(ApiManager, AuthView, User, Routes) {
  var Rooms = function() {
    var self = this;
    this.apiManager = new ApiManager(this);
    this.views.auth = new AuthView(this);
    this.user = new User();
    this.routes = new Routes();
    this.routes.app = this;
    Backbone.history.start({pushState: true});

    this.apiManager.on('signin', function() { 
            self.user.fetch();            
        });
    this.user.on('change', self.user.home);
    this.user.on('home:staff', function() {self.routes.navigate('room/staff_home', {trigger: true});})

  };
  Rooms.prototype = {
    views: {},
  };
  return Rooms;
});