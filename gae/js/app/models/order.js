define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/cru_api.order_',
            must_be_floats: ['sub_total', 'actual_total'],
        });

        return Model;
    }
);
