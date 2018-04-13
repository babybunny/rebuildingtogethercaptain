define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/cru_api.staffposition_',
            must_be_floats: ['hourly_rate', 'mileage_rate']
        });

        return Model;
    }
);
