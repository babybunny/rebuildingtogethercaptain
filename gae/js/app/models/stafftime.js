define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/cru_api.stafftime_',
	          must_be_floats: ['hours', 'miles'],
              defaults: {
                  state: "new"
              }
        });

        return Model;
    }
);
