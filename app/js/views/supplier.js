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
                name: "since",
                label: "Since",
                control: "input",
                    type: "date",
                    format: "yyyy-mm-dd",
                    disabled: true
            },
            {
                name: "name",
                label: "Name",
                control: "input",
                    type: "text",
                    required: true
            },
            {
                name: "email",
                label: "Email",
                control: "input",
                    type: "email"
            },
            {
                name: "address",
                label: "Address",
                control: "input",
                    type: "text"
            },
            {
                name: "phone1",
                label: "Phone1",
                control: "input",
                    type: "text"
            },
            {
                name: "phone2",
                label: "Phone2",
                control: "input",
                    type: "text"
            },
            {
                name: "notes",
                label: "Notes",
                control: "textarea"
            },
            {
                name: "active",
                label: "Active",
                control: "select",
                options: [
                    {label: "Active", value: "Active"},
                    {label: "Inactive", value: "Inactive"},
                ]
            },
            {
                name: "visibility",
                label: "Visibility",
                control: "select",
                options: [
                    {label: "Everyone", value: "Everyone"},
                    {label: "Staff Only", value: "Staff Only"},
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
                name: 'supplier',
		            template: template,
		            model: app.models.supplier,
		            loading: loading,
		            fields: fields,
            });
        }
        return ViewFactory;
    }
)
