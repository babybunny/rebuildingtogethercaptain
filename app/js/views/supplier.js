define(
    ['backbone', 'backform', 'bootstrap', 'jquery',
     'text!app/templates/supplier.html'],
    function(Backbone, Backform, bootstrap, jquery, template) {
        var fields = [{
            name: "id", // The key of the model attribute
            label: "ID", // The label to display next to the control
            control: "input", // This will be converted to InputControl and instantiated from the proper class under the Backform namespace
            disabled: true // By default controls are editable. Here we disabled it.
        }, {
            name: "name",
            label: "Name",
            control: "input"
        }, {
            name: "address",
            label: "Address",
            control: "input",
            extraClasses: ["fancy"],
            helpMessage: "Full address like 123 Main Street, Big City CA, 95050"
        }, {
            control: "button",
            label: "Save changes"
        }];

        var SupplierView = Backbone.View.extend({
            el: '#supplier-view',
            template: _.template(template),
            
            events: {
                'click #supplier-save': 'save'
            },
            
            initialize: function(app, loading) {
                var self = this;
                console.log('supplier view init');
                this.app = app;
                self.loading = loading;
                self.saved = false;
                this.listenTo(this.app.models.supplier, 'change',
                              function() {
                                  console.log('supplier change');
                                  self.loading = false;
                                  this.render();
                              });
                self.form = new Backform.Form({
                    model: this.app.models.supplier,
                    fields: fields,
                    events: {
                        'submit': function(e) {
                            console.log('submit supplier backform');
                            e.preventDefault();
                            res = this.model.save();
                            if (res) {
                                res.done(function(result) {
                                    self.saved = true;
                                    self.render();
                                });
                                res.fail(function(error) {
                                    alert(error);
                                });
                            }
                            return false;
                        }
                    }
                });
            },
            
            render: function() {                
                var t = this.template({s: this.app.models.supplier.attributes});
                this.$el.html(t);
                if (this.loading) {
                    this.$('#supplier-loading').show();
                    this.$('#supplier-loaded').hide();
                    this.$('#supplier-backform').hide();
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
                    this.$('#supplier-backform').show();
                }
                this.form.setElement(this.$el.find('#supplier-backform'));
                this.form.render();
                return this;
            },
            
            save: function() {
                console.log('saving supplier');
                this.app.models.supplier.save();
            }
        });
        
        return SupplierView;
    }
);
