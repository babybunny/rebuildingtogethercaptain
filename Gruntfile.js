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
    grunt.file.mkdir('app/js/lib');
    grunt.file.copy('node_modules/requirejs/require.js', 'build/js/lib/require.js');
    grunt.file.copy('node_modules/requirejs-text/text.js', 'build/js/lib/text.js');
    grunt.file.copy('node_modules/backbone/backbone-min.js', 'build/js/lib/backbone-min.js');
    grunt.file.copy('node_modules/backbone/backbone.js', 'build/js/lib/backbone.js');
    grunt.file.copy('node_modules/underscore/underscore-min.js', 'build/js/lib/underscore-min.js');
    grunt.file.copy('node_modules/jquery/dist/jquery.min.js', 'build/js/lib/jquery.js');
    grunt.file.copy('node_modules/jqueryui/jquery-ui.min.js', 'build/js/lib/jquery-ui.js');
    grunt.file.copy('node_modules/backform/src/backform.js', 'build/js/lib/backform.js');
    grunt.file.copy('node_modules/bootstrap/dist/css/bootstrap.css', 'build/css/bootstrap.css');
    grunt.file.copy('node_modules/bootstrap/dist/js/bootstrap.min.js', 'build/js/lib/bootstrap.js');
  });
  
  grunt.registerTask('default', ['copy-require']);
};
