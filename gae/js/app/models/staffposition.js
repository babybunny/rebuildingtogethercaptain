define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/cru_api.staffposition_',
            must_be_floats: ['hourly_rate', 'mileage_rate'],

            validate: function(){
                ProtoModel.prototype.validate.apply(this);

                this.attributes.hourly_rates['rate'] = this.get('hourly_rate');
                this.attributes.mileage_rates['rate'] = this.get('mileage_rate');

                this.set({ hourly_rates: this.attributes.hourly_rates,
                          mileage_rates: this.attributes.mileage_rates });
            },

            defaults: {
                hourly_rates: [],
                mileage_rates: []
            }
        });

        return Model;
    }
);
