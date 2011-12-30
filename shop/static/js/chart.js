var chart;
$(document).ready(function() {
   var series = []
   for(var i = 0; i < paramsy.length; i++){
      series.push({
         'name': paramsy[i],
         'data': map[i]
      });
   }
   chart = new Highcharts.Chart({
      chart: {
         renderTo: 'chart',
         defaultSeriesType: 'column'
      },
      title: {
         text: ''
      },
      subtitle: {
         text: ''
      },
      xAxis: {
         categories: paramsx
      },
      yAxis: {
         min: 0,
         title: {
            text: 'Sum'
         }
      },
      legend: {
         layout: 'vertical',
         //backgroundColor: Highcharts.theme.legendBackgroundColor || '#FFFFFF',
         align: 'right',
         verticalAlign: 'top',
         x: 10,
         y: 70,
         //floating: true,
         shadow: true
      },
      tooltip: {
         formatter: function() {
            return ''+
               this.x +': '+ this.y +' €';
         }
      },
      plotOptions: {
         column: {
            pointPadding: 0.2,
            borderWidth: 0
         }
      },
           series: series
   });
   
   
});
