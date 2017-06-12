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
        'app/routes', 
        'app/models/staff',
        'app/views/staff'
    ], 
    function(Backbone, Routes, Staff, StaffView) { 
        Backbone.sync = function(method, model, options) {
            console.log('Backbone sync: ' + method + ' options: ' + JSON.stringify(options));

                var settings = {
                    url: this.urlRoot + method,
                    method: "POST",
                    contentType: "application/json",
                    success: function(data, status, xhr) {
                        console.log('staff ' + method + ' success: ' + JSON.stringify(data));
                        options.success(data);
                    }
                };
                
                switch (method) {
                case 'read':
                    Backbone.$.ajax(_.extend(settings, {
                        data: JSON.stringify({"id": model.id})
                    }))
                    break;
                case 'create':
                case 'update':
                    Backbone.$.ajax(_.extend(settings, {
                        data: JSON.stringify(model.attributes),
                    }))
                    break;
                }
            }
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
