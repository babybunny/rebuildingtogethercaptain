define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/wsgi_service.checkrequest_',
	          must_be_floats: ['food_amount', 'materials_amount', 'labor_amount'],

              validate: function(attrs, options){
                    if(!attrs.payment_date){
                      this.errorModel.set({payment_date: "Please include a payment date for your checkrequest."})
                	}
                    if(!attrs.description){
                        this.errorModel.set({description: " "})
                    }
                    if(!attrs.name){
                        this.errorModel.set({name: "Please include a name for your checkrequest."})
                    }
                    if (!_.isEmpty(_.compact(this.errorModel.toJSON()))) {
                    		return "Validation errors. Please fix.";
                	}
              }

        });

        return Model;
    }
);
