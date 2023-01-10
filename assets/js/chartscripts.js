$(document).ready(function(){
    const ctx = $("#ChartTotalRecords");

    if(ctx.length > 0){
        // alert('found')
        let ChartTotalRecords = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['ACM Digital Library', 'IEEE Explore', 'Springer Link'],
                datasets: [{
                    label:'',
                    data: [0, 0, 0, 0, 0, 0],
                    borderWidth: 1
                }]
            },
            options: {
                plugins: {
                    legend: false // Hide legend
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                // legend: {
                //     display: false,
                //     labels: {
                //         fontSize: 0
                //     }
                // }
            }
        });

        function loadDataChartTotalRecords(){
            let _url = "./../administrator/load-total-records-chart";
            $.get(_url,function(data){
                ChartTotalRecords.data.datasets[0].data = [data.data.acm, data.data.ieee, data.data.spring];
                ChartTotalRecords.update();
            });

        }

        $(document).on("click","#loadDataChartTotalRecords",function(){
            loadDataChartTotalRecords()
        })

        loadDataChartTotalRecords()
    }

});