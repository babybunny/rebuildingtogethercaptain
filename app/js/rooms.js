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
            console.log('ROOMS - SYNCCC!!!');
            var url = this.urlRoot + method;  // Example: '/wsgi_service.captain_' + 'create'
            console.log('Backbone sync ' + method + ' start: ' + url);
            console.log(options);
            // Template for a ROOMS API settings.
            var settings = {
                url: url,

                // Protorpc always sends a POST and expects JSON, it's not RESTful.
                // https://github.com/google/protorpc/blob/9c0854e147e774e574327dc12f1042167a5ace6e/protorpc/wsgi/service.py#L91
                method: "POST",
                dataType: 'json',
                contentType: "application/json",

                success: function(data, status, xhr) {
                    console.log('Backbone sync ' + method
                                + ' success: ' + JSON.stringify(data));
                    xhr.statusText = method;
                    options.success(data, method, xhr);
                }
            };

            var error = options.error;
            settings.error = function(xhr, textStatus, errorThrown) {
                console.log('Backbone sync ' + method + ' error: ' + JSON.stringify('response: ' + xhr.responseText));
                options.textStatus = textStatus;
                options.errorThrown = errorThrown;
                if (error) error.call(options.context, xhr, textStatus, errorThrown);
            };

            switch (method) {
            case 'read':
                var xhr = options.xhr = Backbone.$.ajax(_.extend(settings, {
                    data: JSON.stringify({"id": model.id})
                }))
                break;
            case 'create':
            case 'update':
                var xhr = options.xhr = Backbone.$.ajax(_.extend(settings, {
                    data: JSON.stringify(model.attributes),
                }))
                break;
            }
            model.trigger('request', model, xhr, options);
            return xhr;
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
