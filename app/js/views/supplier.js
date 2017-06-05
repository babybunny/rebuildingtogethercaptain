define(
    ['backbone',
     'text!app/templates/supplier.html'],
    function(Backbone, template) {
        var SupplierView = Backbone.View.extend({
            el: '#supplier-view',
            template: _.template(template),
            
            events: {
                'click #save-button': 'save'
            },
            
            initialize: function(app, loading) {
                var self = this;
                console.log('supplier view init');
                this.app = app;
                self.loading = loading;
                this.listenTo(this.app.models.supplier, 'change',
                              function() {
                                  console.log('supplier change');
                                  self.loading = false;
                                  this.render();
                              });
            },
            
            render: function() {
                
                var t = this.template({s: this.app.models.supplier.toJSON()});
                this.$el.html(t);
                if (this.loading) {
                    this.$('#supplier-loading').show();
                    this.$('#supplier-loaded').hide();
                    this.$('#supplier-form').hide();
                    this.$('#supplier-new').hide();                        
                } else {
                    this.$('#supplier-loading').hide();
                    this.$('#supplier-new').hide();                        
                    if (this.app.models.supplier.has('id')) {
                        this.$('#supplier-loaded').show();
                        this.$('#supplier-new').hide();
                    } else {
                        this.$('#supplier-loaded').hide();
                        this.$('#supplier-new').show();                        
                    }
                    this.$('#supplier-form').show();
                }
                return this;
            },
            
            save: function() {
                console.log('saving supplier');
                this.sync();
            }
        });
        
        return SupplierView;
    }
);
