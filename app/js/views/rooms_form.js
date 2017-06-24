define(
    ['backbone', 'backform', 'bootstrap'],
    function(Backbone, Backform, bootstrap) {

	// options: name, template, model, loading, fields
	var SimpleFormView = Backbone.View.extend({
            el: '#simple-form-view',
            events: {
                'click #simple-form-save': 'save'
            },
            initialize: function(options) {
                var self = this;
                console.log('simple-form view init');
		this.options = options;
                self.template = _.template(options.template);
                self.model = options.model;
                self.name = options.name;
                self.loading = options.loading;
                self.saved = false;
                this.listenTo(this.model, 'change',
                              function() {
                                  console.log(name + ' change');
                                  if (self.loading){
                                    self.loading = false;
                                    this.render();
                                }
                              });
		this.initialize_form(options.fields);
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
                    this.firstfield = this.getFirstField();
                    this.form.setElement(this.$el.find('#simple-form-backform'));
                    this.form.render();
                    this.$(this.firstfield.control + '[name=' + this.firstfield.name +']').focus();
                }
                return this;
            },
            getFirstField: function() {
                var field_list = _.reject(this.form.fields.models, function(model) { return model.get('disabled'); });
                return field_list[0]._previousAttributes;
            },
            save: function() {
                console.log('saving simple-form');
                this.model.save();
            }
        });
        return SimpleFormView;
    }
);
