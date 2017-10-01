define(
    [
        'app/views/rooms_form',
        'text!app/templates/simple_form.html'
    ],
    function(RoomFormView, template) {
        var fields = [
            {
                name: "id",
                label: "ID",
                control: "input",
                disabled: true
            },
            // boilerplate
            {
                name: "site",
                label: "Site",
                // "site is a Key.  TODO",
            },
            {
                name: "captain",
                label: "Captain",
                // "captain is a Key.  TODO",
            },
            {
                name: "type",
                label: "Type",
                control: "select",
                options: [
                    {label: "Volunteer", value: "Volunteer"},
                    {label: "Construction", value: "Construction"},
                    {label: "Team", value: "Team"},
                ]
            },
            {
                id: "submit",
                control: "button",
                label: "Save changes"
            }
        ];
        
        var ViewFactory = function(app, loading) {
            return new RoomFormView({
		            name: 'sitecaptain',
		            template: template,
		            model: app.models.sitecaptain,
		            loading: loading,
		            fields: fields,
	          });
        }
        return ViewFactory;
    }
)
