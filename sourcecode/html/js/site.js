/*
Custom javascript stuff goes here
*/
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
  // need to make ajax call with this text:
  console.log(editor.getValue());
})

$('#reset').click(function() {
  editor.setValue(editor_default_text);
  editor.focus(); //To focus the ace editor
  var n = editor.getSession().getValue().split("\n").length; // To count total no. of lines
  editor.gotoLine(n); //Go to end of document
})

var editor = ace.edit("editor");
var editor_default_text = '-- Type SQL Code here\n';
editor.session.setMode("ace/mode/sql");
editor.setOptions({
  fontSize: "13px"
});
$('#reset').click();
