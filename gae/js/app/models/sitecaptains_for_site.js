// The items and quantities associated with an order.
define(
    ['backbone', 'app/models/sitecaptain'],
    function(Backbone, SiteCaptainModel) {
        var Collection = Backbone.Collection.extend({
            urlPinned: '/custom_api.sitecaptains_for_site',
            model: SiteCaptainModel,
            initialize: function(site_id) {
                this.site_id = site_id;
            },
            parse: function(response, options) {
                return _.map(response.sitecaptain_detail, function(s) {
                    return _.extend(s.sitecaptain, {name: s.name});
                })
            },            
            getApiInputs: function() {
                return {id: this.site_id}
            }
        });
        return Collection;
    }
);
