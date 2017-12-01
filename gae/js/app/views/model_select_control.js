define(
    ['backform'],
    function(Backform) {
	      var ModelSelectControl = Backform.SelectControl.extend({
	          initialize: function() {
		            Backform.SelectControl.prototype.initialize.apply(this, arguments);
		            var self = this;
		            var ModelModule = this.field.get('room_model_module');
		            var modl = new ModelModule();
		            this.field.set('room_model', modl);  // just for debugging
		            modl.on('change', function(m) {
		                var new_options = _.map(m.get('choice'), function(e) {
                        return {label: e.label, value: e.id};
                    });
		                new_options.unshift({label: '--- please select one ---',
                                         value: null});
		                self.field.set('options', new_options);
		                self.render().$el.find('label.control-label:contains("*")').addClass('required');
		            });
		            modl.fetch();
	          },
	          render: function() {
		            return Backform.SelectControl.prototype.render.apply(this, arguments);
	          }
	      });
	      return ModelSelectControl;
    }
);
