module.exports = function(grunt) {
  grunt.initConfig({
          exec: {
              build: {
                  command: 'node node_modules/requirejs/bin/r.js -o require-config.js'
              }
          }
      });
  
  grunt.loadNpmTasks('grunt-exec');
  
  grunt.registerTask('copy-require', function() {
    grunt.file.mkdir('gae/js/lib');
    grunt.file.mkdir('gae/css/lib');
    grunt.file.copy('node_modules/requirejs/require.js', 'gae/js/lib/require.js');
    grunt.file.copy('node_modules/requirejs-text/text.js', 'gae/js/lib/text.js');
    grunt.file.copy('node_modules/backbone/backbone.js', 'gae/js/lib/backbone.js');
    grunt.file.copy('node_modules/backbone/backbone-min.js', 'gae/js/lib/backbone-min.js');
    grunt.file.copy('node_modules/underscore/underscore.js', 'gae/js/lib/underscore.js');
    grunt.file.copy('node_modules/underscore/underscore-min.js', 'gae/js/lib/underscore-min.js');
    grunt.file.copy('node_modules/jquery/dist/jquery.min.js', 'gae/js/lib/jquery.js');
    grunt.file.copy('node_modules/jqueryui/jquery-ui.min.js', 'gae/js/lib/jquery-ui.js');
    grunt.file.copy('node_modules/backform/src/backform.js', 'gae/js/lib/backform.js');
    grunt.file.copy('node_modules/bootstrap/dist/css/bootstrap.css', 'gae/css/lib/bootstrap.css');
    grunt.file.copy('node_modules/bootstrap/dist/css/bootstrap.css.map', 'gae/css/lib/bootstrap.css.map');
    grunt.file.copy('node_modules/bootstrap/dist/js/bootstrap.min.js', 'gae/js/lib/bootstrap.js');
    grunt.file.copy('node_modules/bootstrap-datepicker/dist/css/bootstrap-datepicker3.standalone.css', 'gae/css/lib/bootstrap-datepicker.css');
    grunt.file.copy('node_modules/bootstrap-datepicker/dist/js/bootstrap-datepicker.min.js', 'gae/js/lib/bootstrap-datepicker.js');
  });
  
  grunt.registerTask('default', ['copy-require']);
};
