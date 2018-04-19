// A model base class the plays nice with protorpc API.

define(
    ['backbone', 'underscore'],
    function(Backbone, _) {
        var Model = Backbone.Model.extend({
            // matches first part of method name in @remote.method
            // Derived class must implement.
	          // urlRoot: '/cru_api.checkrequest_',

	          // List of attributes that must be floating point numbers.
	          // Empty string becomes zero.
	          // must_be_floats: ['food_amount', 'materials_amount', 'labor_amount'],
	          must_be_floats: [],

	          // Validation method, as described by Backforms.
	          // Derived class may implement this to do more model-specific validation.
	          // But be sure to call validate_protorpc().
	          validate: function(attrs, options) {
		            this.validate_protorpc(attrs, options);
	          },

	          // Make sure stuff that model values are compatible
            // with their protorpc definitions.
	          // Add general stuff here.

	          validate_protorpc: function(attrs, options) {

		            var self = this;


		            // Don't allow empty string for floats.
		            _.each(this.must_be_floats,
		                   function(f) {
 	                         if (! self.get(f) ) {
			                         self.set(f, 0);
			                     }
                             else {
                                 this.f = parseFloat(String(self.get(f)).replace(/,/g, ''));
                                 self.set(f, this.f);
                                 }
		                   });
	          }
        });

        return Model;
    }
);
