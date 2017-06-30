var cpubar;

function BarChart(options) {

    var parentThis = this;
    
    this.data = [
        {
            type: "stackedColumn",
            name: "",
            showInLegend: false,            
            dataPoints: []
        }
    ];
    this.chart = new CanvasJS.Chart(options.container, {
        title: {
            text: options.title
        },
        axisX: {   
            
        },
        axisY: {
            title: options.ytitle,
            minimum: 0,
            maximum: 100
        },
        axisY2: {
            title: options.y2title,
                
        },
        dataPointWidth: options.dataPointWidth,
        dataPointMaxWidth: options.dataPointMaxWidth,
        data: this.data
    });

    this.add_datapoint = function (data, render)
    {
        render = render || true;
        this.data.push( data );
        if(render)
            this.chart.render();
    };
    
    this.clear = function(){
        var l = this.data.length;
        for(var i = 0; i < l; i++){
            var a = this.data.splice(0,1);
            console.log("Removing",i,a);
        }  
        this.data.push({
            type: "stackedColumn",
            name: "",
            showInLegend: false,            
            dataPoints: []
        });
    };

    setTimeout(this.chart.render, 300);
    console.log("CPU BarChart initialized!");

};
$(function() {
    
    var options = {
        container: "cpuBar",
        title: "CPU share",
        ytitle: "CPU in %",        
        dataPointMaxWidth: 100
    };
    cpubar = new BarChart(options);    
    
    // Add function for adding vsdn_data to the barchart
    cpubar.add_vsdn = function(vsdn_data) {
        var cpu_usage = vsdn_data.vsdn.allocated_cpu;
        var message_rate = vsdn_data.vsdn.message_rate;
        var bitrate = vsdn_data.vsdn.bitrate;
        
        var data = {
                    type: "stackedColumn",
                    name: vsdn_data.vsdn.name,
                    showInLegend: false,
                    color: "#"+vsdn_data.vsdn.color,
                    toolTipContent: "<b>CPU:</b> {y} % <br /> <b>Msg Rate:</b> {message_rate} <br /> <b>Bitrate:</b> {bitrate} ",
                    dataPoints: [
                        {
                            y: cpu_usage, 
                            label: "CPU",
                            cpu_usage: cpu_usage,
                            message_rate: message_rate,
                            bitrate: bitrate
                        }

                    ]
                };
        this.add_datapoint(data,true);
    };
    
    cpubar.chart.render();
});

