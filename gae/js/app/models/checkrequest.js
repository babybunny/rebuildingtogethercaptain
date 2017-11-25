define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/cru_api.checkrequest_',
	          must_be_floats: ['food_amount', 'materials_amount', 'labor_amount'],
              defaults: { state: "new" }
        });

        return Model;
    }
);
