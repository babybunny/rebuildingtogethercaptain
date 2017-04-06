define(['app/gapi', 'app/views/auth', 'app/models/user'], 
       function(ApiManager, AuthView, User) {
  var Rooms = function() {
    var self = this;
    this.apiManager = new ApiManager(this);
    this.views.auth = new AuthView(this);
    this.user = new User();
    this.apiManager.on('ready', function() { 
            console.log('apimanager ready'); 
            self.user.fetch();
            
        });
  };
  Rooms.prototype = {
    views: {},
  };
  return Rooms;
});