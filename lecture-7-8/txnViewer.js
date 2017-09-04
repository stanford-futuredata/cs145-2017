// State of the vars / system
var state;

// The TXNs log
var txnLog;

// Load data from json files
var getTxns = function() {
  d3.json("txnLog.json", function(error, json) {
    if (error) return console.warn(error);
    txnLog = json;

    // Make the viewer once txns data is loaded
    makeViewer();

    // Bind to window resize event as well
    $(window).resize(function() { 
      makeViewer(); 
    });
  });
}
getTxns();

// Fixed parameters
// We fix the width of the transaction boxes
var txnWidth = 175;
var txnHeight = 65;
var txnPadding = 15;
var colors = ['#0099CC', '#FF6666'];
var tableHeaderHeight = 20;


// Render the svg canvas
var makeViewer = function() {
  $("#chart-"+chartNum).html('');

  // Have width be relative to the width of the IPython output subarea width
  var W = $('.output_subarea').width() - 20;
  var canvasProportion = 0.7;
  var canvasWidth = canvasProportion * W;
  var canvasHeight = txnPadding + numThreads * (txnHeight + txnPadding);

  // Set the var table width appropriately
  $('#vals-'+chartNum).width((1 - canvasProportion)*W + 'px');

  // Top spacing (hackey)
  var topMargin = tableHeaderHeight + txnHeight;
  $("#top-spacer-"+chartNum).height(topMargin);
  $("#chart-"+chartNum).css("margin-top", 0);

  // Make the svg canvas
  var svg = d3.select("#chart-"+chartNum)
              .append('svg')
              .attr({
                'width': canvasWidth,
                'height': canvasHeight,
                'x': topMargin
              })
              .style('border', '1px solid black');

  // Populate the timeline with transaction boxes
  makeTxns(svg, canvasWidth, canvasHeight);
}

// Lay out the transition boxes- g with rect + text
// NOTE that the first txn in txnLog is a placeholder (for initial vals)!
var makeTxns = function(svg, canvasWidth, canvasHeight) {
  
  // Make a group for the whole timeline for sliding animation
  var timelineWidth = txnPadding + (txnLog.length - 1) * (txnWidth + txnPadding);
  var dT = -Math.max(timelineWidth - canvasWidth);
  var timeline = svg.append('g')
                    .attr({
                      'id': 'timeline-g-' + chartNum,
                      'transform': 'translate(' + dT + ',0)',
                      'class': 'timeline'});
  
  // Make the timeline i.e. the TXN boxes
  var txns = timeline.selectAll('g.txn')
     .data(txnLog)
     .enter()
     .append('g')
     .attr({
       'id': function(d,i) { return 'txn-' + chartNum + '-' + (i-1); },
       'transform': function(d,i) {
         var x = txnPadding + (i-1) * (txnWidth + txnPadding);
         var y = txnPadding + d.thread * (txnHeight + txnPadding);
         return 'translate(' + x + ',' + y + ')'; },
       'class': 'txn'})
  txns.append('rect')
   .attr({
     'width': txnWidth,
     'height': txnHeight,
     'fill': function(d) { return colors[d.thread % colors.length]; },
     'stroke': 'none'});
  txns.append('text')
   .attr({
      'text-anchor': 'middle',
      'dominant-baseline': 'middle',  // NOTE: doesn't work in IE?
      'dx': 0.5*txnWidth,
      'dy': 0.5*txnHeight,
      'fill': 'white'})
    .text(function(d) { return d.operation; });
  
  // Initialize the state to that of the last txn
  var t = txnLog.length - 1;
  state = txnLog[t].state;

  // Make the slider and state table
  makeTable();
  makeLog(t);
  makeSlider(svg, timeline, timelineWidth, canvasWidth, canvasHeight);
}

var makeSlider = function(svg, timeline, timelineWidth, canvasWidth, canvasHeight) {
  var slider = $("#slider-"+chartNum);
  var line = svg.append('line')
        .attr({
          'class': 'slider-bar',
          'x1': 0,
          'x2': 0,
          'y1': 0,
          'y2': canvasHeight,
          'stroke': '#393D3D',
          'stroke-dasharray': '2,2',
          'opacity': 0.5});
  slider.width(canvasWidth);
  slider.slider();
  slider.slider('option', 'value', slider.slider('option', 'max'));
  slider.off("slide");
  slider.on("slide", function(e,ui) {
    var p = ui.value / 100.0;
    var w = p * canvasWidth;

    // move the slider bar
    line.attr('transform', 'translate(' + w + ',0)');

    // move the timeline
    var dT = -p * Math.max(0, timelineWidth - canvasWidth);
    timeline.attr('transform', 'translate(' + dT + ',0)');

    // Find the index of the last txn that should be active
    var t = 0;
    while (w > t*(txnPadding+txnWidth) + txnPadding + 0.5*txnWidth + dT) {
      t += 1;
    }
    t -= 1;

    // show / hide the txns
    for (var tt=0; tt < txnLog.length; tt++) {
      if (tt <= t) {
        $("#txn-" + chartNum + '-' + tt).css('opacity', 1.0);
      } else {
        $("#txn-" + chartNum + '-' + tt).css('opacity', 0.3);
      }
    }

    // Set the state & re-render the values table appropriately
    if (t >= -1) {
      state = txnLog[t+1].state;
    }
    makeTable();
    makeLog(t+1);
  });
}

var makeTable = function() {
  
  // Make the header row- var names
  var html = '<tr style="height:' + tableHeaderHeight + 'px;"><th></th>';
  for (var v in state) {
    if (state.hasOwnProperty(v)) {
      html += '<th>' + v + '</th>';
    }
  }
  html += '</tr>';

  // Make the local / thread rows
  for (var r=0; r < numThreads + 1; r++) {
    html += '<tr style="height:' + (txnHeight + 0.5*txnPadding) + 'px;">';
    if (r > 0) {
      html += '<th>Thread ' + r + '</th>';
    } else {
      html += '<th>Main</th>';
    }
    for (var v in state) {
      if (state.hasOwnProperty(v)) {
        html += '<td>' + state[v][r] + '</td>';
      }
    }
    html += '</tr>';
  }
  $("#vals-"+chartNum).html(html);
}

var makeLog = function(t) {
  html = "<ul>";
  for (var i=0; i <= t; i++) {
    var l = txnLog[i];
    if (l.var != null) {
      html += "<li>T" + l.thread + " - " + l.var + " : " + l.old + " -\> " + l.new + "</li>";
    }
  }
  $("#log-"+chartNum).html(html + "</ul>");
}
