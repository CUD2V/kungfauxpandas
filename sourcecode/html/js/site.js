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
  // check to make sure a query has been entered before submitting.
  var filtered_input = $.trim(editor.getValue().replace(/-- Type SQL Code here/g,''));
  if ((filtered_input.length <= 14) ||
      (filtered_input === '-- Type SQL Code here')) {
        return;
  }

  // reset query result area and show loading indicator
  // need to remove which ever is showing fa-plus or fa-minus
  // then set back at the end
  if ($('#qr_indicator').hasClass('fa-plus')) {
    restore_class = 'fa-plus';
    $('#qr_indicator').removeClass('fa-plus');
  }
  else {
    restore_class = 'fa-minus';
    $('#qr_indicator').removeClass('fa-minus');
  }

  $('#qr_indicator').addClass("fa-spinner fa-pulse");
  $('#query_result_text').html('<p>Loading Results</p>');
  $('#download_link').empty();
  $('#qr_indicator').parent().removeClass('alert-danger');

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
        $('#query_result_text').html('<pre id="response_table">' + data.response + '</pre>');
        $('thead').addClass('thead-light');
        // build link to download csv data
        // had to add event.stopPropagation() to prevent card from collapsing/expanding
        $('#download_link').append('<a href="data:text/csv;charset=utf-8,'
          + escape(data.csv)
          + '" onclick="event.stopPropagation();" download="query_results.csv">query_results.csv</a>')
      }
      else{
        $('#qr_indicator').parent().addClass('alert-danger');
        var response = '<p>Error encountered while attempting to get synthetic data.</p>';
        response += '<pre class="alert alert-warning">' + data.response + '</pre>';
        response += '<p>Query submitted:</p>';
        response += '<pre>' + data.query + '</pre>';
        $('#query_result_text').html(response);
      }
      $('#qr_indicator').removeClass("fa-spinner fa-pulse");
      $('#qr_indicator').addClass(restore_class);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
      console.log('error encountered attempting to get synthetic data' + textStatus + errorThrown);
      $('#qr_indicator').parent().addClass('alert-danger');
      $('#query_result_text').html('Error encountered while attempting to get synthetic data. See browser console for additional details.');
      $('#qr_indicator').removeClass("fa-spinner fa-pulse");
      $('#qr_indicator').addClass(restore_class);
    });
})

$('#reset').click(function() {
  editor.setValue(editor_default_text);
  editor.focus(); //To focus the ace editor
  var n = editor.getSession().getValue().split('\n').length; // To count total no. of lines
  editor.gotoLine(n); //Go to end of document
  $('#qr_indicator').parent().removeClass('alert-danger');
  $('#query_result_text').html('Type a query and hit submit to see results here.');
  $('#download_link').empty();
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
