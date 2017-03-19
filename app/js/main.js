requirejs.config({
  baseUrl: 'js',
  paths: {},
  shim: {}
});

require(['rooms'],
  function(Rooms) {
    window.rooms = new Rooms();
  }
);
