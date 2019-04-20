// StaffPosition (hourly or mileage) rate and start date.
define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            must_be_floats: ['rate'],
            idAttribute: "cid",

            validate: function(attrs){
                this.errorModel.clear();

                if (!attrs.date){
                    this.errorModel.set({date: "Date is required"});
                }
                if (!attrs.rate){
                    this.errorModel.set({rate: "Rate is required"});
                }
                if (!_.isEmpty(_.compact(this.errorModel.toJSON()))) {
                    return "Validation errors. Please fix.";
                }
            }

        });

        return Model;
    }
);
