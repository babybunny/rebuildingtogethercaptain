// details for the (hourly,mileage) rates associated with a staffposition.
define(
    ['backbone', 'app/models/rate_after_date'], function(Backbone, RateAfterDate) {

        var Collection = Backbone.Collection.extend({
            model: RateAfterDate,
            comparator: 'date',

        });
        return Collection;
    }
);
