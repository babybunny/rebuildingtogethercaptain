define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            must_be_floats: ['rate'],

            rate_after_date: function(){
                return {rate: this.get('rate'), date: this.get('date')};
            },
            getRates: function(staffposition, submit=false){
                if(submit){
                    staffposition.get(this.rateType).push(this.rate_after_date());
                }
                return staffposition.get(this.rateType);
            },
            initialize: function(app, name){
                var self = this;
                this.rateType = name + 'rates';
                this.getRates = this.getRates.bind(self, app.models.staffposition);

                this.listenTo(app.models.staffposition, 'submit',
                    function(mdl, changed){
                        mdl.set(self.rateType, self.getRates(true));
                    });
                this.listenTo(app.models.staffposition, 'change:'.concat(name).concat('rate'),
                    function(mdl, changed){
                        self.set('rate', changed);
                        self.validate_protorpc();
                    });
                this.listenTo(app.models.staffposition, 'change:'.concat(name).concat('date'),
                    function(mdl, changed){
                        self.set('date', changed);
                    });
            }

        });

        return Model;
    }
);
