define(
    ['backbone', 'backform', 'bootstrap', 'jquery',
     'text!app/templates/staff.html'],
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
            name: "email",
            label: "Email Address",
            control: "input",
            extraClasses: ["fancy"],
            helpMessage: "used to sign in to ROOMS"
        }, {
            name: "notes",
            label: "Notes",
            control: "textarea"
        }, {
            name: "since",
            label: "Since",
            control: "input",
            disabled: true
            
        }, {
            control: "button",
            label: "Save changes"
        }];

        var StaffView = Backbone.View.extend({
            el: '#staff-view',
            template: _.template(template),
            
            events: {
                'click #staff-save': 'save'
            },
            
            initialize: function(app, loading) {
                var self = this;
                console.log('staff view init');
                this.app = app;
                self.loading = loading;
                self.saved = false;
                this.listenTo(this.app.models.staff, 'change',
                              function() {
                                  console.log('staff change');
                                  self.loading = false;
                                  this.render();
                              });
                self.form = new Backform.Form({
                    model: this.app.models.staff,
                    fields: fields,
                    events: {
                        'submit': function(e) {
                            console.log('submit staff backform');
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
                var t = this.template({s: this.app.models.staff.attributes});
                this.$el.html(t);
                if (this.loading) {
                    this.$('#staff-loading').show();
                    this.$('#staff-loaded').hide();
                    this.$('#staff-backform').hide();
                    this.$('#staff-new').hide();                        
                } else {
                    this.$('#staff-loading').hide();
                    this.$('#staff-new').hide();                        
                    if (this.app.models.staff.has('id')) {
                        this.$('#staff-loaded').show();
                        this.$('#staff-new').hide();
                    } else {
                        this.$('#staff-loaded').hide();
                        this.$('#staff-new').show();                        
                    }
                    this.$('#staff-backform').show();
                }
                this.form.setElement(this.$el.find('#staff-backform'));
                this.form.render();
                return this;
            },
            
            save: function() {
                console.log('saving staff');
                this.app.models.staff.save();
            }
        });
        
        return StaffView;
    }
);
