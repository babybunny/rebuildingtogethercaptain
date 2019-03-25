define(
    ['backbone'],
    function(Backbone) {
        var Model = Backbone.Model.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/staffposition_api.staffposition_',
            defaults: {
                hourly_rates: [],
                mileage_rates: []
            }
        });
        return Model;
    }
);
