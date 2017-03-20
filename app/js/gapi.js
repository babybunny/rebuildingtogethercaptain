define(['app/config', 'backbone-min'], function(config, backbone) {
  var rooms;
  var LoginState = backbone.Model.extend();

  function ApiManager(_rooms) {
    rooms = _rooms;
    this.loadGapi();
  }

  _.extend(ApiManager.prototype, Backbone.Events);

  ApiManager.prototype.loginState = new LoginState({state: 'unknown'});

  ApiManager.prototype.init = function() {
    var self = this;

    // gapi.client.load('tasks', 'v1', function() { /* Loaded */ });

    function handleClientLoad() {
      gapi.client.setApiKey(config.apiKey);
      gapi.load('client:auth2', initAuth);
    }

    function initAuth() {
      gapi.client.init({ apiKey: config.apiKey, clientId: config.clientId, scope: config.scopes})
      .then(function() {
        // Listen for sign-in state changes.
        googleAuth = gapi.auth2.getAuthInstance();
        googleAuth.isSignedIn.listen(updateSigninStatus);
        googleAuth.currentUser.listen(updateUserDetails);

        // Handle the initial sign-in state.
        updateSigninStatus(googleAuth.isSignedIn.get());
        updateUserDetails(googleAuth.currentUser.get());
      });
    }

    function updateSigninStatus(isSignedIn) {
      self.loginState.set('state', isSignedIn);
    }   
    function updateUserDetails(googleUser) {
      self.loginState.set('email', googleUser.getBasicProfile().getEmail());
    }   

    handleClientLoad();
  };

  ApiManager.prototype.handleSignin = function() {
    gapi.auth2.getAuthInstance().signIn();
  };

  ApiManager.prototype.handleSignout = function() {
    gapi.auth2.getAuthInstance().signOut();
  };

  ApiManager.prototype.loadGapi = function() {
    var self = this;

    // Don't load gapi if it's already present
    if (typeof gapi !== 'undefined') {
      console.log('gapi already loaded');
      return this.init();
    }

    require(['https://apis.google.com/js/client.js'], function() {
      // Poll until gapi is ready
      function checkGAPI() {
        if (gapi && gapi.client) {
          self.init();
        } else {
          setTimeout(checkGAPI, 100);
        }
      }
      
      checkGAPI();
    });
  };

  Backbone.sync = function(method, model, options) {
    options || (options = {});

    switch (method) {
      case 'create':
      break;

      case 'update':
      break;

      case 'delete':
      break;

      case 'read':
      break;
    }
  };

  return ApiManager;
});
