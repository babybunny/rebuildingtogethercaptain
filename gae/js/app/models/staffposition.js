define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/cru_api.staffposition_',

            validate: function(attrs){
                this.errorModel.clear();

                if(attrs.hourly_rate || attrs.hourly_date){
                    this.set('hourly_update', {rate: this.get('hourly_rate'), date: this.get('hourly_date')})
                    if(!attrs.hourly_rate){
                        this.unset('hourly_update');
                        this.errorModel.set({hourly_rate: "Please set an Hourly (new rate)."});
                    }
                    else if(!attrs.hourly_date){
                        this.unset('hourly_update');
                        this.errorModel.set({hourly_date: "Please enter an Hourly (start date)."})
                    }
                }
                if(attrs.mileage_rate || attrs.mileage_date){
                    this.set('mileage_update', {rate: this.get('mileage_rate'), date: this.get('mileage_date')})
                    if(!attrs.mileage_rate){
                        this.unset('mileage_update');
                        this.errorModel.set({mileage_rate: "Please set a Mileage (new rate)."});
                    }
                    else if(!attrs.mileage_date){
                        this.unset('mileage_update');
                        this.errorModel.set({mileage_date: "Please enter a Mileage (start date)."})
                    }
                }
                if (!_.isEmpty(_.compact(this.errorModel.toJSON()))) {
                    return "Validation errors. Please fix.";
                }
            },
        });

        return Model;
    }
);
