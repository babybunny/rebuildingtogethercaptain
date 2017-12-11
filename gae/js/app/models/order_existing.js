// Existing Orders for a Site and OrderSheet.
define(
    ['backbone'],
    function(Backbone) {
        var Collection = Backbone.Collection.extend({
            urlPinned: '/custom_api.order_existing',
            initialize: function(site_id, ordersheet_id) {
                this.site_id = site_id;
                this.ordersheet_id = ordersheet_id;
            },
            parse: function(response, options) {
                return response.order;
            },            
            getApiInputs: function() {
                return {site_id: this.site_id, ordersheet_id: this.ordersheet_id}
            }
        });
        return Collection;
    }
);
