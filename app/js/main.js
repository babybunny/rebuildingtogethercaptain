// don't think we need this file any more.

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
        'backbone': {
            deps: ['underscore-min'],
            exports: 'Backbone'
        },
        'app/rooms': {
            deps: ['underscore-min', 'backbone']
        }
    }
});

require(
    ['app/rooms'],
    function(Rooms) {
        window.rooms = new Rooms();
    }
);
