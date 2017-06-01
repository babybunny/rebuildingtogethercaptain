define(
    ['text!app/templates/auth.html', 'text!app/templates/welcome_auth.html'],
    function(template, welcome_template) {
        var AuthView = Backbone.View.extend({
            el: '#signed-in-container',
            template: _.template(template),
            welcome_template: _.template(welcome_template),
            
            events: {
                'click #signin-button': 'signin',
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
                if (state) {
                    this.$('#signin-button').hide();
                    this.$('#signout-button').show();
                } else {
                    this.$('#signin-button').show();
                    this.$('#signout-button').hide();
                }
                return this;
            },
            
            render_welcome: function() {
                var state = this.app.apiManager.loginState.get('state');
                console.log('rendering welcome with state: ' + state + ' and email: '
                            + this.app.apiManager.loginState.get('email'));
                var t = this.welcome_template({
                    email: this.app.apiManager.loginState.get('email')
                });
                this.$el.html(t);
                if (state) {
                    this.$('#signin-button').hide();
                    this.$('#signout-button').show();
                } else {
                    this.$('#signin-button').show();
                    this.$('#signout-button').hide();
                }
                return this;
            },
            signin: function() {
                this.app.apiManager.handleSignin();
                return false;
            },
            signout: function() {
                console.log('signing out');
                this.app.apiManager.handleSignout();
                return false;
            }
        });
        
        return AuthView;
    }
);
