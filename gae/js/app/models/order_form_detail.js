// The details of an order form, including its sheet attributes and all the items.
define(
    ['backbone'],
    function(Backbone) {
        var Collection = Backbone.Model.extend({
            urlPinned: '/custom_api.order_form_detail',
        });
        
        return Collection;
    }
);
