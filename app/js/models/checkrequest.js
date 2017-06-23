define(
    ['backbone', 'underscore'],
    function(Backbone, _) {
        var Model = Backbone.Model.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/wsgi_service.checkrequest_',
	    validate: function(attrs, options) {
		var self = this;
		_.each(['food_amount', 'materials_amount', 'labor_amount'],
		       function(f) {
			   if (! self.get(f) ) {
			       self.set(f, 0);
			   }
		       });
	    }
        });
        
        return Model;
    }
);
