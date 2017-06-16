requirejs.config({
    shim: {
        "bootstrap" : { "deps" :['jquery'] }  // because bootstrap doesn't use AMD to declare its dependency on jquery
    },
    baseUrl: '/js/lib',
    paths: {
        app: '/js/app',
    },
});

require(
    [
        'backbone',
        'app/common',
        'app/routes', 
    ], 
    function(Backbone, common, Routes) { 
        var Rooms = function() {
            var self = this;
            this.routes = new Routes(this);
            this.go();
        };
        Rooms.prototype = {
            views: {},
            models: {},
            go: function() {
                Backbone.history.start({pushState: true});
            }
        };
        window.rooms = new Rooms();
    }
);
