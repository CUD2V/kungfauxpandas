/*
Custom javascript stuff goes here
*/

//Need to configure port for AJAX calls. Default is port 8000 on same host as html
var HOST = window.location.hostname;
var PORT = '8000';

$('#query_results').on('hidden.bs.collapse', function () {
  console.log('caught hidden event');
  $('#qr_indicator').removeClass('fa-minus');
  $('#qr_indicator').addClass('fa-plus');
})

$('#query_results').on('shown.bs.collapse', function () {
  console.log('caught shown event');
  $('#qr_indicator').removeClass('fa-plus');
  $('#qr_indicator').addClass('fa-minus');
})

$('#metadata').on('hidden.bs.collapse', function () {
  console.log('caught hidden event');
  $('#m_indicator').removeClass('fa-minus');
  $('#m_indicator').addClass('fa-plus');
})

$('#metadata').on('shown.bs.collapse', function () {
  console.log('caught shown event');
  $('#m_indicator').removeClass('fa-plus');
  $('#m_indicator').addClass('fa-minus');
})

$('#submit').click(function() {
  console.log('Called submit click.')

  var jqxhr = $.ajax({
    dataType: 'json',
    type: 'GET',
    url: 'http://' + HOST + ':' + PORT + '/synthesize_data',
    data: {
      query: editor.getValue(),
      method: 'kde'
    }
  })
    .done(function(data) {
      // need to add elements to query result area...
      // create columns
      // populate rows
      console.log(jqxhr);
      console.log(data);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
      console.log('error encountered attempting to get synthetic data');
    });

})

$('#reset').click(function() {
  editor.setValue(editor_default_text);
  editor.focus(); //To focus the ace editor
  var n = editor.getSession().getValue().split('\n').length; // To count total no. of lines
  editor.gotoLine(n); //Go to end of document
})

var editor = ace.edit('editor');
var editor_default_text = '-- Type SQL Code here\n';
editor.setTheme('ace/theme/crimson_editor');
editor.session.setMode('ace/mode/sql');

editor.setOptions({
  fontSize: '13px'
});
$('#reset').click();

// Assign handlers immediately after making the request,
// and remember the jqXHR object for this request
var jqxhr = $.ajax({
  dataType: 'json',
  url: 'http://' + HOST + ':' + PORT + '/synthesis_methods'})
  .done(function(data) {
    // need to add elements to UI...
    console.log(jqxhr);
    console.log(data);
    if (data.response.constructor === Array) {
      data.response.forEach(function(m, index){
        console.log(m);
        var html_to_append = '<div class="form-check form-check-inline"><input class="form-check-input" type="radio" name="selected_method" id="'
        html_to_append += 'selected_method' + index + '"';
        if (m === 'kde')
          html_to_append += 'value="' + m + '" checked>';
        else {
          html_to_append += 'value="' + m + '">';
        }
        html_to_append += '<label class="form-check-label" for="inlineRadio1">' + m + '</label></div>';
        $('#synthesis_methods').append(html_to_append);
      });
    }
  })
  .fail(function(jqXHR, textStatus, errorThrown) {
    console.log('error encountered attempting to get data synthesis methods');
  });
