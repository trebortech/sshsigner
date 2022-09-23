

window.onload = function () {


    localYubiHSM();
}


async function postData(route, postdata) {

    var results = "";
    let callAPI = await $.ajax({
        contentType: 'application/json; charset=utf-8',
        url: route,
        type: 'POST',
        data: JSON.stringify(postdata),
        success: function (result) {
            result = result.replace(/'/g, '"');
            result = result.replace(/None/g, '""');
            //console.log(result);
            results = JSON.parse(result);
        },
        'error': function (request, error) {
            console.log(request)
            console.log(error)
            //alert("Error:" + error);
        }
    });

    return results;

};



async function localYubiHSM() {
    var postdata = {};
    postdata["method"] = "get_yubihsm_list";
    var results = await postData("/v1/data", postdata)

    select_hsm = document.getElementById('select_hsm');
    select_hsm.innerHTML = ""

    // Set default selections
    var hsmoption = document.createElement("option");
    hsmoption.text = "Select YubiHSM";
    hsmoption.value = "0";
    hsmoption.selected = true;
    select_hsm.add(hsmoption);

    for (var hsm in results) {
        var option = document.createElement("option");
        option.text = hsm;
        option.value = results[hsm]
        select_hsm.add(option);
    };


}

async function getTemplates() {
    var postdata = {};
    postdata["method"] = "get_ssh_templates";
    postdata["hsmport"] = document.getElementById("select_hsm").value;
    postdata["userid"] = document.getElementById("text-loginname").value;
    postdata["usercode"] = document.getElementById("passphrase").value;

    var results = await postData("/v1/data", postdata)

    select_template = document.getElementById('select-template');
    select_template.innerHTML = ""

    // Set default selections
    var templateoption = document.createElement("option");
    templateoption.text = "Select Template";
    templateoption.value = "0";
    templateoption.selected = true;
    select_template.add(templateoption);

    for (var template in results) {
        var option = document.createElement("option");
        option.text = results[template];
        option.value = template + "-" + results[template];
        select_template.add(option);
    };

}


async function signRequest() {
    var postdata = {};

    postdata["hsmport"] = document.getElementById("select_hsm").value;
    postdata["userid"] = document.getElementById("text-loginname").value;
    postdata["usercode"] = document.getElementById("passphrase").value;

    postdata["templateid"] = document.getElementById("select-template").value
    postdata["principals"] = document.getElementById("text-sshname").value
    postdata["sshkey"] = document.getElementById("text-sshpk").value

    var results = await postData("/v1/data", postdata)
}