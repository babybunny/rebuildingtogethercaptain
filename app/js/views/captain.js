define(
    [
        'app/views/simple_form',
        'text!app/templates/simple_form.html'
    ],
    function(SimpleFormView, template) {
        var fields = [
            {
                name: "id", // The key of the model attribute
                label: "ID", // The label to display next to the control
                control: "input", // This will be converted to InputControl and instantiated from the proper class under the Backform namespace
                disabled: true // By default controls are editable. Here we disabled it.
            },
            // boilerplate
            {
                name: "rooms_id",
                label: "Rooms id",
                control: "input",
            },
            {
                name: "name",
                label: "Name",
                control: "input",
            },
            {
                name: "email",
                label: "Email",
                control: "input",
            },
            {
                name: "tshirt_size",
                label: "Tshirt size",
                control: "input",
            },
            {
                name: "phone_mobile",
                label: "Phone mobile",
                control: "input",
            },
            {
                name: "phone_home",
                label: "Phone home",
                control: "input",
            },
            {
                name: "phone_fax",
                label: "Phone fax",
                control: "input",
            },
            {
                name: "phone_work",
                label: "Phone work",
                control: "input",
            },
            {
                name: "phone_other",
                label: "Phone other",
                control: "input",
            },
            {
                name: "notes",
                label: "Notes",
                control: "textarea",
            },
            {
                control: "button",
                label: "Save changes"
            }
        ];
        
        var ViewFactory = function(app, loading) {
            return new SimpleFormView('captain', template, app.models.captain, loading, fields)
        }
        return ViewFactory;
    }
)
