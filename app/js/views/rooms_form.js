define(
    ['backbone', 'backform', 'bootstrap'],
    function(Backbone, Backform, bootstrap) {

        // options: name, template, model, loading, fields
        var RoomFormView = Backbone.View.extend({
            el: '#simple-form-view',
            events: {'click button:submit': 'submit'},
            initialize: function(options) {
                var self = this;
                this.options = options;
                self.template = _.template(options.template);
                self.model = options.model;
                self.name = options.name;
                self.loading = options.loading;
                self.saved = false;

                this.listenTo(this.model, 'change',
                              function(model) {
                                  if ( self.loading ) {
                                      self.loading = false;
                                      this.render();
                                  }
                              });
                var onSave = function() {
                    self.model.save(null, {
                        'success': function(model, attrs, response) {
                            response.xhr.statusText = 'SAVED';
                            $('span.status')
                                .css('color', '#409b27')
                                .text('Saved')
                                .show()
                                .fadeOut({
                                    duration: 1000,
                                    complete: function() {
                                        // redirect to the "back to site" URL
                                        window.location = $('#rooms-form-after-save').attr('href');
                                    }
                                });
                        },
                        'error': function(model, response, error) {
                            $('span.status')
                                .css('color', 'red')
                                .text('Error: ' + response.responseText)
                                .show();
                        },
                    });
                };

                this.form = new Backform.Form({
                    model: this.model,
                    fields: options.fields,
                    events: {
                        'submit': function(e) {
                            e.preventDefault();
                            this.statusText = e.statusText;
                            console.log( self.name,' submit backform');
                            if (!self.model.isValid()){
                                $('span.status').text(self.model.validationError).css('color', '#a94442');
                            }
                            else{
                                onSave();
                            }
                        },

                    },
                });
            },
            render: function() {
                var t = this.template({
                    name: this.name,
                    s: this.model.attributes
                });
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
                    this.$(this.firstfield.control + '[name=' + this.firstfield.name +']')
                        .focus();
                    this.$('button').on('mousedown mouseup', function() {
                        $(this).toggleClass('white');
                    });

                }
                return this;
            },
            getFirstField: function() {
                var field_list = _.reject(
                    this.form.fields.models,
                    function(model) { return model.get('disabled'); }
                );
                return field_list[0]._previousAttributes;
            },

        });
        return RoomFormView;
    }
);
