define(
    ['backbone', 'backform', 'bootstrap'],
    function(Backbone, Backform, bootstrap) {

    // options: name, template, model, loading, fields
    var RoomFormView = Backbone.View.extend({
            el: '#simple-form-view',
            events: {
                'click button:submit': 'submit'
            },
            initialize: function(options) {
                console.log('simple-form view init');
                var self = this;
            this.options = options;
                self.template = _.template(options.template);
                self.model = options.model;
                self.name = options.name;
                self.loading = options.loading;
                self.saved = false;

                this.model.on('sync', function(model, attrs, options) {
                    console.log('SYNC status', options.xhr.statusText, '- VALID', model.isValid());
                    console.log('model ',attrs.id,' has options here!', options);

                    if (options.xhr.statusText == 'SAVED') {
                        self.saved = true;
                        console.log('MODEL SAVED', self.saved);
                    }
                });

                this.listenTo(this.model, 'change',
                              function(model) {
                                    console.log(this.name + ' generic change');
                                    if ( self.loading ) {
                                        console.log('model is loading', self.loading);
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
                            e.preventDefault();
                            this.statusText = e.statusText;
                            console.log( self.name,' submit backform');
                            this.model.save(this.model.toJSON(),{
                                'success': function(model, attrs, response) {
                                    response.xhr.statusText = 'SAVED';
                                    e.statusText = response.xhr.statusText;
                                    console.clear();
                                    console.log('success model', model);
                                    console.log('success attrs', attrs);
                                    console.log('success response', response);
                                    console.log('statusText ', response.xhr.statusText);
                                    $('span.status').css('color', '#409b27').text(e.statusText).show().fadeOut(1000);
                                },
                                'error': function(model, response, error) {
                                    e.statusText = response.statusText;
                                    console.clear();
                                    console.log('error model', model);
                                    console.log('error response Text,', response.responseText);
                                    console.log('error status Text,', response.statusText);
                                    console.log('error', error);
                                    $('span.status').css('color', 'red').text(e.statusText).show().fadeOut(1000);
                                },
                            });
                            console.log(this.statusText);
                        },

                    },

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
                    this.$('button').on('mousedown mouseup', function() {
                        $(this).toggleClass('white');
                    });

                }
                return this;
            },
            getFirstField: function() {
                var field_list = _.reject(this.form.fields.models, function(model) { return model.get('disabled'); });
                return field_list[0]._previousAttributes;
            },

        });
        return RoomFormView;
    }
);
