document.addEventListener('DOMContentLoaded',() => {
    
    // Do whatever you want
    getData('experiments/experiment/stat', 'POST', 'slug', EXPE_SLUG)
        .then(response => response.json())
        .then(data => {

            const session_labels = []
            const session_data = []
            const class_list = [ "primary", "success", "info" ]
            
            div_stat = document.querySelector('div[name="experiment-stat-names"]')
            
            var count_sum = 0;
            Object.keys(data).forEach(key => {
                count_sum += data[key]['count']
            });

            if (count_sum == 0) {
                var div_chart = document.querySelector(".chart-pie");
                console.log(div_chart)
                div_chart.innerHTML = "No session information"
            }
            else 
            {
                Object.keys(data).forEach(key => {

                    let index = Object.keys(data).indexOf(key);
    
                    session_labels.push(key);
                    session_data.push(data[key]['count']);
    
                    var span = document.createElement("span");  
                    span.className = "mr-2"
                    span.innerHTML = `<i class="fas fa-circle text-${class_list[index]}"></i> ${key}`
                    
                    div_stat.appendChild(span);  
                });
           
                // Set new default font family and font color to mimic Bootstrap's default styling
                Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
                Chart.defaults.global.defaultFontColor = '#858796';
    
                // Pie Chart Example
                var ctx = document.getElementById("experiment-stat");
                var myPieChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: session_labels,
                        datasets: [{
                            data: session_data,
                            backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc'],
                            hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf'],
                            hoverBorderColor: "rgba(234, 236, 244, 1)",
                        }],
                    },
                    options: {
                        maintainAspectRatio: false,
                        tooltips: {
                            backgroundColor: "rgb(255,255,255)",
                            bodyFontColor: "#858796",
                            borderColor: '#dddfeb',
                            borderWidth: 1,
                            xPadding: 5,
                            yPadding: 5,
                            displayColors: false,
                            caretPadding: 10,
                        },
                        legend: {
                            display: false
                        },
                        cutoutPercentage: 80,
                    },
                });
            }
        });
});
