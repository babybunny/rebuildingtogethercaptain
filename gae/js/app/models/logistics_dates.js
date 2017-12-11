// Logistics dates for orders on a site.
define(
    ['backbone'],
    function(Backbone) {
        var Collection = Backbone.Collection.extend({
            urlPinned: '/custom_api.logistics_dates',
            initialize: function(site_id) {
                this.site_id = site_id;
            },
            parse: function(response, options) {
                return response.logistics_date;
            },            
            getApiInputs: function() {
                return {id: this.site_id}
            }
        });
        return Collection;
    }
);
