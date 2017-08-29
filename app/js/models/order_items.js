// The items and quantities associated with an order.
define(
    ['backbone'],
    function(Backbone) {
        var Collection = Backbone.Collection.extend({
            urlPinned: '/wsgi_service.order_items',
        });
        
        return Collection;
    }
);
