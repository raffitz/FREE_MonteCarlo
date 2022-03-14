/* Javascript used to start an experiment and showns graphics in real time

Developed by José Veiga and Pedro Rosa

Last updated out 9 11:12 , 2021*/


// starting all the variables
var base_url = "http://10.2.12.86:8000";
let new_execution = JSON.parse(document.getElementById('execution-config').textContent);
result_data = JSON.parse(document.getElementById('final-result').textContent);
var apparatus = new_execution.apparatus;
var protocol = new_execution.protocol.id;
// {
//   "apparatus": 0,
//   "protocol": 0,
//   "config": {}
// }

let execution_id = 0;
let Results=0;
var DeltaX=0;
var Samples=0;
var point_x;
var point_y;
var name = ''
var frist=0;
var point_x;
var point_y;
var output_data = [];
var receive_error_velocity = [];
var receive_error_period = [];
var mytable = [];
var DeltaX = document.getElementById('DeltaX');
var Samples = document.getElementById('Samples');
let save_table = ""

function getCookie(name) 
{
  var dc = document.cookie;
  var prefix = name + "=";
  var begin = dc.indexOf("; " + prefix);
  if (begin == -1) 
  {
    begin = dc.indexOf(prefix);
    if (begin != 0) return null;
  }
  else
  {
    begin += 2;
    var end = document.cookie.indexOf(";", begin);
    if (end == -1) 
    {
      end = dc.length;
    }
  }
  
  // because unescape has been deprecated, replaced with decodeURI
  // return unescape(dc.substring(begin + prefix.length, end));
  return decodeURI(dc.substring(begin + prefix.length, end));
}

$(".menu .item").click(function() {
  var tab_description = $(this).attr("data-tab");
  // console.log('Description : ', tab_description);
  if (tab_description === 'results')
  {
    Show_data()
  }
  });

function Show_data(){
  result_data = JSON.parse(document.getElementById('final-result').textContent);
  buildPlot1(0);
  buildPlot2(0);
  buildPlot3(0);
  receive_error_velocity = 0.1;
  receive_error_period = 0.0005;//response.data.value.e_period;
  Plotly.extendTraces('myplot', {x: [result_data.value.map(data => data.Sample_number)],y: [result_data.value.map(data => data.Val3)],'error_y.array': [Array(result_data.value.length).fill(receive_error_velocity)]}, [0]);
  Plotly.extendTraces('myplot1', {x:  [result_data.value.map(data => data.Val1)]}, [0]);
  Plotly.extendTraces('myplot2', {x: [result_data.value.map(data => data.Sample_number)],y: [result_data.value.map(data => data.Val1)],'error_y.array': [Array(result_data.value.length).fill(receive_error_period)]}, [0]);


}


// This function receive as input the parameters and send them to the experiment and send back the data to browser*/

function queue() {
  // get inputs values from the client side
  if ($("#R").val() !== undefined)
    DeltaX = $("#R").val();
  if ($("#Iteration").val() !== undefined)
    Samples = $("#Iteration").val();

  
  data_send = {"id":new_execution.id,"apparatus": apparatus, "protocol": protocol, "config": {"R": parseInt (DeltaX), "Iteration":parseInt (Samples)}}
  // '{"experiment_name": "Pendulo", "config_experiment": {"DeltaX":'+ String(DeltaX)+', "Samples":'+String(Samples)+' }}'
  HEADERS = {
    "X-CSRFToken": getCookie("csrftoken"),
    }
  var endpoint="/api/v1/execution/"+new_execution.id;
  // print out
  console.log('JSON : ' +  endpoint);
  console.log('JSON : ' +  data_send);

  // $.ajax({
  //   url: endpoint,   //Your api url
  //   type: 'POST',   //type is any HTTP method
  //   contentType: 'application/json;charset=UTF-8',
  //   data: JSON,
  //   success: function (response){
  //   console.log('PUT response in:' +response.id);
  //   execution_id = response.id
  //   }
  // });

  axios({
    method: 'put', //you can set what request you want to be
    url: endpoint,
    headers: HEADERS,
    data: data_send,
  }).then(response => {
    console.log('plotly_results', response);
    execution_id = new_execution.id
  }).catch(console);


  // não quero fazer pontos no botão start!
  // Tenho que mudar alguma coisa aqui pois ainda não faz o que realmente quero
  // getData(); 
  


}


function myStopFunction() {
  clearInterval(Results);
  console.log(Results);
}

