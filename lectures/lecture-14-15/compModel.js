// Load data from json files
var pagesLog;
var getPagesLog = function() {
  d3.json("pagesLog.json", function(error, json) {
    if (error) return console.warn(error);
    pagesLog = json;

    // Make the animation
    makeComp();

    // Bind to window resize
    //$(window).resize(function() {
    //  makeComp();
    //});
  });
}
getPagesLog();

// Set some globals
var pageWidth = 50 + 20*pageSize; // NOTE: this is hard-coding the font-width!!!
var pageHeight = 30;
var pagePadding = 5;
var frameWidth = pageWidth + 2*pagePadding;
var frameHeight = pageHeight + 2*pagePadding;
var framePadding = 2*pagePadding;

var bufferFrameFill = '#3366FF';
var diskFrameFill = '#B685FF';
var frameStroke = 'white';  // '#C1C0C0'
var diskBackground = '#ABACB0';
var pageColor = 'blue';
var pageHighlightColor = 'red';

var maxDiskSize = 4;  // MAX # of files that can fit in disk
var fileSize;
var height = framePadding + (maxDiskSize + 2) * (framePadding + frameHeight);
var width;

// Create a row of frames
var appendFrameRowTo = function(e, x, y, len, name, label, fill, duration, callback) {
  var frameRow = e.append('g')
                  .attr({
                    'transform': 'translate(' + x + ',' + y + ')',
                    'id': name + '-g'})
                  .style('opacity', 0);
  var frameRange = new Array(len);
  frameRow.append('text')
          .text(label)
        .attr({
          'text-anchor': 'middle',
          'dominant-baseline': 'middle',  // NOTE: doesn't work in IE?
          'dx': 0.5*frameWidth,
          'dy': 0.5*frameHeight});
  frameRow.selectAll('rect.' + name + '-frame')
          .data(frameRange)
          .enter()
          .append('rect')
          .attr({
            'id': function(d,i) { return name + '-frame-' + i; },
            'class': name + '-frame',
            'width': frameWidth,
            'height': frameHeight,
            'x': function(d,i) { return (i+1)*frameWidth; },
            'y': pagePadding,
            'fill': fill,
            'stroke': frameStroke});
  if (duration != null) {
    frameRow.transition()
            .style('opacity', 1)
            .duration(DURATION)
            .each("end", function() { if (callback != null) { callback(); } });
  } else {
    frameRow.style('opacity', 1);
    if (callback != null) { callback(); }
  }
  return frameRow;
}

var diskHeight = function(nFiles) {
  return 2*framePadding + nFiles * (framePadding + frameHeight)
}

// Create the chart
var bufferPages;
var files = [];
var svg;
var buffer;
var disk;
var makeComp = function() {
  $("#chart-"+chartNum).html('');
  
  // Make sure the tooltips are hidden
  $(".tooltip").hide();

  // viewer size
  width = $('.output_subarea').width() - 20;

  // Make the files the max possible size
  // TODO: make files dynamically resizeable?
  fileSize = Math.floor((width - framePadding) / (framePadding + frameWidth) - 2);

  // append svg
  svg = d3.select("#chart-"+chartNum)
          .append('svg')
          .attr({
            'width': width,
            'height': height})
          .style('border', '1px solid black');

  // append buffer
  buffer = appendFrameRowTo(svg, pagePadding, pagePadding, numBufferPages, 'buffer', 'BUFFER', bufferFrameFill, null, null);

  // append disk container
  var diskY = 2*pagePadding + 2*frameHeight;
  disk = svg.append('g')
            .attr({
              'id': 'disk-g',
              'transform': 'translate(' + pagePadding + ',' + diskY + ')'});
  disk.append('text')
      .text('DISK')
      .attr({
        'text-anchor': 'middle',
        'dominant-baseline': 'middle',  // NOTE: doesn't work in IE?
        'dx': 0.5*frameWidth,
        'dy': 0.5*frameHeight});
  disk.append('rect')
      .attr({
        'id': chartNum + '-disk-box',
        'width': width - 2*frameWidth,
        'height': diskHeight(1), // Start w/ space for one file
        'x': frameWidth,
        'y': 0,
        'fill': diskBackground,
        'stroke': 'none'});

  // Animate the page transistions according to the log diff in pagesLog
  var success = takeActions(0);
}

