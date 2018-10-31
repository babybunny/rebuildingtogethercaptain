define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/cru_api.inkinddonation_',
	    must_be_floats: ['labor_amount', 'materials_amount'],
        defaults: {
            labor_amount: 0.0,
            materials_amount: 0.0
        },
	    validate: function(attrs, options){
            this.errorModel.clear();
            var msg = "You can not submit an in-kind Donation without a Value. Please add an estimated Value or find out an estimated Value from the source and then submit. Values are very important for our reporting";

            if (!attrs.labor_amount && !attrs.materials_amount){
                this.errorModel.set(
                    {labor_amount: msg, materials_amount: msg});
            }
            else if (this.changed.labor_amount || this.changed.materials_amount) {
                 this.validate_protorpc(attrs, options);
            }
            if (!_.isEmpty(_.compact(this.errorModel.toJSON()))) {
                return "Validation errors. Please fix.";
            }
        }

        });

        return Model;
    }
);
