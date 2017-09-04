define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/wsgi_service.stafftime_',
	          must_be_floats: ['hours', 'miles'],
              defaults: {
                  state: "new",
                  hours: 0.0,
                  miles: 0.0,
                  description: "",
                  modified: new Date()
              }
        });

        return Model;
    }
);
