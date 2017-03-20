requirejs.config({
  baseUrl: 'js/lib',
  paths: {
    app: '../app',
  },
  shim: {
    'underscore-min': {
      exports: '_'
    },
    'backbone-min': {
        deps: ['underscore-min'],
      exports: 'Backbone'
    },
    'app/rooms': {
      deps: ['underscore-min', 'backbone-min']
    }
  }
});

require(['app/rooms'],
  function(Rooms) {
    window.rooms = new Rooms();
  }
);
