define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/wsgi_service.item_',
            must_be_floats: ['unit_cost'],
            defaults: {must_be_returned: "No", "supports_extra_name_on_order": false},
            check_url: function(url){
                var patt = new RegExp("(http://.|https://.)");
                var res = patt.test(url);
                return res
            },
            validate: function(attrs, options) {
                	if (!attrs.name) {
                   		this.errorModel.set({name: "Please enter a unique name for this item."})
                	}
                    if(attrs.url && !this.check_url(attrs.url)){
                        this.errorModel.set({url: "Please enter a url."})
                    }
                    if (!_.isEmpty(_.compact(this.errorModel.toJSON()))) {
                    		return "Validation errors. Please fix.";
                	}
            	}

        });

        return Model;
    }
);
