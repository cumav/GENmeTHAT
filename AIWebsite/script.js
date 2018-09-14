//alert("Muh")

var languages = [];
var selectedLang = "None";

function getLang() {
	$.get('http://localhost:8000/api/languages/', function(data){
	    console.log(data);
	    for (var i = 0; i < data.length; i++) {
	        console.log(data[i]);
	        languages.push({
            "description":   "kinda " + data[i],
            "data-value":  data[i]
        });
        }
        console.log(languages);
	    createDropdown();
	})

	}

function createDropdown() {
    $('.ui.dropdown').dropdown({
        fields: {name: "description", value: "data-value"},
        apiSettings: {
            mockResponse: {
                success: true,
                results: languages
            }
        },
        onChange: (val) =>  {selectedLang = val}
    });
}
getLang();

$('.ui.button').click(() => {
    if (selectedLang === "None"){
        $('.ui.basic.modal')
          .modal('show');
    } else {
        $.get('http://localhost:8000/api/generate/?lang=' + selectedLang, function (data) {
            console.log(data["name"]);
            console.log(data["language"]);
            document.getElementById("result").innerHTML = data["name"];

        })
    }
});