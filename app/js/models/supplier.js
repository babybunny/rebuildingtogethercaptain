define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/wsgi_service.supplier_',

            // This has the effect of setting the form defaults, too.
            defaults: {
                active: "Active",
                visibility: "Everyone"
            }
        });

        return Model;
    }
);
