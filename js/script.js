function setValues() {
	input = document.getElementById("input").value;

	output = document.createElement('div');
	output.style.cssText = "background-color:#ffffff;width:75%;height:auto;";

	outputText = document.createElement('p');
	text = document.createTextNode(input);
	outputText.appendChild(text);
	output.appendChild(outputText);

}

function run() {
	setValues();


	$.ajax({
		type: "test",
		url: "/autogloss.py",
		crossOrigin: null,
		data: { param: input },
		success: updateScreen
	})



}

function updateScreen() {
	document.body.appendChild(output);
}
