define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/wsgi_service.ordersheet_',

            // not sure if these do anything.
            visibility: 'Everyone',
	          default_supplier: '',
        });
        
        return Model;
    }
);
