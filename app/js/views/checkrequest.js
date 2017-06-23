define(
    [
        'bootstrap-datepicker',
        'app/views/simple_form',
        'app/models/staffposition_choice',
        'text!app/templates/simple_form.html'
    ],
    function(bsdp, SimpleFormView, CaptainChoice, template) {
        var fields = [
            {
                name: "id", // The key of the model attribute
                label: "ID", // The label to display next to the control
                control: "input", // This will be converted to InputControl and instantiated from the proper class under the Backform namespace
                disabled: true // By default controls are editable. Here we disabled it.
            },
            // boilerplate
            {
                name: "site",
                label: "Site",
                control: "input", 
                disabled: true 
            },
            {
                name: "state",
                label: "State",
                control: "select",
                options: [
                    {label: "fulfilled", value: "fulfilled"},
                    {label: "new", value: "new"},
                    {label: "deleted", value: "deleted"},
                    {label: "submitted", value: "submitted"},
                    {label: "payable", value: "payable"},
                ]
            },
            {
                name: "name",
                label: "Name",
                control: "input",
            },
            {
                name: "address",
                label: "Address",
                control: "textarea",
            },
            {
                name: "tax_id",
                label: "Tax id",
                control: "input",
            },
            {
                name: "form_of_business",
                label: "Form of business",
                control: "select",
                options: [
                    {label: "Corporation", value: "Corporation"},
                    {label: "Sole Proprietor", value: "Sole Proprietor"},
                    {label: "Partnership", value: "Partnership"},
                    {label: "Don't Know", value: "Don't Know"},
                ]
            },
            {
                name: "payment_date",
                label: "Payment date",
                control: "datepicker",
                options: {format: "yyyy-mm-dd"},
            },
            {
                name: "captain",
                label: "Captain",
                control: "select",
                // "captain is a Key.  TODO",
            },
            {
                name: "materials_amount",
                label: "Materials amount",
                control: "input",
            },
            {
                name: "labor_amount",
                label: "Labor amount",
                control: "input",
            },
            {
                name: "food_amount",
                label: "Food amount",
                control: "input",
            },
            {
                name: "description",
                label: "Description",
                control: "textarea",
            },
            {
                control: "button",
                label: "Save changes"
            }
        ];
        
        var ViewFactory = function(app, loading) {
            return new SimpleFormView('checkrequest', template, app.models.checkrequest, loading, fields)
        }
        return ViewFactory;
    }
)
