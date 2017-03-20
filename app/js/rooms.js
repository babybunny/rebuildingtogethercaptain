define(['app/gapi', 'app/views/auth'], 
       function(ApiManager, AuthView) {
  var Rooms = function() {
    this.apiManager = new ApiManager(this);
    this.views.auth = new AuthView(this);
  };
  Rooms.prototype = {
    views: {},
  };
  return Rooms;
});