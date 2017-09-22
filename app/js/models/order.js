define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/wsgi_service.order_',
            must_be_floats: ['sub_total', 'actual_total'],

            defaults: {reconciliation_notes: ""},

            validate: function(attrs){
                if (!attrs.site) {
                   this.errorModel.set({site: "Please go back and associate a site with this order."})
                }
                if (!attrs.order_sheet){
                    this.errorModel.set({order_sheet: "Please go back and associate an order sheet with this order."})
                }
                if (!_.isEmpty(_.compact(this.errorModel.toJSON()))) {
                    return "Validation errors. Please fix.";
                }
            }
        });

        return Model;
    }
);
