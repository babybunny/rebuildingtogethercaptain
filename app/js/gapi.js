define(['app/config', 'backbone'], function(config, backbone) {
  var rooms;
  var numApisToLoad = 2;  // the number of gapi.load or gapi.client.load calls below
  var LoginState = backbone.Model.extend();

  function ApiManager(_rooms) {
    rooms = _rooms;
    this.loadGapi();
  }

  _.extend(ApiManager.prototype, backbone.Events);

  ApiManager.prototype.loginState = new LoginState({state: 'unknown'});

  ApiManager.prototype.init = function() {
    var self = this;

    function loadedAuthedAndReady() {
        console.log('all ready');

        // Listen for sign-in state changes.
        googleAuth = gapi.auth2.getAuthInstance();
        googleAuth.isSignedIn.listen(updateSigninStatus);
        googleAuth.currentUser.listen(updateUserDetails);

        // Handle the initial sign-in state.
        updateUserDetails(googleAuth.currentUser.get());
        updateSigninStatus(googleAuth.isSignedIn.get());

        self.trigger('signin');
    }

    function apisLoaded() {
      if (--numApisToLoad == 0) {
          console.log('loaded all APIs');
          gapi.client.init({ apiKey: config.apiKey, clientId: config.clientId, scope: config.scopes})
          .then(loadedAuthedAndReady);
      }
    }
    
    function updateSigninStatus(isSignedIn) {
      self.loginState.set('state', isSignedIn);
    }   
    function updateUserDetails(googleUser) {
        if (googleUser.isSignedIn()) {
            self.loginState.set('email', googleUser.getBasicProfile().getEmail());
            self.trigger('signin');
        } else {
            self.loginState.set('email', 'not signed in');
        }
    }   

    gapi.client.load('oauth2', 'v2', apisLoaded);
    gapi.client.load('roomApi', 'v1', apisLoaded, 
                     window.location + '_ah/api')
  };

  ApiManager.prototype.handleSignin = function() {
    gapi.auth2.getAuthInstance().signIn();
  };

  ApiManager.prototype.handleSignout = function() {
    gapi.auth2.getAuthInstance().disconnect();
  };

  ApiManager.prototype.loadGapi = function() {
    var self = this;

    // Don't load gapi if it's already present
    if (typeof gapi !== 'undefined') {
      console.log('gapi already loaded');
      return self.init();
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

  // Override sync with a custom method that works with gapi and our roomApi
  Backbone.sync = function(method, model, options) {
    options || (options = {});

    console.log('sync: ' + method + ' ' + model.url);

    switch (method) {
      case 'create':
      break;

      case 'update':
      break;

      case 'delete':
      break;

      case 'read':
          var request = gapi.client.roomApi[model.url].list(options.data);
          backbone.gapiRequest(request, method, model, options);
      break;
    }
  };

  Backbone.gapiRequest = function(request, method, model, options) {
      var result;
      request.execute(function(res) {
              if (res.error) {
                  if (options.error) options.error(res);
              } else if (options.success) {
                  result = res;
                  options.success(result, true, request);
              }
          });
  };

  return ApiManager;
});
