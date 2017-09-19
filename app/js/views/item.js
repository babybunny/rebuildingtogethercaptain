define(
    [
        'app/views/rooms_form',
	    'app/views/model_select_control',
        'app/models/supplier_choices',
        'app/models/ordersheet_choices',
        'text!app/templates/simple_form.html'
    ],
    function(RoomFormView, ModelSelectControl,
             SupplierChoices, OrderSheetChoices, template) {
        var fields = [
            {
                name: "id",
                label: "ID",
                control: "input",
                    disabled: true
            },
            {
                name: "bar_code_number",
                label: "Bar code number",
                control: "input",
                    type: "text"
            },
            {
                name: "name",
                label: "Name",
                control: "input",
                    type: "text"
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
                    type: "text"
            },
            {
                name: "description",
                label: "Description",
                control: "input",
                    type: "text"
            },
            {
                name: "measure",
                label: "Measure",
                control: "select",
                options: [
                    {label: "", value: ""},
                    {label: "Bag", value: "Bag"},
                    {label: "Board", value: "Board"},
                    {label: "Bottle", value: "Bottle"},
                    {label: "Box", value: "Box"},
                    {label: "Bundle", value: "Bundle"},
                    {label: "Cartridge", value: "Cartridge"},
                    {label: "Drop-off", value: "Drop-off"},
                    {label: "Each", value: "Each"},
                    {label: "Gallon", value: "Gallon"},
                    {label: "Home", value: "Home"},
                    {label: "Other", value: "Other"},
                    {label: "Pair", value: "Pair"},
                    {label: "Roll", value: "Roll"},
                    {label: "Section", value: "Section"},
                    {label: "Sheet", value: "Sheet"},
                    {label: "Sq. Yds.", value: "Sq. Yds."},
                    {label: "Ton", value: "Ton"},
                    {label: "Tub", value: "Tub"},
                    {label: "Tube", value: "Tube"},
                    {label: "Yard", value: "Yard"}
                ]
            },
            {
                name: "unit_cost",
                label: "Unit cost ($)",
                control: "input"
            },
            {
                name: "must_be_returned",
                label: "Must be returned",
                control: "select",
                options: [
                    {label: "No", value: "No"},
                    {label: "Yes", value: "Yes"},
                ],
            },
            {
                name: "picture",
                label: "Picture",
                control: "input",
                    type: "file"
            },
            {
                name: "thumbnail",
                label: "Thumbnail",
                control: "input",
                    type: "file"
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
                    type: "text"
            },
            {
                name: "url",
                label: "Url",
                control: "input"
            },
            {
                name: "supports_extra_name_on_order",
                label: "Supports extra name on order",
		            control: "checkbox"
            },
            {
                id: "submit",
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
