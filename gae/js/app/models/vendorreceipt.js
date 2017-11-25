define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/cru_api.vendorreceipt_',
	          must_be_floats: ['amount'],

              defaults: {
                  state: "new",
                  description: ""
                //   added description so users dont see None
              }
        });

        return Model;
    }
);
