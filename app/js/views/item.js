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
            {
                control: "button",
                label: "Save changes"
            },
            # boilerplate
            {
                name: "picture",
                label: "Picture",
            # "picture is a BlobProperty, skipping",
            }
            {
                name: "description",
                label: "Description",
                control: "input",
            }
            {
                name: "bar_code_number",
                label: "Bar code number",
                control: "input",
            }
            {
                name: "unit_cost",
                label: "Unit cost",
                control: "input",
            }
            {
                name: "appears_on_order_form",
                label: "Appears on order form",
                # "appears_on_order_form is a Key.  TODO",
            }
            {
                name: "must_be_returned",
                label: "Must be returned",
                control: "input",
            }
            {
                name: "measure",
                label: "Measure",
                control: "input",
            }
            {
                name: "last_editor",
                label: "Last editor",
                # "last_editor is a UserProperty('last_editor').  TODO",
            }
            {
                name: "name",
                label: "Name",
                control: "input",
            }
            {
                name: "created",
                label: "Created",
                # "created is a DateTimeProperty('created', auto_now_add=True).  TODO",
            }
            {
                name: "supplier_part_number",
                label: "Supplier part number",
                control: "input",
            }
            {
                name: "modified",
                label: "Modified",
                # "modified is a DateTimeProperty('modified', auto_now=True).  TODO",
            }
            {
                name: "url",
                label: "Url",
                control: "input",
            }
            {
                name: "supports_extra_name_on_order",
                label: "Supports extra name on order",
                # "supports_extra_name_on_order is a BooleanProperty('supports_extra_name_on_order', default=False).  TODO",
            }
            {
                name: "order_form_section",
                label: "Order form section",
                control: "input",
            }
            {
                name: "supplier",
                label: "Supplier",
                # "supplier is a Key.  TODO",
            }
            {
                name: "thumbnail",
                label: "Thumbnail",
            # "thumbnail is a BlobProperty, skipping",
            }
        ];
        
        var ViewFactory = function(app, loading) {
            return new SimpleFormView(fields, 'item', template, app.models.item, loading)
        }
        return ViewFactory;
    }
)
