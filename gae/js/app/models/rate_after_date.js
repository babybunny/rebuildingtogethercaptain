define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            must_be_floats: ['rate'],
            idAttribute: "cid",
            validate: function(attrs){
                this.errorModel.clear();
                if (!attrs.type){
                    this.errorModel.set({type: "Type is required"});
                }
                if(!attrs.rate) {
                    this.errorModel.set({rate: "Rate is required"});
                }
                if(!attrs.date) {
                    this.errorModel.set({date: "Date is required"});
                }
                if (!_.isEmpty(_.compact(this.errorModel.toJSON()))) {
                    return "Validation errors. Please fix.";
                }
            }

        });

        return Model;
    }
);
