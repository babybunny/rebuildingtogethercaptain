define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/cru_api.staffposition_',
            defaults: {
                hourly_rates: {rate: 0.0, date: ""},
                mileage_rates:{rate: 0.0, date: ""}
            },
            parse: function(response, options){
                if (response.hourly_rates){
                    response.hourly_rates = response.hourly_rates[response.hourly_rates.length-1];
                }
                if (response.mileage_rates){
                    response.mileage_rates = response.mileage_rates[response.mileage_rates.length-1];
                }
                return response
            },
            must_be_floats: ['hourly_rate', 'mileage_rate']
        });

        return Model;
    }
);