var addFile = function(fileId, duration, callback) {
  var n = files.length;
  if (fileId >= maxDiskSize) {
    return null;
  }
  if (n > 0 && fileId >= n) {
    $("#" + chartNum + "-disk-box").height(diskHeight(n+1));
  }
  var file = appendFrameRowTo(disk, 2*framePadding + frameWidth, framePadding + fileId * (framePadding + frameHeight), fileSize, 'file-' + fileId, 'File ' + fileId, diskFrameFill, duration, callback);
  if (fileId < n) {
    files[fileId] = file;
  } else {
    files.push(file);
  }
}

var removeFile = function(fileId) {
  var file = files[fileId];
  file.remove();
  files[fileId] = null;
  var n = files.length;
  var nh = n;
  if (n > 0) {
    for (var j=n-1; j > 0; j--) {
      if (files[j] != null) {
        break;
      } else {
        nh = j;
      }
    }
    $("#" + chartNum + "-disk-box").height(diskHeight(nh));
  }
}

// For some reason in certain situations e.g. d3.select("#0-0-1")
// d3.select is not working here??  Workaround...
var getElement = function(elementType, filterFn) {
  var e = d3.select('#chart-'+chartNum)
           .selectAll(elementType)[0]
           .filter(filterFn)[0];
  return e;
}

var pageText = function(fid, pid, data) {
  var s = fid + '/' + pid + ' : ';
  for (var i=0; i < data.length; i++) {
    s += (data[i] != null) ? data[i] : '_';
    if (i < data.length - 1) {
      s += ', ';
    }
  }
  return s;
}

var appendPageTo = function(e, a, x, y, opacity, color) {
  var page = e.append('g')
              .attr({
                'id': chartNum + '-' + a.file + '-' + a.page + '-' + a.newLocation,
                'transform': 'translate(' + x + ',' + y + ')',
                'class': 'page'})
              .style('opacity', opacity);
  page.append('rect')
      .attr({
        'id': 'page-' + a.file + '-' + a.page + '-rect',
        'class': 'page',
        'width': pageWidth,
        'height': pageHeight,
        'fill': color,
        'stroke': '#444'});
  page.append('text')
      .attr({
        'dx': pagePadding,
        'dy': 0.5*pageHeight,
        'fill': 'white'})
      .text(pageText(a.file, a.page, a.pageData));
  return page;
}

var getBufferPageAbsPos = function(bufferIndex) {
  var bufferPos = d3.transform(buffer.attr("transform")).translate;
  var x = bufferPos[0] + pagePadding + (bufferIndex + 1) * frameWidth;
  var y = bufferPos[1] + 2 * pagePadding;
  return [x, y];
}

var getFilePageAbsPos = function(file, page) {
  var diskPos = d3.transform(disk.attr("transform")).translate;
  var filePos = d3.transform(files[file].attr("transform")).translate;
  var x = diskPos[0] + filePos[0] + pagePadding + (page + 1) * frameWidth;
  var y = diskPos[1] + filePos[1] + 2 * pagePadding;
  return [x, y];
}

var placeRelativeTo = function(a, b, dTop, dLeft) {
  var bOffset = b.offset();
  if (bOffset != null) {
    a.offset({'top' : bOffset.top + dTop, 'left' : bOffset.left + dLeft});
  }
}