let last_result_id =0 
// Receive data from experiment
function getData(){
  let endpoint_result =  "/api/v1/execution/"+execution_id+"/result/0";
  if (frist === 0)
  {
    endpoint_result = "/api/v1/execution/"+execution_id+"/result/0";
  }
  else{
    endpoint_result = "/api/v1/execution/"+execution_id+"/result/"+last_result_id
  }

  axios({
    method: 'get', //you can set what request you want to be
    url: endpoint_result,
    headers: HEADERS,
  }).then(response => {
    console.log('plotly_results', response.data);
    if (frist === 0)
    {
      if (response.data !== "")
      {
        console.log('ola', response.data[0].value);
        res = Object.keys(response.data[0].value);
        buildPlot1(res);
        last_result_id = response.data[0].id+1
        frist = 1;
      }
    }
    console.log(response);
    // check for ending of the experiment
    if (response.data.result_type !== 'undefined' && response.data[0].result_type === 'f'){
        myStopFunction();
    }
    else{
      if (typeof response.data[0] === 'object'){
        let j = parseInt(response.data.value.circ,10);
				Plotly.extendTraces('myplot', {x: [[response.data.value.eX]],y: [[response.data.value.eY]]}, [j]);
            last_result_id = parseInt(response.data.id)+1
				if (j === 1)
				{
					point_in_1 = point_in_1+1;
					document.getElementById('point_in').innerHTML = 'Points in : ' + parseInt(point_in_1,10);
				}
				total_point_1 = total_point_1 +1
				document.getElementById('total_point').innerHTML = 'Total points : ' +  parseInt(total_point_1,10);
				document.getElementById('pi').innerHTML = 'PI : ' + (4*parseFloat(point_in_1,10)/parseFloat(total_point_1,10));
      }
      // getData();
    }
   
  }).catch(error => {
    if (error.response !== undefined) {
    console.error('Error : ', error.response.data);
    }
  });
  
}

function myStartFunction() {
  Results = setInterval(getData,500)
  console.log("Valor da função");
  console.log(Results);
}


function start() {
  var endpoint_2="/api/v1/execution/"+execution_id+"/start";
  // print out
  console.log('JSON : ' +  endpoint_2);
  // console.log('JSON : ' +  JSON);
  // data_send = {}
  // $.ajax({
  //   url: endpoint_2,   //Your api url
  //   type: 'PUT',   //type is any HTTP method
  //   contentType: 'application/json;charset=UTF-8',
  //   data: JSON,
  //   success: function (response){
  //   console.log('PUT response in:' +response);
  //   }
  // });

  axios({
    method: 'put', //you can set what request you want to be
    url: endpoint_2,
    headers: HEADERS,
  }).then(response => {
    console.log('plotly_results', response);
  }).catch(error => {
    if (error.response !== undefined) {
    console.error('Error : ', error.response.data);
    }
  });
  
  $('.menu .item').tab('change tab','execution');
  myStartFunction();
}





//// nao usado
function tablebind(response) {  
          if (obj.length > 0) {  

              var table = $("<table />");  
              table[0].border = "1";  

              var row$;  

              var columns = addAllColumnHeaders(["S"]);  
              for (var i = 0; i < data.length; i++)
               {  
                  row$ = $('<tr/>');  
           
                  for (var colIndex = 0; colIndex < columns.length; colIndex++) 
                  {  
                      var cellValue = data[i][columns[colIndex]];  

                      if (cellValue == null) { cellValue = ""; }  

                      row$.append($('<td/>').html(cellValue));  
                  }  
                  $("#jsonTable").append(row$);  
              }      
          }  

}  




var point_x;
var point_y;
/////////////////////////////////////////////////////////////////////////////////
//////////// Build graphic                    
/////////////////////////////////////////////////////////////////////////////////


// To improve
var selectorOptions = {
  buttons: [{
      step: '1',
      stepmode: 'backward',
      count: 1,
      label: '10N'
  },{

      step: 'all',

  }],

};


function buildPlot1(results) {

  var dados_f = [];
           //color = "rgb(" + (200*Math.random()+50).toString()+',' + (200*Math.random()+20).toString()+',' +(200*Math.random()+10).toString()+')';
           for (let i=0; i < 2; i++){
              if (i === 1){
                 name= "IN";
                 color = "rgb(0, 204, 0)";
              }
              else{
                 name = "OUT";
                 color = "rgb(255, 0, 0)";
              }
              dados_f.push({
                      name: name,
                      x: [],
                      y: [],
                      marker: {
                       color: color,
                       size: 5,
                      },
                      line: {
                       color: color,
                       width: 0,
                      },
                      mode: 'lines+markers',
                      type: 'scatter',
                    });
           }
           var layout = {
              title: 'Monte Carlo',
              width: 550,
              height: 550,
              xaxis: {
                 title: 'R [ua]',
                 titlefont: {
                   family: 'Arial, sans-serif',
                   size: 18,
                   color: 'black'
                 },
                 showticklabels: true,
                 exponentformat: 'e',
                 showexponent: 'all',
                 range: [-R, R]
              },
              yaxis: {
                 title: 'R [ua]',
                 titlefont: {
                   family: 'Arial, sans-serif',
                   size: 18,
                   color: 'black'
                 },
                 showticklabels: true,
                   range: [-R, R]
                 
              },
              shapes: [
  
                 // Unfilled Circle
  
                 {
                   type: 'circle',
                   xref: 'x',
                   yref: 'y',
                   x0: -R,
                   y0: -R,
                   x1: R,
                   y1: R,
                   line: {
                    color: "rgb(0, 204, 0)",
                    width: 1
                   }
                 },
                 {
                  type: 'rect',
                  x0: -R,
                  y0: -R,
                  x1: R,
                  y1: R,
                  line: {
                     color: 'rgba(128, 0, 128, 1)'
                  }

                 }
              ],
              
           };
           console.log(dados_f);
           Plotly.newPlot('myplot', dados_f, layout);
   
}





function set_reset() {
  var resetBtn = document.getElementById('delete_conf');
  var location = window.location.href.split('?')[0];
  
    resetBtn.addEventListener('click', function(event) {
    console.log('Reseting values of R or iteration...');
    window.location.href = location;
    });
    }





