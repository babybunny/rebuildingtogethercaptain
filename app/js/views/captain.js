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
            {
                name: "rooms_id",
                label: "Rooms id",
                control: "input",
                type: "text"
            },
            {
                name: "name",
                label: "Name",
                control: "input"
            },
            {
                name: "email",
                label: "Email",
                control: "input",
                type: "email"
            },
            {
                name: "phone_mobile",
                label: "Phone mobile",
                control: "input",
                type: "text"
            },
            {
                name: "phone_work",
                label: "Phone work",
                control: "input",
                type: "text"
            },
            {
                name: "phone_home",
                label: "Phone home",
                control: "input",
                type: "text"
            },
            {
                name: "phone_fax",
                label: "Phone fax",
                control: "input",
                type: "text"
            },
            {
                name: "phone_other",
                label: "Phone other",
                control: "input",
                type: "text"
            },
            {
                name: "tshirt_size",
                label: "Tshirt size",
                control: "select",
                options: [
                    {label: "--------", value: ""},
                    {label: "Small", value: "Small"},
                    {label: "Medium", value: "Medium"},
                    {label: "Large", value: "Large"},
                    {label: "X-Large", value: "X-Large"},
                    {label: "2XL", value: "2XL"},
                    {label: "3XL", value: "3XL"},
                ]
            },
            {
                name: "notes",
                label: "Notes",
                control: "textarea"
            },
            {
                id: "submit",
                label: "Save changes",
                control: "button"

            },

        ];

        var ViewFactory = function(app, loading) {
            return new RoomFormView({
		            name: 'captain',
		            template: template,
		            model: app.models.captain,
		            loading: loading,
		            fields: fields,
	          });
        }
        return ViewFactory;
    }
)
