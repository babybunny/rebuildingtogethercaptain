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
            {
                name: "number",
                label: "Number",
                control: "input",
		            required: true,
                    helpMessage: "\"10001DAL\" reads: 2010, #001, Daly City"
                    // in future autogenerate number
            },
            {
                name: "program",
                label: "Program",
                control: "input",
                    type: "text"
            },
            {
                name: "name",
                label: "Recipient Name",
                control: "input",
                    type: "text"
            },
            {
                name: "applicant",
                label: "Applicant Contact",
                control: "input",
                    type: "text"
            },
            {
                name: "applicant_home_phone",
                label: "Applicant home phone",
                control: "input",
                    type: "text"
            },
            {
                name: "applicant_work_phone",
                label: "Applicant work phone",
                control: "input",
                    type: "text"
            },
            {
                name: "applicant_mobile_phone",
                label: "Applicant mobile phone",
                control: "input",
                    type: "text"
            },
            {
                name: "applicant_email",
                label: "Applicant email",
                control: "input",
                    type: "email"
            },
            {
                name: "rating",
                label: "Rating",
                control: "input",
                    type: "text"
            },
            {
                name: "roof",
                label: "Roof",
                control: "input",
                    type: "text"
            },
            {
                name: "rrp_test",
                label: "Rrp test",
                control: "input",
                    type: "text"
            },
            {
                name: "rrp_level",
                label: "Rrp level",
                control: "input",
                    type: "text"
            },
            {
                name: "jurisdiction",
                label: "Jurisdiction",
                control: "input",
                    type: "text"
            },
            {
                name: "jurisdiction_choice",
                label: "Jurisdiction choice",
                    control: ModelSelectControl,
                    room_model_module: JurisdictionChoices,
            },
            {
                name: "scope_of_work",
                label: "Scope of work",
                control: "textarea",
            },
            {
                name: "sponsor",
                label: "Sponsor",
                control: "input",
                    type: "text"
            },
            {
                name: "street_number",
                label: "Street Address",
                control: "input",
                    type: "text",
                    helpMessage: "Full street address like 960 Main Street, Apt 4"
            },
            {
                name: "city_state_zip",
                label: "City State Zip",
                control: "input",
                    helpMessage: "City State Zip, like Menlo Park CA 94025"
            },
            {   // ndb.IntegerProperty
                name: "budget",
                label: "Budget",
                control: "input",
                    type: "number"
            },
            {
                name: "announcement_subject",
                label: "Announcement subject",
                control: "input",
                    type: "text"
            },
            {
                name: "announcement_body",
                label: "Announcement body",
                control: "textarea"
            },
            {
                name: "photo_link",
                label: "Photo link",
                control: "input",
                    type: "text",
                    helpMessage: "example: https://www.flickr.com/gp/rebuildingtogetherpeninsula/UX22iM/"
            },
            {
                name: "volunteer_signup_link",
                label: "Volunteer signup link",
                control: "input",
                    type: "text",
                    helpMessage: "http://rebuildingtogetherpeninsula.force.com/GW_Volunteers__VolunteersJobListingFS?&CampaignID=701U0000000rnvU"
            },
            {
                name: "latest_computed_expenses",
                label: "Latest Compted Expenses",
                control: "input"
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
