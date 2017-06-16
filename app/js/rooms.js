requirejs.config({
    shim: {
        // because bootstrap doesn't use AMD to declare its dependency on jquery
        "bootstrap" : { "deps" :['jquery'] }  
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
    ], 
    function(Backbone, Routes) { 
        Backbone.sync = function(method, model, options) {
            console.log('Backbone sync: ' + method
                        + ' options: ' + JSON.stringify(options));
            
            // Template for a model's sync settings.
            var settings = {
                url: this.urlRoot + method,  // '/wsgi_service.captain_' + 'create'

                // Protorpc always expects JSON in a POST, it's not RESTful.
                // https://github.com/google/protorpc/blob/9c0854e147e774e574327dc12f1042167a5ace6e/protorpc/wsgi/service.py#L91
                method: "POST",  
                contentType: "application/json",

                success: function(data, status, xhr) {
                    console.log('Backbone sync' + method
                                + ' success: ' + JSON.stringify(data));
                    // The default Backbone success method.
                    // It populates the model with attributes from the JSON body..
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
