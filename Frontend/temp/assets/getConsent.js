function getConsent(){
    fetch('placeholder.json')
    .then((res) => res.json())
    .then((data) => {
      const placeholder = JSON.stringify(data,undefined,2)
      document.getElementById('purposeCSV').placeholder = placeholder;
    })
  }
  getConsent()