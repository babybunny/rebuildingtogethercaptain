define(
    ['backbone'],
    function(Backbone) {
        var Model = Backbone.Model.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/choices_api.captain_for_site_choices_',
	    getApiInputs: function(){
		return {id: this.get('parent').get('site')}
	    }
        });
        
        return Model;
    }
);
