// The items and quantities associated with an order.
define(
    ['backbone', 'app/models/sitecaptain'],
    function(Backbone, SiteCaptainModel) {
        var Collection = Backbone.Collection.extend({
            urlPinned: '/wsgi_service.sitecaptains_for_site',
            model: SiteCaptainModel,
            initialize: function(site_id) {
                this.site_id = site_id;
            },
            parse: function(response, options) {
                return response.sitecaptain;
            },            
            getApiInputs: function() {
                return {id: this.site_id}
            }
        });
        return Collection;
    }
);
