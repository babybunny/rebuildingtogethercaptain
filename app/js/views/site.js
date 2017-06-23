define(
    [
        'app/views/simple_form',
        'app/models/jurisdiction_choices',
        'text!app/templates/simple_form.html'
    ],
    function(SimpleFormView, JurisdictionChoices, template) {
        var fields = [
            {
                name: "id", // The key of the model attribute
                label: "ID", // The label to display next to the control
                control: "input", // This will be converted to InputControl and instantiated from the proper class under the Backform namespace
                disabled: true // By default controls are editable. Here we disabled it.
            },
            // boilerplate
            {
                name: "number",
                label: "Number",
                control: "input",
		required: true,
            },
            {
                name: "name",
                label: "Name",
                control: "input",
            },
            {
                name: "applicant",
                label: "Applicant",
                control: "input",
            },
            {
                name: "street_number",
                label: "Street number",
                control: "input",
            },
            {
                name: "city_state_zip",
                label: "City state zip",
                control: "input",
            },
            {
                name: "applicant_email",
                label: "Applicant email",
                control: "input",
            },
            {
                name: "applicant_mobile_phone",
                label: "Applicant mobile phone",
                control: "input",
            },
            {
                name: "applicant_home_phone",
                label: "Applicant home phone",
                control: "input",
            },
            {
                name: "applicant_work_phone",
                label: "Applicant work phone",
                control: "input",
            },
            {
                name: "sponsor",
                label: "Sponsor",
                control: "input",
            },
            {
                name: "scope_of_work",
                label: "Scope of work",
                control: "textarea",
            },
            {
                name: "rating",
                label: "Rating",
                control: "input",
            },
            {
                name: "rrp_level",
                label: "Rrp level",
                control: "input",
            },
            {
                name: "photo_link",
                label: "Photo link",
                control: "input",
            },
            {
                name: "rrp_test",
                label: "Rrp test",
                control: "input",
            },
            {
                name: "roof",
                label: "Roof",
                control: "input",
            },
            {
                name: "announcement_subject",
                label: "Announcement subject",
                control: "input",
            },
            {
                name: "volunteer_signup_link",
                label: "Volunteer signup link",
                control: "input",
            },
            {
                name: "jurisdiction_choice",
                label: "Jurisdiction choice",
                control: "select",
                // "jurisdiction_choice is a Key.  TODO",
            },
            {
                name: "announcement_body",
                label: "Announcement body",
                control: "textarea",
            },
            {
                name: "budget",
                label: "Budget",
                control: "input",
            },
            {
                control: "button",
                label: "Save changes"
            }
        ];
        
        var ViewFactory = function(app, loading) {
            var simpleform = new SimpleFormView('site', template, app.models.site, loading);
            app.models.jurisdiction_choices = app.models.jurisdiction_choices || new JurisdictionChoices();
            app.models.jurisdiction_choices.on('change', function(m) {
                stanza = _.find(fields, function(f) { return f.name == 'jurisdiction_choice' });
                stanza.options = _.map(m.get('choice'), function(e) { return {'label': e.label, 'value': e.id}; });                
                if (stanza.options) {
                    // stanza.value = _.head(stanza.options).value;
                    console.log('popped ' + stanza.value);
                }
                _.each(fields, function(f) {
                    if (!app.models.site.get(f.name)) {
                        console.log(f.name, f.value)
                        app.models.site.set(f.name, f.value);
                    }
                });
                simpleform.initialize_form(fields);
                simpleform.render();
            });
            app.models.jurisdiction_choices.fetch();
            return simpleform;
        }
        return ViewFactory;
        var ViewFactory = function(app, loading) {
            return new SimpleFormView('site', template, app.models.site, loading, fields)
        }
        return ViewFactory;
    }
)