var takeActions = function(step) {

  // Get the next action to execute
  if (step < pagesLog.length) {
    var a = pagesLog[step];
    //console.warn(a.operation);
  } else {
    $(".tooltip").hide();
    return null;
  }

  // Are we in the new part of the log which should be animated?
  var animate = (a.show && step >= logStart);

  // Update IO counter
  $("#chart-" + chartNum + "-bufferReads").html(a.ioCount.bufferReads);
  $("#chart-" + chartNum + "-bufferWrites").html(a.ioCount.bufferWrites);
  $("#chart-" + chartNum + "-diskReads").html(a.ioCount.diskReads);
  $("#chart-" + chartNum + "-diskWrites").html(a.ioCount.diskWrites);

  // Show tooltip!  -> @ old location, or new if old is null
  if (animate) {
    var tooltip = $("#chart-" + chartNum + "-tooltip");
    var pageId = "#" + chartNum + "-" + a.file + "-" + a.page + "-";
    pageId += (a.oldLocation != null) ? a.oldLocation : a.newLocation;
    placeRelativeTo(tooltip, $(pageId), 0.7*pageHeight, 0.3*pageWidth);
    tooltip.html(a.operation);
    tooltip.show();
  }

  // Check for tooltip animations & handle here
  if (a.operation.slice(0, 7) == 'TOOLTIP') {
    // TODO: Clean this up
    if (a.operation == 'TOOLTIP-2') {
      var tooltip = $("#chart-" + chartNum + "-tooltip-2");
      var page = $("#" + chartNum + "-" + a.file + "-" + a.page + "-" + a.oldLocation);
      placeRelativeTo(tooltip, page, -(tooltip.outerHeight() + 1.5*pagePadding), 0.1*pageWidth);
      tooltip.html(a.tooltipContent);
      tooltip.show();
    }
    takeActions(step + 1);
    return true;
  }

  // Check for file actions & handle here
  if (a.operation === "NEWFILE") {
    addFile(a.file, DURATION, function() { takeActions(step + 1); });
    return true;
  } else if (a.operation === "DELETEFILE") {
    removeFile(a.file);
    takeActions(step + 1);  // TODO: Do proper animation here
    return true;
  }

  // old -> new location animation
  if (a.newLocation != null) {

    // Delete the old element
    if (!a.keepOld && a.oldLocation != null) {
      $("#" + chartNum + '-' + a.file + '-' + a.page + '-' + a.oldLocation).remove();
    }

    // ANIMATION: If animation is called for, we create a new copy of page *which is above all 
    // other SVG g layers* to do the animation, then delete it once the animation is done
    // The point is to do the animation so nice & visible (not hidden behind g layers)
    // But so that the end object is appended to the proper g
    var newE = (a.newLocation === "BUFFER") ? buffer : files[a.file];
    var newI = (a.newLocation === "BUFFER") ? a.bufferIndex : a.page;
    var newX = (newI + 1) * frameWidth + pagePadding;
    var newY = 2 * pagePadding;

    // Animate only if we are in the new part of the log
    if (animate) {
      var newPos = (a.newLocation === "BUFFER") ? getBufferPageAbsPos(a.bufferIndex) : getFilePageAbsPos(a.file, a.page);
      if (a.oldLocation != null) {
        var oldPos = (a.oldLocation === "BUFFER") ? getBufferPageAbsPos(a.bufferIndex) : getFilePageAbsPos(a.file, a.page);
        var oldE = (a.oldLocation === "BUFFER") ? buffer : files[a.file];
      } else {
        var oldPos = newPos;
        var oldE = (a.newLocation === "BUFFER") ? buffer : files[a.file];
      }

      // Append the dummpy page for animation
      var p = appendPageTo(svg, a, oldPos[0], oldPos[1], 0, pageColor);

      // Animation! Place the new page and proceed to next action at end
      p.transition()
       .style('opacity', 1).duration(DURATION)
       .transition()
       .attr('transform', 'translate(' + newPos[0] + ',' + newPos[1] + ')').duration(DURATION)
       .each("end", function() { 
         var page = appendPageTo(newE, a, newX, newY, 1, pageColor);
         takeActions(step + 1);
         p.remove();
       });

    // Else if no animation we just place the new element and proceed
    } else {
      var page = appendPageTo(newE, a, newX, newY, 1, pageColor);
      takeActions(step + 1);
    }

  // If no new location: simple fade out animation
  } else {
    if (!a.keepOld && a.oldLocation != null) {
      var page = $("#" + chartNum + '-' + a.file + '-' + a.page + '-' + a.oldLocation);
      if (animate) {
        page.fadeOut(DURATION, function() {
          page.remove();
          takeActions(step + 1);
        });
      } else {
        page.remove();
        takeActions(step + 1);
      }
    } else {
      takeActions(step + 1);
    }
  }
  return true;
}
