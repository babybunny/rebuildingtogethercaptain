define(
    ['jquery-ui',
     'text!app/templates/staff_home.html'
    ],
    function(unused_jquery, template) {
        var StaffView = Backbone.View.extend({
            el: '#main-content',
            template: _.template(template),
            render: function() {
                console.log('at staff home');
                this.$el.html(this.template({
                    program_selected: '',
                    jurisdictions: [],
                    order_sheets: []
                }));
                return this;
            }
        });
        
        return StaffView;
    }
);
