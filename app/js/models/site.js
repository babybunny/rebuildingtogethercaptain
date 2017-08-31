define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/wsgi_service.newsite_',
            must_be_floats: ['latest_computed_expenses'],

            defaults: {
                budget: 0,
                announcement_subject: "Nothing Needs Attention",
                announcement_body: "Pat yourself on the back - no items need attention.\n"+
                                            "You have a clean bill of health."
                }
        });

        return Model;
    }
);
