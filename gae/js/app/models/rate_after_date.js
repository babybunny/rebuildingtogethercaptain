define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            must_be_floats: ['rate'],
            idAttribute: "cid"

        });

        return Model;
    }
);
