define(
    [
        'backbone',
        'app/models/site', 'app/models/sitecaptains_for_site',
        'app/views/site', 'app/views/sitecaptain',
        'text!app/templates/site_form.html'
    ],
    function(Backbone, SiteModel, SiteCaptainsForSite,
             SiteView, SiteCaptainView, SiteFlowTemplate){
        var View = Backbone.View.extend({
            el: '#simple-form-view',
            initialize: function(app, site_id) {
                console.log('initializing site_flow');
                var self = this;
                this.app = app;  // TODO: obsolete and remove this
                this.site_id = parseInt(site_id);
                var name = 'site';
                self.app.models[name] = new SiteModel({id: this.site_id});
                self.app.models[name].fetch();
                this.site_view = new SiteView(app, true);

                var sitecaptains = new SiteCaptainsForSite(this.site_id);
                sitecaptains.fetch().then(function() {
                    self.sitecaptain_view = new SiteCaptainView({
                        sitecaptains: sitecaptains,
                        site_id: self.site_id,
                    })
                    self.render();
                });                   
                this.t = _.template(SiteFlowTemplate);
                this.render();
            },
            render: function() {
                this.$el.html(this.t());
                console.log('site_flow render');
                this.site_view.setElement(this.$('#site-form'));
                this.site_view.render();
                if (this.sitecaptain_view) {
                    this.sitecaptain_view.setElement(this.$('#sitecaptains'));
                    this.sitecaptain_view.render();
                }
            }
        });
        return View;
    }
)
