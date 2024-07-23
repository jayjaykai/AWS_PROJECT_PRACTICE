async function getData() {
    let url = "/api/msg";
    let response = await fetch(url, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    });
    if (!response.ok) {
        console.error('HTTP error', response.status);
        isLoading = false;
        return;
    }
    let result = await response.json();
    console.log(result);
    if (result.data) {
        for (let i = 0; i < result.data.length; i++) {
            let element = result.data[i];
            
            let text = document.createElement("div");
            text.append(document.createTextNode(element[0]));

            let pic = document.createElement("img");
            pic.src = element[1];
            pic.classList.add("pic-size");

            let line = document.createElement("div");
            line.setAttribute("class", "line");

            let body = document.getElementById("image_container");
            body.append(text);
            body.append(pic);
            body.append(line);
        }
    }
}

async function UploadFile(){
    let url = "/api/msg";
    let image = document.getElementById('myFile').files[0];
    let msg = document.getElementsByName("msg")[0].value;

    let formData =new FormData();
    formData.append('file',image);
    formData.append('content',msg);
    // for (let pair of formData.entries()) {
    //     console.log(pair[0] + ': ' + pair[1]);
    // }

    let response = await fetch(url, {
        method: 'POST',
        body: formData
    });

    let result = await response.json();
    if(!response.ok){
        console.error('HTTP error', response.status);
        alert(result.message);
        return;
    }
    else{
        alert(result.message);
        let text = document.createElement("div");
        text.append(document.createTextNode(msg));

        let pic = document.createElement("img");
        pic.src = URL.createObjectURL(image);
        pic.classList.add("pic-size");

        let line = document.createElement("div");
        line.setAttribute("class", "line");

        let body = document.getElementById("image_container");

        body.insertBefore(line, body.firstChild);
        body.insertBefore(pic, body.firstChild);
        body.insertBefore(text, body.firstChild);

        document.getElementById('myFile').value = "";
        document.getElementsByName("msg")[0].value = "";
    }
}

getData();