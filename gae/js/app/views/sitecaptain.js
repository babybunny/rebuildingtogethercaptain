define(
    [
        'backbone', 'backform', 'bootstrap',
        'app/models/captain_choices', 'app/models/sitecaptain',
	      'app/views/model_select_control',
        'text!app/templates/sitecaptains.html'
    ],
    function(Backbone, Backform, bootstrap,
             CaptainChoice, SiteCaptainModel,
             ModelSelectControl,
             template) {
        var fields = [
            {
                name: "site",
                label: "Site",
                control: "input",
                disabled: true
            },
            {
                name: "captain",
                label: "Captain",
                control: ModelSelectControl,
                room_model_module: CaptainChoice
            },
            {
                name: "type",
                label: "Type",
                control: "select",
                options: [
                    {label: "--- please select one ---", value: ""},
                    {label: "Volunteer", value: "Volunteer"},
                    {label: "Construction", value: "Construction"},
                    {label: "Team", value: "Team"},
                ]
            },
            {
                id: "submit",
                control: "button",
                name: "addCaptain",
                label: "Add Captain"
            }
        ];

        var View = Backbone.View.extend({
            el: '#sitecaptain-form-view',
            events: {
                'click button.remove-sitecaptain': 'removeCaptain',
                'click button[name=addCaptain]': 'before_save',
            },
            initialize: function(options) {
                this.options = options;
                this.template = _.template(template);
                this.model = new SiteCaptainModel({site: options.site_id});
                this.sitecaptains = options.sitecaptains;
                this.listenTo(this.sitecaptains, 'change', this.render);
                this.makeForm();
            },
            makeForm: function() {
                this.form = new Backform.Form({
                    model: this.model,
                    fields: fields,
                });
            },
            removeCaptain: function(e) {
                // console.log('remove captain ', this, e, e.target.name);
                var m = this.sitecaptains.get(parseInt(e.target.name));
                this.sitecaptains.remove(m);
                m.destroy();
                this.render();
            },
            before_save: function(e){
                e.preventDefault();
                var id_value = Number(this.$el.find('select').val());
                var choices = this.form.fields.models[1].changed.options;
                this.filtered_captain = _.findWhere(choices, {value: id_value});
                this.addCaptain();
            },
            addCaptain: function() {
                console.log('add captain ', this);
                var self = this;
                this.model.save().then(function() {
                    self.model.set({name: self.filtered_captain.label});
                    self.sitecaptains.add(self.model);
                    self.model = new SiteCaptainModel({site: self.options.site_id});
                    self.makeForm();
                    self.render();
                });
            },
            render: function() {
                this.$el.html(this.template({sitecaptains: this.sitecaptains.models}));
                this.form.setElement(this.$el.find('#sitecaptain-form-backform'));
                this.form.render();
                return this;
            }
        });
        return View;
    }
)
