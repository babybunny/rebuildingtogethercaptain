// Corresponds to the order fields that are written when an order is submitted.
define(
    ['backbone'],
    function(Backbone) {
        return Backbone.Model.extend({
            urlRoot: '/custom_api.order_full_',
        });
    }
);
