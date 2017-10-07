// The items and quantities associated with an order.
define(
    ['backbone'],
    function(Backbone) {
        var Collection = Backbone.Collection.extend({
            // no URL - this is browser-side only.
            model: Backbone.Model.extend({
                idAttribute: 'item'
            }),                
        });
        
        return Collection;
    }
);
