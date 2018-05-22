/*
Custom javascript stuff goes here
*/

//Need to configure port for AJAX calls. Default is port 8000 on same host as html
var HOST = window.location.hostname;
var PORT = '8000';
var DEBUG_MODE = true;

$('#query_results').on('hidden.bs.collapse', function () {
  $('#qr_indicator').removeClass('fa-minus');
  $('#qr_indicator').addClass('fa-plus');
})

$('#query_results').on('shown.bs.collapse', function () {
  $('#qr_indicator').removeClass('fa-plus');
  $('#qr_indicator').addClass('fa-minus');
})

$('#metadata').on('hidden.bs.collapse', function () {
  $('#m_indicator').removeClass('fa-minus');
  $('#m_indicator').addClass('fa-plus');
})

$('#metadata').on('shown.bs.collapse', function () {
  $('#m_indicator').removeClass('fa-plus');
  $('#m_indicator').addClass('fa-minus');
})

$('#submit').click(function() {
  var jqxhr_query = $.ajax({
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
      if(DEBUG_MODE) {
        console.log(jqxhr_query);
        console.log(data);
      }
      if (data.message === 'success'){
        $('#qr_indicator').parent().removeClass('alert-danger');
        $('#query_result_text').html('<pre>' + data.response + '</pre>');
      }
      else{
        $('#qr_indicator').parent().addClass('alert-danger');
        var response = '<p>Error encountered while attempting to get synthetic data. See browser console for additional details.</p>';
        response += '<p>Query submitted:</p>';
        response += '<pre>' + data.query + '</pre>';
        $('#query_result_text').html(response);
        console.log(data.response);
      }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
      console.log('error encountered attempting to get synthetic data' + textStatus + errorThrown);
      $('#qr_indicator').parent().addClass('alert-danger');
      $('#query_result_text').html('Error encountered while attempting to get synthetic data. See browser console for additional details.');
    });

})

$('#reset').click(function() {
  editor.setValue(editor_default_text);
  editor.focus(); //To focus the ace editor
  var n = editor.getSession().getValue().split('\n').length; // To count total no. of lines
  editor.gotoLine(n); //Go to end of document
  $('#qr_indicator').parent().removeClass('alert-danger');
  $('#query_result_text').html('Type a query and hit submit to see results here.');
})

var editor = ace.edit('editor');
var editor_default_text = '-- Type SQL Code here\n';
editor.setTheme('ace/theme/crimson_editor');
editor.session.setMode('ace/mode/sql');

editor.setOptions({
  fontSize: '13px'
});
$('#reset').click();

$( document ).ready(function() {
  // Get Synthesis Methods
  var jqxhr_synthesis = $.ajax({
    dataType: 'json',
    url: 'http://' + HOST + ':' + PORT + '/synthesis_methods'})
    .done(function(data) {
      if(DEBUG_MODE) {
        console.log(jqxhr_synthesis);
        console.log(data);
      }
      if (data.response.constructor === Array) {
        data.response.forEach(function(m, index){
          if(DEBUG_MODE)
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
      $('#errorModal').modal('show');
    });

  // populate Database Metadata field
  // Get Synthesis Methods
  var jqxhr_metadata = $.ajax({
    dataType: 'json',
    url: 'http://' + HOST + ':' + PORT + '/metadata'})
    .done(function(data) {
      if(DEBUG_MODE) {
        console.log(jqxhr_metadata);
        console.log(data);
      }
      if (data.response.constructor === Array) {
        data.response.forEach(function(r, index){
          if (DEBUG_MODE)
            console.log(r);
          $('#metadata_text').append('<pre>' + r + '</pre>');
        });
      }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
      console.log('error encountered attempting to get metadata');
      $('#errorModal').modal('show');
    });
});
