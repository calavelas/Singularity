const myForm = document.getElementById('postForm');

myForm.addEventListener('submit', function (e){
    e.preventDefault()

    const formData = {
        "clientId" : document.getElementById('clientId').value,
        "clientSecret" : document.getElementById('clientSecret').value,
        "siteUrl" : document.getElementById('siteUrl').value,
        "purposeCSV" : JSON.parse(document.getElementById('purposeCSV').value)
    }

    formBody = JSON.stringify(formData)
    console.log(formBody)

    const requestOptions = {
        method: 'POST',
        body: formBody,
        redirect: 'follow'
      };

    console.log(requestOptions)

    fetch("http://singularity-backend:8000/api/", requestOptions)
    .then(response => response.json())
    .then(result => {
        console.log(result)
        if (result[0]['Status'] === 'OK'){
            alert('Upload Success, Check Console Log for more information')
        }
        else{
            alert('Upload Failed, Check Console Log for more information')
        }

    })
    .catch(error => console.log('error', error));
})