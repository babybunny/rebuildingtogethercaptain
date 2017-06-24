define(
    [
        'app/views/rooms_form',
	'app/views/model_select_control',
        'app/models/supplier_choices',
        'app/models/ordersheet_choices',
        'text!app/templates/simple_form.html'
    ],
    function(RoomFormView, ModelSelectControl, SupplierChoices, OrderSheetChoices, template) {
        var fields = [
            {
                name: "id", // The key of the model attribute
                label: "ID", // The label to display next to the control
                control: "input", // This will be converted to InputControl and instantiated from the proper class under the Backform namespace
                disabled: true // By default controls are editable. Here we disabled it.
            },
            // boilerplate
            {
                name: "name",
                label: "Name",
                control: "input",
            },
            {
                name: "bar_code_number",
                label: "Bar code number",
                control: "input",
            },
            {
                name: "unit_cost",
                label: "Unit cost",
                control: "input",
            },
            {
                name: "measure",
                label: "Measure",
                control: "select",
                options: [
                    {label: "Box", value: "Box"},
                    {label: "", value: ""},
                    {label: "Yard", value: "Yard"},
                    {label: "Cartridge", value: "Cartridge"},
                    {label: "Sq. Yds.", value: "Sq. Yds."},
                    {label: "Tube", value: "Tube"},
                    {label: "Bundle", value: "Bundle"},
                    {label: "Drop-off", value: "Drop-off"},
                    {label: "Bag", value: "Bag"},
                    {label: "Gallon", value: "Gallon"},
                    {label: "Ton", value: "Ton"},
                    {label: "Board", value: "Board"},
                    {label: "Bottle", value: "Bottle"},
                    {label: "Each", value: "Each"},
                    {label: "Pair", value: "Pair"},
                    {label: "Sheet", value: "Sheet"},
                    {label: "Tub", value: "Tub"},
                    {label: "Home", value: "Home"},
                    {label: "Other", value: "Other"},
                    {label: "Roll", value: "Roll"},
                    {label: "Section", value: "Section"},
                ]
            },
            {
                name: "must_be_returned",
                label: "Must be returned",
                control: "select",
                options: [
                    {label: "Yes", value: "Yes"},
                    {label: "No", value: "No"},
                ]
            },
            {
                name: "url",
                label: "Url",
                control: "input",
            },
            {
                name: "supports_extra_name_on_order",
                label: "Supports extra name on order",
		control: "checkbox",
            },
            {
                name: "appears_on_order_form",
                label: "Appears on order form",
		control: ModelSelectControl,
		room_model_module: OrderSheetChoices,
            },
            {
                name: "order_form_section",
                label: "Order form section",
                control: "input",
            },
            {
                name: "supplier",
                label: "Supplier",
		control: ModelSelectControl,
		room_model_module: SupplierChoices,
            },
            {
                name: "supplier_part_number",
                label: "Supplier part number",
                control: "input",
            },
            {
                name: "description",
                label: "Description",
                control: "input",
            },
            {
                control: "button",
                label: "Save changes"
            }
        ];
        
        var ViewFactory = function(app, loading) {
            return new RoomFormView({
		name: 'item',
		template: template,
		model: app.models.item,
		loading: loading,
		fields: fields,
	    });
        }
        return ViewFactory;
    }
)
