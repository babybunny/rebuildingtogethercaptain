define(
    ['backbone',
     'text!app/templates/auth.html'],
    function(Backbone, template) {
        var AuthView = Backbone.View.extend({
            el: '#auth-view',
            template: _.template(template),
            
            events: {
                'click #signout-button': 'signout'
            },
            
            initialize: function(app) {
                this.app = app;
                this.listenTo(this.app.apiManager.loginState,
                              'change:state change:email', this.render);
            },
            
            render: function() {
                var state = this.app.apiManager.loginState.get('state');
                console.log('rendering auth with state: ' + state + ' and email: '
                            + this.app.apiManager.loginState.get('email'));
                var t = this.template({
                    email: this.app.apiManager.loginState.get('email')
                });
                this.$el.html(t);
                return this;
            },
            
            signout: function() {
                console.log('signing out');
                this.app.apiManager.handleSignout();
                var loc = window.location;
                // Go to /, which will redirect users who are logged in.
                var new_loc = loc.protocol + '//' + loc.host + '/';
                window.location = new_loc;                
                return false;
            }
        });
        
        return AuthView;
    }
);
