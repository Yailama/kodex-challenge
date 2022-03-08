/*jshint esversion: 6 */
document.addEventListener("DOMContentLoaded", function() {

    //$('#var_table').DataTable();
    // Track follow-unfollow status once user page opened
    const button = document.querySelector("#get_analysis")
    button.addEventListener('click', () => {
        let repo_url = document.querySelector("#repo_url").value
        console.log(repo_url)
        get_analysis(repo_url)
    })
});

function get_analysis(repo_url) {
    loading(true)
    fetch(`api/?repo_url=${repo_url}`, {
            method: "GET"
        })
        .then(
        function(response) {
          if (response.status !== 200) {
            alert("Invalid URL. Expected github repo url")
            return;
          }

          response.json().then(function(data) {
            console.log(data);
            const holder = document.querySelector("#var_table");
            display_data(holder, data);
            $('#var_table').DataTable();
            loading(false)
          });
        }
      )
      .catch(function(err) {
        console.log('Fetch Error :-S', err);
      });
      }


function display_data(table, data){
    let tbody = table.getElementsByTagName('tbody')[0];
    count = 0;
    for (var file in data){
        for (var model in data[file]){

          let row = tbody.insertRow(count);
          let filename = row.insertCell(0);
          let risk_group = row.insertCell(1);
          let model_name = row.insertCell(2);
          let total = row.insertCell(3);
          let relu = row.insertCell(4);
          let sigmoid = row.insertCell(5);
          let occurrences = row.insertCell(6);

          filename.innerHTML = file
          risk_group.innerHTML = data[file][model]["risk"]
          model_name.innerHTML = model
          total.innerHTML = data[file][model]["total"]

          if (data[file][model].hasOwnProperty('relu')){
            relu.innerHTML = data[file][model]["relu"]["count"]
            if (data[file][model]["relu"]["count"] > 0){
                occurrences.innerHTML = "relu: " + data[file][model]["relu"]["lines"]
            }
          }

          if (data[file][model].hasOwnProperty('sigmoid')){
            sigmoid.innerHTML = data[file][model]["sigmoid"]["count"]
            if (data[file][model]["sigmoid"]["count"] > 0){
                occurrences.innerHTML = occurrences.innerHTML + " sigmoid: " + data[file][model]["sigmoid"]["lines"]
            }
          }

          count++;
        }
    }
}


function loading(is_loading){

    const sheet = document.querySelector("#sheet")
    const holder = document.querySelector("#resultHolder")

    if(is_loading){
        sheet.style.display = "block";
        holder.style.display = "none";
    } else {
        sheet.style.display = "none";
        holder.style.display = "block";
    }
}