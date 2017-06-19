define(
    ['backbone', 'backform', 'bootstrap'],
    function(Backbone, Backform, bootstrap) {
        var SimpleFormView = Backbone.View.extend({
            el: '#simple-form-view',            
            events: {
                'click #simple-form-save': 'save'
            },
            
            initialize: function(name, template, model, loading, fields) {
                var self = this;
                console.log('simple-form view init');
                self.template = _.template(template),
                self.model = model;
                self.name = name;
                self.loading = loading;
                self.saved = false;
                this.listenTo(this.model, 'change',
                              function() {
                                  console.log(name + ' change');
                                  self.loading = false;
                                  this.render();
                              });
                if (fields) {
                    this.initialize_form(fields);
                }
            },

            initialize_form: function(fields) {
                this.form = new Backform.Form({
                    model: this.model,
                    fields: fields,
                    events: {
                        'submit': function(e) {
                            console.log(name + ' submit backform');
                            e.preventDefault();
                            res = this.model.save();
                            if (res) {
                                res.done(function(result) {
                                    this.saved = true;
                                    this.render();
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
                var t = this.template({name: this.name,
                                       s: this.model.attributes});
                this.$el.html(t);
                if (this.loading) {
                    this.$('#simple-form-loading').show();
                    this.$('#simple-form-loaded').hide();
                    this.$('#simple-form-backform').hide();
                    this.$('#simple-form-new').hide();                        
                } else {
                    this.$('#simple-form-loading').hide();
                    this.$('#simple-form-new').hide();                        
                    if (this.model.has('id')) {
                        this.$('#simple-form-loaded').show();
                        this.$('#simple-form-new').hide();
                    } else {
                        this.$('#simple-form-loaded').hide();
                        this.$('#simple-form-new').show();                        
                    }
                    this.$('#simple-form-backform').show();
                }
                if (this.form) {
                    this.form.setElement(this.$el.find('#simple-form-backform'));
                    this.form.render();
                }
                return this;
            },
            
            save: function() {
                console.log('saving simple-form');
                this.model.save();
            }
        });
        
        return SimpleFormView;
    }
)
