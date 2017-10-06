define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/cru_api.inkinddonation_',
	          must_be_floats: ['labor_amount', 'materials_amount'],
        });

        return Model;
    }
);
