define(
    [
        'app/views/rooms_form',
	      'app/views/model_select_control',
        'app/models/jurisdiction_choices',
        'text!app/templates/simple_form.html'
    ],
    function(RoomFormView, ModelSelectControl, JurisdictionChoices, template) {
        var fields = [
            {
                name: "id",
                label: "ID",
                control: "input",
                disabled: true
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
		            control: ModelSelectControl,
		            room_model_module: JurisdictionChoices,
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
                id: "submit",
                control: "button",
                label: "Save changes"
            }
        ];
        
        var ViewFactory = function(app, loading) {
            return new RoomFormView({
		            name: 'site',
		            template: template,
		            model: app.models.site,
		            loading: loading,
		            fields: fields,
	          });
        }
        return ViewFactory;
    }
)
