// The order forms that are available for creating an order.
define(
    ['backbone'],
    function(Backbone) {
        var Collection = Backbone.Collection.extend({
            urlPinned: '/custom_api.order_form_choices',
            parse: function(response, options) {
                return response.order_form;
            },            
        });
        
        return Collection;
    }
);
