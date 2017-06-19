define(
    [
        'app/views/simple_form',
        'app/models/supplier_choices',
        'text!app/templates/simple_form.html'
    ],
    function(SimpleFormView, SupplierChoices, template) {
        var fields = [
            {
                name: "id", // The key of the model attribute
                label: "ID", // The label to display next to the control
                control: "input", // This will be converted to InputControl and instantiated from the proper class under the Backform namespace
                disabled: true // By default controls are editable. Here we disabled it.
            },
            // boilerplate
            {
                name: "code",
                label: "Code",
                control: "input",
            },
            {
                name: "name",
                label: "Name",
                control: "input",
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
                name: "logistics_instructions",
                label: "Logistics instructions",
                control: "textarea",
            },
            {
                name: "delivery_options",
                label: "Delivery options",
                control: "select",
                options: [
                    {label: "Yes", value: "Yes"},
                    {label: "No", value: "No"},
                ]
            },
            {
                name: "default_supplier",
                label: "Default supplier",
                control: "select",
            },

            {
                name: "retrieval_options",
                label: "Retrieval options",
                control: "select",
                options: [
                    {label: "Yes", value: "Yes"},
                    {label: "No", value: "No"},
                ]
            },
/* TODO     {
                name: "supports_extra_name_on_order",
                label: "Supports extra name on order",
                // "supports_extra_name_on_order is a BooleanProperty('supports_extra_name_on_order', default=False).  TODO",
            },
*/            {
                name: "pickup_options",
                label: "Pickup options",
                control: "select",
                options: [
                    {label: "Yes", value: "Yes"},
                    {label: "No", value: "No"},
                ]
            },
            {
                name: "instructions",
                label: "Instructions",
                control: "textarea",
            },
            {
                control: "button",
                label: "Save changes"
            }
        ];
        
        var ViewFactory = function(app, loading) {
            var simpleform = new SimpleFormView('ordersheet', template, app.models.ordersheet, loading);
            app.models.supplier_choices = app.models.supplier_choices || new SupplierChoices();
            app.models.supplier_choices.on('change', function(m) {
                stanza = _.find(fields, function(f) { return f.name == 'default_supplier' });
                stanza.options = _.map(m.get('choice'), function(e) { return {'label': e.label, 'value': e.id}; });                
                simpleform.initialize_form(fields);
                simpleform.render();
            });
            app.models.supplier_choices.fetch();
            return simpleform;
        }
        return ViewFactory;
    }
)
