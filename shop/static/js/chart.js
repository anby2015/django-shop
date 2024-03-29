var chart;
var barChart, useGradients, labelType, nativeTextSupport, animate;

(function() {
  var ua = navigator.userAgent,
      iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
      typeOfCanvas = typeof HTMLCanvasElement,
      nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
      textSupport = nativeCanvasSupport
        && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
  //I'm setting this based on the fact that ExCanvas provides text support for IE
  //and that as of today iPhone/iPad current text support is lame
  labelType = (!nativeCanvasSupport || (textSupport && !iStuff))? 'Native' : 'HTML';
  nativeTextSupport = labelType == 'Native';
  useGradients = nativeCanvasSupport;
  animate = !(iStuff || !nativeCanvasSupport);
})();

$(document).ready(function() {
   var series = [];
   for(var i = 0; i < paramsy.length; i++){
      series.push({
         'label': paramsy[i],
         'values': map[i]
      });
   }
   var json = {
      'label': paramsx,
      'values': series
   };
   barChart = new $jit.BarChart({
      //id of the visualization container
      injectInto: 'chart',
      //whether to add animations
      animate: true,
      //horizontal or vertical barcharts
      orientation: 'vertical',
      //bars separation
      barsOffset: 20,
      //visualization offset
      Margin: {
        top:5,
        left: 5,
        right: 5,
        bottom:5
      },
      //labels offset position
      labelOffset: 5,
      //bars style
      type: useGradients? 'grouped:gradient' : 'grouped',
      //whether to show the aggregation of the values
      showAggregates:function(paramy, value){
        return Math.round(value * 100) / 100
      },
      //whether to show the labels for the bars
      showLabels:true,
      //labels style
      Label: {
        type: labelType, //Native or HTML
        size: 13,
        family: 'Arial',
        color: 'black'
      },
      //add tooltips
      Tips: {
        enable: true,
        onShow: function(tip, elem) {
          tip.innerHTML = '<span class = "bar-tip">' +
            "<strong>" + elem.name + "</strong>: " + elem.value +
        '</span>';
        }
      }
    });
    //load JSON data.
    barChart.loadJSON(json);
    
    var list = $jit.id('id-list');
    //dynamically add legend to list
    var legend = barChart.getLegend(),
        listItems = [];
    for(var name in legend) {
      listItems.push('<div class=\'bar-query-color\' style=\'background-color:'
          + legend[name] +'\'>&nbsp;</div>' + name);
    }
    list.innerHTML = '<li>' + listItems.join('</li><li>') + '</li>';
});