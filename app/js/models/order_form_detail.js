// The details of an order form, including its sheet attributes and all the items.
define(
    ['backbone'],
    function(Backbone) {
        var Collection = Backbone.Model.extend({
            urlPinned: '/wsgi_service.order_form_detail',
        });
        
        return Collection;
    }
);
