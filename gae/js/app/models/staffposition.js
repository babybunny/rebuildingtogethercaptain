define(
    ['backbone', 'app/models/staffposition_rate_collection'],
    function(Backbone, Rates) {
        var Model = Backbone.Model.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/staffposition_api.staffposition_',
            defaults: {
                hourly_rates: new Rates(),
                mileage_rates: new Rates()
            },
            parse: function(response){
                response.hourly_rates = new Rates(response.hourly_rates);
                response.mileage_rates = new Rates(response.mileage_rates);
                return response;
            }
        });
        return Model;
    }
);
