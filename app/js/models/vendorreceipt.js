define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/wsgi_service.vendorreceipt_',
	          must_be_floats: ['amount'],
        });
        
        return Model;
    }
);